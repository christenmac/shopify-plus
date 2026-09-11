#!/usr/bin/env python3
"""ckdetect.py — detect CHECKOUT-LEVEL UI extensions, not storefront apps.

    python3 ckdetect.py permalinks.txt   # "domain variant_id" or a full permalink per line

Why this exists: detect.py greps the *storefront* for app fingerprints (Judge.me,
Rebuy, Loox, Gift Wrap). Those almost always render on the product or cart page and
prove nothing about the checkout. This script instead walks a cart permalink into a
live /checkouts/cn/ session and reads the checkout document, where Shopify
serialises every installed checkout UI extension as an object like:

    {"appName":"Vincero App","extensionPoints":["purchase.checkout.header.render-after"],
     "name":"trust-icons-ui", ...}

Presence of a checkout extension point is hard evidence the merchant customised
the checkout itself, which is the Plus-gated surface.

⚠️ THERE ARE TWO TARGET SYNTAXES AND YOU MUST MATCH BOTH.
  new dotted  purchase.checkout.header.render-after
  legacy      Checkout::Reductions::RenderAfter, Checkout::Dynamic::Render,
              Checkout::Contact::RenderAfter, Checkout::CartLineDetails::RenderAfter,
              Checkout::Actions::RenderBefore, Checkout::DeliveryAddress::RenderBefore
Matching only the dotted form under-reports badly — Vincero serialises 18 extension
objects and just 4 of them use dotted targets, so a dotted-only regex reported 2 of
24 stores as customised when the true number is far higher.

⚠️ THE VARIANT MUST BE PURCHASABLE, OR EVERY STORE LOOKS BARE. An empty checkout
serialises NO extensions, and a sold-out/stale variant id adds nothing to the cart —
yet hop 2 still opens a checkout shell, so in_checkout is True and the store is
scored "stock checkout". A first pass over 24 watch brands with stale variant ids
reported 2 customised; re-resolving live `available` variants with ckvariant.py
turned the same 24 into 19. Always feed this script ckvariant.py output, never
hand-typed or cached ids.

⚠️ NOT EVERY TARGET IS PLUS-GATED. Anything containing ThankYou / OrderStatus /
thank-you / order-status renders on the post-purchase pages, which are available on
every plan except Starter, and `customer-account.*` is the customer-account surface.
Those are collected separately and must never be cited as evidence of Plus.
"""
import concurrent.futures as cf
import html
import json
import os
import re
import subprocess
import sys
import tempfile

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

# either syntax; classified into checkout vs post-purchase afterwards
TARGET_ANY = re.compile(
    r'purchase\.checkout\.[a-z0-9.\-]+?\.render(?:-(?:before|after))?'
    r'|purchase\.thank-you\.[a-z0-9.\-]+?\.render(?:-(?:before|after))?'
    r'|customer-account\.[a-z0-9.\-]+'
    r'|Checkout(?:::[A-Za-z0-9]+)+::Render(?:Before|After)?')
POST_MARK = re.compile(r'thank-?you|order-?status|customer-account', re.I)

APP_RE = re.compile(r'"appName"\s*:\s*"([^"]{2,60})"')
EXTPOINTS_RE = re.compile(r'"extensionPoints"\s*:\s*(\[[^\]]{0,4000}\])')
NAME_RE = re.compile(r'"name"\s*:\s*"([A-Za-z0-9][A-Za-z0-9\-_ ]{1,48})"')
SCOPE_RE = re.compile(r'^(read|write)_')

# handle/app vocabulary -> the merchandising element it implements
ELEMENT_SIGNS = [
    ('trust badges',       r'trust[-_ ]?(icon|badge|seal)|secur(e|ity)[-_ ]?(badge|icon)|guarantee|benefit'),
    ('reviews',            r'review|testimonial|judge|loox|okendo|stamped|yotpo|star[-_ ]?rating|social[-_ ]?proof'),
    ('free-ship bar',      r'free[-_ ]?ship|shipping[-_ ]?(bar|progress|threshold)|spend[-_ ]?more|unlock'),
    ('ship/return policy', r'polic|return|refund|exchange|terms|condition|shipping[-_ ]?info|delivery[-_ ]?info|faq'),
    ('add-ons / upsell',   r'rebuy|upsell|cross[-_ ]?sell|recommend|addon|add[-_ ]?on|offer|personaliz|smart'),
    ('gift options',       r'gift|wrap|greeting|note|message'),
    ('bundling',           r'bundle|\bkit\b|combo'),
    ('loyalty / rewards',  r'loyalt|reward|point|referr|smile|growave|\bvip\b|member'),
    ('custom fields',      r'custom[-_ ]?field|additional[-_ ]?(field|information)|instruction|order[-_ ]?note|delivery[-_ ]?date|line[-_ ]?item[-_ ]?edit'),
    ('duties / tax msg',   r'\bdut(y|ies)\b|\btax|\bvat\b|landed[-_ ]?cost'),
    ('address validation', r'address[-_ ]?valid|address[-_ ]?check|verif'),
    ('discount messaging', r'discount|promo|reduction|coupon'),
    ('payment options',    r'payment[-_ ]?method|alternative[-_ ]?payment|instal|financ|bnpl'),
    ('subscription',       r'subscri|recharge|skio|stay[-_ ]?ai'),
    ('pickup / local',     r'pickup|pick[-_ ]?up|local[-_ ]?deliver|store[-_ ]?locator'),
    ('age / ID check',     r'\bage\b|\bid[-_ ]?check'),
    ('B2B / net terms',    r'b2b|wholesal|net[-_ ]?terms|purchase[-_ ]?order|tax[-_ ]?exempt'),
]


def _get(jar, url, timeout):
    out = subprocess.run(
        ['curl', '-sS', '-L', '--max-redirs', '12', '--compressed',
         '--max-time', str(timeout), '-c', jar, '-b', jar,
         '-A', UA, '-H', 'Accept-Language: en-US,en;q=0.9',
         '-w', '\n===URL===%{url_effective}', url],
        capture_output=True, text=True, errors='replace')
    body, final = out.stdout, ''
    if '\n===URL===' in body:
        body, final = body.rsplit('\n===URL===', 1)
    return final.strip(), body


def walk_to_checkout(permalink, timeout=45):
    """Follow a cart permalink into a live checkout session. Returns (final_url, html).

    TWO HOPS, and both are required. The permalink alone only reaches checkout on
    stores whose theme lets Shopify server-redirect (~2 in 24). Everyone else
    renders the cart page and redirects with JavaScript, which curl will never
    execute — so hop 1 exists purely to put the variant in the cart cookie, and
    hop 2 requests /checkout on that same jar to open the session. Skipping hop 2
    makes 22 of 24 stores look like they have no checkout at all.

    /checkout on an EMPTY cart bounces to the homepage, so hop 1 must succeed
    first; that is also why the cookie jar is shared rather than per-request.
    """
    jar = tempfile.NamedTemporaryFile(prefix='ckjar_', delete=False)
    jar.close()
    try:
        final, body = _get(jar.name, permalink, timeout)
        if '/checkouts/' in final:
            return final, body
        host = re.sub(r'^https?://', '', final or permalink).split('/')[0]
        return _get(jar.name, f'https://{host}/checkout', timeout)
    finally:
        os.unlink(jar.name)


def zone_of(target):
    """Human-readable checkout zone for either target syntax."""
    if target.startswith('purchase.'):
        parts = target.split('.')
        return parts[2] if len(parts) > 2 else target
    seg = [s for s in target.split('::') if s not in ('Checkout',)]
    return seg[0] if seg else target


def classify(tokens):
    blob = ' '.join(tokens).lower()
    return [name for name, pat in ELEMENT_SIGNS if re.search(pat, blob)]


def analyse(entry):
    domain, permalink = entry
    rec = {'domain': domain, 'permalink': permalink, 'checkout_url': '',
           'in_checkout': False, 'extensions': [], 'apps': [], 'handles': [],
           'zones': [], 'elements': [], 'post_purchase_only': [], 'error': ''}
    try:
        final, body = walk_to_checkout(permalink)
    except Exception as exc:                                  # noqa: BLE001
        rec['error'] = f'{type(exc).__name__}: {exc}'
        return rec

    rec['checkout_url'] = final
    rec['in_checkout'] = '/checkouts/' in final
    if not body:
        rec['error'] = 'empty response'
        return rec
    if not rec['in_checkout']:
        rec['error'] = 'never reached a checkout session'
        return rec

    txt = html.unescape(html.unescape(body))
    rec['apps'] = sorted(set(APP_RE.findall(txt)))

    # Parse per extension OBJECT, anchored on "extensionPoints". The extension's own
    # handle is keyed "name", NOT "handle" — a window grep for "handle" returns only
    # read_customer_* access scopes, which is how Vincero's trust icons were missed.
    raw = []
    for m in EXTPOINTS_RE.finditer(txt):
        pts = [p for p in re.findall(r'"([^"]+)"', m.group(1)) if TARGET_ANY.fullmatch(p)]
        if not pts:
            continue
        back = txt[max(0, m.start() - 500):m.start()]
        fwd = txt[m.end():m.end() + 300]
        app = (APP_RE.findall(back) or [''])[-1]
        handle = next((h for h in NAME_RE.findall(fwd) + NAME_RE.findall(back)
                       if not SCOPE_RE.match(h)), '')
        ck = sorted({p for p in pts if not POST_MARK.search(p)})
        post = sorted({p for p in pts if POST_MARK.search(p)})
        raw.append({'app': app, 'handle': handle, 'targets': ck, 'post': post})

    seen, uniq, post_only = set(), [], []
    for e in sorted(raw, key=lambda e: (e['app'], e['handle'])):
        key = (e['app'], e['handle'], tuple(e['targets']), tuple(e['post']))
        if key in seen:
            continue
        seen.add(key)
        if e['targets']:
            uniq.append(e)
        elif e['post']:
            post_only.append(f"{e['app']}/{e['handle']}")

    rec['extensions'] = uniq
    rec['post_purchase_only'] = sorted(set(post_only))
    rec['handles'] = sorted({e['handle'] for e in uniq if e['handle']})
    rec['zones'] = sorted({zone_of(t) for e in uniq for t in e['targets']})
    rec['elements'] = classify(rec['handles'] + [e['app'] for e in uniq])
    return rec


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    entries = []
    for line in open(sys.argv[1], encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) == 2 and not parts[0].startswith('http'):
            entries.append((parts[0], f'https://{parts[0]}/cart/{parts[1]}:1'))
        else:
            url = parts[0] if parts[0].startswith('http') else 'https://' + parts[0]
            entries.append((re.sub(r'^https?://(www\.)?', '', url).split('/')[0], url))

    print(f'walking {len(entries)} permalink(s) into checkout…\n', file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        for rec in pool.map(analyse, entries):
            results.append(rec)
            if rec['error']:
                print(f"  ✖ {rec['domain']:<28} {rec['error']}", file=sys.stderr)
            elif rec['extensions']:
                print(f"  ✔ {rec['domain']:<28} {len(rec['extensions'])} ext / "
                      f"{len(rec['zones'])} zone(s) | "
                      f"{', '.join(rec['elements']) or 'unclassified'}", file=sys.stderr)
            else:
                extra = (f" (post-purchase only: {', '.join(rec['post_purchase_only'])})"
                         if rec['post_purchase_only'] else '')
                print(f"  · {rec['domain']:<28} stock checkout{extra}", file=sys.stderr)

    with open('/tmp/ckdetect_results.json', 'w', encoding='utf-8') as fh:
        json.dump(results, fh, indent=1)
    print('\nwrote /tmp/ckdetect_results.json', file=sys.stderr)


if __name__ == '__main__':
    main()
