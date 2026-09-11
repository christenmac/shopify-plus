#!/usr/bin/env python3
"""ckvariant.py — resolve bare domains into cart permalinks for ckdetect.py.

    python3 ckvariant.py domains.txt > permalinks.txt

Pulls /products.json, picks an AVAILABLE variant, and prints "domain variant_id".
Non-Shopify or bot-blocked hosts are skipped with a note on stderr, so this
doubles as the is-it-Shopify gate before the (slower) checkout walk.

Picks a mid-priced available variant rather than the cheapest: the cheapest is
often a $0 sample, gift card or "coming soon" placeholder, none of which reach a
real checkout, and gift cards suppress shipping steps entirely.
"""
import concurrent.futures as cf
import json
import re
import subprocess
import sys

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')
SKIP = re.compile(r'gift[- ]?card|sample|swatch|coming soon|pre[- ]?order|deposit', re.I)


def resolve(domain):
    domain = re.sub(r'^https?://', '', domain.strip()).strip('/').split('/')[0]
    if not domain:
        return None
    for host in (domain, f'www.{domain}') if not domain.startswith('www.') else (domain,):
        out = subprocess.run(
            ['curl', '-sS', '-L', '--max-redirs', '6', '--compressed', '--max-time', '25',
             '-A', UA, f'https://{host}/products.json?limit=250'],
            capture_output=True, text=True, errors='replace')
        try:
            prods = json.loads(out.stdout).get('products', [])
        except Exception:                                     # noqa: BLE001
            continue
        cands = []
        for p in prods:
            if SKIP.search(p.get('title', '')):
                continue
            for v in p.get('variants', []):
                if not v.get('available'):
                    continue
                try:
                    price = float(v.get('price') or 0)
                except (TypeError, ValueError):
                    continue
                if price <= 0:
                    continue
                cands.append((price, v['id'], p.get('title', '')))
        if not cands:
            continue
        cands.sort()
        price, vid, title = cands[len(cands) // 2]
        print(f'  ✔ {domain:<30} {vid}  ${price:<9.2f} {title[:40]}', file=sys.stderr)
        return f'{domain} {vid}'
    print(f'  ✖ {domain:<30} no shopify products.json / no available variant', file=sys.stderr)
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    domains = [l.strip() for l in open(sys.argv[1], encoding='utf-8')
               if l.strip() and not l.startswith('#')]
    print(f'resolving {len(domains)} domain(s)…\n', file=sys.stderr)
    with cf.ThreadPoolExecutor(max_workers=10) as pool:
        for line in pool.map(resolve, domains):
            if line:
                print(line)


if __name__ == '__main__':
    main()
