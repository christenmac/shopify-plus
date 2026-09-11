#!/usr/bin/env python3
"""Rebuild checkout-library.html from verified probe + detection evidence."""
import json, re, datetime

SRC = "/tmp/checkout-library.BACKUP.html"   # pre-rebuild original
OUT = "/Users/christenmcallister/shopify-plus/checkout-library.html"
TODAY = "2026-08-25"

probe = {r["domain"]: r for r in json.load(open("/tmp/probe_results.json"))}
detect = {r["domain"]: r for r in json.load(open("/tmp/detect_results.json"))}
excl = json.load(open("/tmp/excluded.json"))
shopchk = {r["domain"]: r for r in json.load(open("/tmp/shopify_check.json"))}

# ---- parse the old INDUSTRIES array for names / industries / type tags -------
src = open(SRC, encoding="utf-8").read()
block = src[src.index("const INDUSTRIES = ["):src.index("\n];", src.index("const INDUSTRIES = ["))]

inds = []
for m in re.finditer(
        r"id:'([^']+)',\s*emoji:'([^']*)',\s*name:'([^']+)',\s*tags:\[([^\]]*)\],\s*brands:\[(.*?)\],\s*\}",
        block, re.S):
    iid, emoji, name, tags, brands = m.groups()
    tags = re.findall(r"'([^']+)'", tags)
    blist = []
    for bm in re.finditer(r"\{n:'((?:[^'\\]|\\.)*)',\s*u:'([^']+)',\s*f:\[([^\]]*)\]", brands):
        n = bm.group(1).replace("\\'", "'")
        blist.append({"n": n, "u": bm.group(2),
                      "f": re.findall(r"'([^']+)'", bm.group(3))})
    inds.append({"id": iid, "emoji": emoji, "name": name, "tags": tags, "brands": blist})

# ---- the eight elements the library must cover ------------------------------
ELEMENTS = [
    ("trust",    "Trust badges"),
    ("reviews",  "Reviews"),
    ("shipbar",  "Free-ship bar"),
    ("policies", "Ship & return policy"),
    ("addons",   "Add-ons / recs"),
    ("gift",     "Gift options"),
    ("bundle",   "Bundling"),
    ("loyalty",  "Rewards / loyalty"),
]
EXTRA = [("sub", "Subscriptions"), ("bnpl", "BNPL")]


def evidence(dom):
    """Return {elementKey: [app names or evidence strings]} — hard signals only."""
    d = detect.get(dom)
    if not d:
        return {}
    a = d.get("apps", {})
    ev = {}
    for k, _ in ELEMENTS + EXTRA:
        names = list(a.get(k, []))
        if k == "policies":
            pol = [p.replace("-", " ") for p in d.get("policies", [])
                   if p in ("shipping-policy", "refund-policy")]
            names += [f"/{p.replace(' ', '-')} published" for p in pol]
        if k == "bundle" and len(d.get("bundles", [])) >= 3:
            names.append(f"{len(d['bundles'])} bundle/kit SKUs")
        if names:
            ev[k] = names
    return ev


# ---- assemble only brands whose checkout permalink actually resolved --------
out_inds, seen_brand, dropped = [], {}, []
for ind in inds:
    kept = []
    for b in ind["brands"]:
        p = probe.get(b["u"])
        if not (p and p.get("ok")):
            dropped.append((b["n"], b["u"]))
            continue
        ev = evidence(b["u"])
        kept.append({
            "n": b["n"], "u": b["u"], "v": p["variant"],
            "p": p.get("product", ""), "ev": ev,
            "c": sum(1 for k, _ in ELEMENTS if k in ev),
            "x": len(detect.get(b["u"], {}).get("ext_slugs", [])),
        })
        seen_brand[b["u"]] = b["n"]
    if kept:
        kept.sort(key=lambda z: (-z["c"], z["n"].lower()))
        out_inds.append({"id": ind["id"], "name": ind["name"],
                         "tags": ind["tags"], "brands": kept})

# top showcase: best coverage, one entry per domain
best = {}
for ind in out_inds:
    for b in ind["brands"]:
        cur = best.get(b["u"])
        if not cur or b["c"] > cur["c"]:
            best[b["u"]] = {**b, "ind": ind["name"]}
top = sorted(best.values(), key=lambda z: (-z["c"], -z["x"], z["n"].lower()))[:12]

# best complementary pair: two stores that together cover all eight
import itertools
pool = sorted(best.values(), key=lambda z: -z["c"])[:30]
pair = None
for a, b in itertools.combinations(pool, 2):
    ga = {k for k, _ in ELEMENTS if k in a["ev"]}
    gb = {k for k, _ in ELEMENTS if k in b["ev"]}
    if len(ga | gb) == len(ELEMENTS):
        names = dict(ELEMENTS)
        pair = {
            "a": a, "b": b,
            "aOnly": ", ".join(names[k].lower() for k, _ in ELEMENTS if k in ga - gb) or "shared coverage",
            "bOnly": ", ".join(names[k].lower() for k, _ in ELEMENTS if k in gb - ga) or "shared coverage",
        }
        break

blocked = sorted(excl["blocked"])
notshop = sorted(excl["not_shopify"])
shopify_no_link = sorted(d for d, r in shopchk.items() if r.get("shopify"))

DATA = {
    "generated": TODAY,
    "elements": ELEMENTS,
    "extra": EXTRA,
    "industries": out_inds,
    "top": top,
    "pair": pair,
    "excluded": {"notShopify": notshop, "blocked": blocked,
                 "shopifyNoLink": shopify_no_link},
    "counts": {
        "verified": len(best),
        "rows": sum(len(i["brands"]) for i in out_inds),
        "probed": len(probe),
    },
}
json.dump(DATA, open("/tmp/library_data.json", "w"), indent=1)
print("verified domains:", DATA["counts"]["verified"],
      "| rows:", DATA["counts"]["rows"],
      "| industries:", len(out_inds))
print("top:", [(t["n"], t["c"]) for t in top])
