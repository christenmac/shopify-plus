#!/usr/bin/env python3
"""build_ck.py — fold ckdetect.py output into library_data.json as the `ck` block.

    python3 build_ck.py /tmp/ck_watches.json /tmp/ck_premium.json …

The library's original evidence comes from detect.py, which reads the STOREFRONT —
it proves a merchant *runs* Judge.me or Rebuy, not that anything is in the checkout.
This block is different and is labelled differently on the page: every row here was
read out of a live /checkouts/cn/… document, so the app, the block handle and the
checkout zone are all known.

Only merchandising blocks survive the filter. Consent banners, analytics beacons and
A/B tooling are real extensions but there is nothing to point at on a call, so they
are dropped — otherwise a store with one GDPR banner would rank as "customised".
"""
import json
import re
import sys

# element key -> (label, handle/app vocabulary)
ELEMENTS = [
    ('trust',    'Trust badges',        r'trust[-_ ]?(icon|badge|seal|banner)|benefit'),
    ('reviews',  'Reviews & ratings',   r'review|rating|nugget|testimonial|okendo|judge|loox|yotpo[- ]?review'),
    ('shipbar',  'Free-ship progress',  r'freeshipping|free[-_ ]?ship|shipping[-_ ]?progress'),
    ('addons',   'Add-ons & upsell',    r'upsell|rebuy|cross[-_ ]?sell|recommend|smart component|urgency|aftersell'),
    ('fields',   'Custom fields',       r'custom[-_ ]?field|attribute|photopendant|personaliz|line item edit|note widget|instruction|dynamic content'),
    ('gift',     'Gift options',        r'gift|wrap|packaging|giftnote|gift note|zest|note widget|greeting'),
    ('loyalty',  'Rewards & points',    r'reward|point|loyal|smile|rivo|cashback|referr|\bvip\b'),
    ('protect',  'Warranty & protection', r'warrant|protect|navidium|mulberry|assurance|redo'),
    ('policy',   'Policy & terms',      r'terms|condition|polic|warning|return'),
    ('duties',   'Duties & tax',        r'\bdut(y|ies)\b|duties-and-taxes|tax id|\bvat\b|landed'),
    ('delivery', 'Delivery & pickup',   r'delivery estimat|shipping[-_ ]?estimat|\bedd\b|locker|pickup|split shipping|decision block|shipping option widget|shipping method'),
    ('capture',  'Email / SMS capture', r'dataships|opt-?in|sms[-_ ]?consent|email collection|phone collection|otp'),
    ('address',  'Address validation',  r'address[-_ ]?valid|addresshero|address blocker|shipping-address-validation'),
    ('payments', 'Payment options',     r'payment[-_ ]?method|alternative[-_ ]?payment|usdc|mobilepay|instal|financ'),
    ('discount', 'Discount control',    r'discount|coupon|promo|reduction|capture discounts'),
]

# extensions that exist but are not worth opening on a call
DROP = re.compile(
    r'gdpr|consent|onetrust|osano|pandectes|consentmo|cookie'
    r'|analytic|monitor|intelligems|visually|a/?b test|checkout-visual'
    r'|govx|id\.me|community verification|donation|shoppinggives'
    r'|purple dot|items monitor', re.I)

# the elements worth opening on a call — used to rank, see build loop
MERCH = {'trust', 'reviews', 'shipbar', 'addons', 'gift', 'loyalty', 'fields', 'protect'}

ZONES = [
    (r'header', 'Header'),
    (r'Contact', 'Contact step'),
    (r'delivery-address|DeliveryAddress', 'Address step'),
    (r'ShippingMethodDetails|ShippingMethods|ShippingOption', 'Shipping step'),
    (r'payment-method-list|PaymentMethod', 'Payment step'),
    (r'Reductions', 'Discount box'),
    (r'CartLineDetails|CartLines|OrderSummary', 'Order summary'),
    (r'Actions', 'Above pay button'),
    (r'PickupLocation', 'Pickup list'),
    (r'footer', 'Footer'),
    (r'Dynamic', 'App-placed'),
]

NAMES = {
    'vincerocollective.com': 'Vincero', 'windupwatchshop.com': 'Windup Watch Shop',
    'bartonwatchbands.com': 'Barton Watch Bands', 'elliotbrownwatches.com': 'Elliot Brown',
    'undone.com': 'UNDONE', 'danielwellington.com': 'Daniel Wellington',
    'originalgrain.com': 'Original Grain', 'spinnaker-watches.com': 'Spinnaker',
    'watchgecko.com': 'WatchGecko', 'autodromo.com': 'Autodromo',
    'lorierwatches.com': 'Lorier', 'marathonwatch.com': 'Marathon',
    'nixon.com': 'Nixon', 'shinola.com': 'Shinola', 'rzewatches.com': 'RZE',
    'vaerwatches.com': 'Vaer', 'serica-watches.com': 'Serica',
    'watchobsession.co.uk': 'WatchObsession', 'tsovet.com': 'TSOVET',
    'thegldshop.com': 'The GLD Shop', 'jaxxon.com': 'Jaxxon',
    'auratenewyork.com': 'AUrate New York', 'missoma.com': 'Missoma',
    'gorjana.com': 'gorjana', 'blenderseyewear.com': 'Blenders Eyewear',
    'knockaround.com': 'Knockaround', 'goodr.com': 'goodr', 'roka.com': 'ROKA',
    'filson.com': 'Filson', 'allbirds.com': 'Allbirds', 'rothys.com': "Rothy's",
    'chubbiesshorts.com': 'Chubbies', 'statebicycle.com': 'State Bicycle Co.',
    'prioritybicycles.com': 'Priority Bicycles', 'aventon.com': 'Aventon',
    'brooklinen.com': 'Brooklinen', 'parachutehome.com': 'Parachute',
    'burrow.com': 'Burrow', 'floydhome.com': 'Floyd', 'ritual.com': 'Ritual',
    'liquiddeath.com': 'Liquid Death', 'deathwishcoffee.com': 'Death Wish Coffee',
    'mackweldon.com': 'Mack Weldon', 'untuckit.com': 'UNTUCKit',
    'trueclassictees.com': 'True Classic', 'fellowproducts.com': 'Fellow',
    'blendjet.com': 'BlendJet', 'therabody.com': 'Therabody',
    'hyperice.com': 'Hyperice', 'tonal.com': 'Tonal',
}

# which sweep a domain came from, for the Category filter on the page
WATCHES = {
    'vincerocollective.com', 'windupwatchshop.com', 'bartonwatchbands.com',
    'elliotbrownwatches.com', 'undone.com', 'danielwellington.com',
    'originalgrain.com', 'spinnaker-watches.com', 'watchgecko.com',
    'autodromo.com', 'lorierwatches.com', 'marathonwatch.com', 'nixon.com',
    'shinola.com', 'rzewatches.com', 'vaerwatches.com', 'serica-watches.com',
    'watchobsession.co.uk', 'tsovet.com',
}
JEWELRY = {'thegldshop.com', 'jaxxon.com', 'auratenewyork.com', 'missoma.com', 'gorjana.com'}
EYEWEAR = {'blenderseyewear.com', 'knockaround.com', 'goodr.com', 'roka.com'}


def zone_label(target):
    for pat, label in ZONES:
        if re.search(pat, target):
            return label
    return target


def elements_for(text):
    return [k for k, _, pat in ELEMENTS if re.search(pat, text, re.I)]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    stores = {}
    for path in sys.argv[1:]:
        for r in json.load(open(path, encoding='utf-8')):
            if not r.get('extensions'):
                continue
            rows = []
            for e in r['extensions']:
                label = f"{e['app']} {e['handle']}".strip()
                if not label or DROP.search(label):
                    continue
                els = elements_for(label)
                if not els:
                    continue
                zones = sorted({zone_label(t) for t in e['targets']})
                # App-placed adds nothing when a real zone is also known
                if len(zones) > 1 and 'App-placed' in zones:
                    zones.remove('App-placed')
                rows.append({'a': e['app'] or '—', 'h': e['handle'] or '—',
                             'z': zones, 'e': els})
            if not rows:
                continue
            dom = r['domain']
            prev = stores.get(dom)
            if prev and len(prev['ck']) >= len(rows):
                continue
            variant = re.search(r'/cart/(\d+):', r['permalink'])
            cat = ('Watches' if dom in WATCHES else 'Jewelry' if dom in JEWELRY
                   else 'Eyewear' if dom in EYEWEAR else 'Premium DTC')
            stores[dom] = {
                'n': NAMES.get(dom, dom.split('.')[0].title()),
                'u': dom,
                'v': int(variant.group(1)) if variant else 0,
                'cat': cat,
                'nx': len(r['extensions']),
                'ck': rows,
                'el': sorted({k for row in rows for k in row['e']},
                             key=lambda k: [e[0] for e in ELEMENTS].index(k)),
            }
            # Rank on the blocks Christen actually points at on a call. Without this a
            # store whose only customisation is the Global-e cross-border suite scores
            # 5 elements (policy/duties/address/payments/discount) off one app and
            # outranks Elliot Brown, whose checkout is four real merchandising blocks.
            stores[dom]['ms'] = len([k for k in stores[dom]['el'] if k in MERCH])

    out = sorted(stores.values(),
                 key=lambda s: (-s['ms'], -len(s['el']), -len(s['ck']), s['n'].lower()))
    data = json.load(open('/tmp/library_data.json', encoding='utf-8'))
    data['ck'] = {
        'elements': [[k, lbl] for k, lbl, _ in ELEMENTS],
        'stores': out,
        'counts': {'stores': len(out),
                   'blocks': sum(len(s['ck']) for s in out),
                   'cats': len({s['cat'] for s in out})},
    }
    json.dump(data, open('/tmp/library_data.json', 'w'), indent=1)
    print(f'{len(out)} stores, {sum(len(s["ck"]) for s in out)} demo-worthy checkout blocks')
    for s in out[:12]:
        print(f"  {s['n']:<22} {s['cat']:<12} {len(s['ck']):>2} blocks  {', '.join(s['el'])}")


if __name__ == '__main__':
    main()
