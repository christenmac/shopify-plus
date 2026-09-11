#!/usr/bin/env python3
"""Is this domain actually on Shopify? Header + body signature check."""
import json, re, subprocess, sys, concurrent.futures as cf

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def check(dom):
    try:
        r = subprocess.run(
            ["curl", "-sSLD", "-", "--max-time", "20", "-A", UA, "--compressed",
             f"https://{dom}/"],
            capture_output=True, timeout=35)
        t = r.stdout.decode("utf-8", "replace")
    except Exception:
        return {"domain": dom, "shopify": None, "why": "unreachable"}
    low = t.lower()
    hits = []
    if re.search(r"^x-shopid:", low, re.M):
        hits.append("x-shopid header")
    if re.search(r"^x-shopify-stage:", low, re.M):
        hits.append("x-shopify-stage header")
    if "cdn.shopify.com" in low:
        hits.append("cdn.shopify.com")
    if "shopify.theme" in low or "window.shopify" in low:
        hits.append("Shopify JS global")
    if "myshopify.com" in low:
        hits.append("myshopify ref")
    # competing platforms
    other = []
    for k, v in {"salesforce commerce": "demandware", "bigcommerce": "bigcommerce",
                 "magento": "magento", "sap hybris": "hybris",
                 "commercetools": "commercetools", "vtex": "vtex",
                 "woocommerce": "woocommerce", "shopware": "shopware"}.items():
        if v in low:
            other.append(k)
    return {"domain": dom, "shopify": bool(hits), "why": ", ".join(hits) or "no signature",
            "other": other}


doms = [d.strip() for d in open(sys.argv[1]) if d.strip()]
out = []
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for r in ex.map(check, doms):
        out.append(r)
        print("SHOPIFY " if r["shopify"] else "NOT     ", r["domain"],
              "|", r["why"], ("| also:" + ",".join(r["other"])) if r.get("other") else "",
              flush=True)
json.dump(out, open("/tmp/shopify_check.json", "w"), indent=1)
print(f"\n{sum(1 for r in out if r['shopify'])}/{len(out)} show a Shopify signature")
