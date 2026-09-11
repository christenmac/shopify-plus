#!/usr/bin/env python3
"""Evidence gathering per store.

For each domain we fetch the storefront (and its policy pages) and record
HARD signals only:
  * Shopify app-extension slugs from cdn.shopify.com/extensions/<uuid>/<slug>/
  * known app script/host signatures
  * which /policies/* pages are actually published
  * whether products.json contains real bundle/kit SKUs
Everything is tagged with what it proves, so the UI can say
"app detected" rather than pretending we inspected the checkout.
"""
import json, os, re, subprocess, sys, tempfile, concurrent.futures as cf
from collections import defaultdict

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# app signature -> (feature key, human app name)
# keys map to the eight elements the library must cover.
APPS = [
    # reviews
    (r"okendo",                      "reviews",  "Okendo"),
    (r"yotpo",                       "reviews",  "Yotpo"),
    (r"judge\.?me|judgeme",          "reviews",  "Judge.me"),
    (r"stamped\.io|stampedio",       "reviews",  "Stamped"),
    (r"loox",                        "reviews",  "Loox"),
    (r"junip",                       "reviews",  "Junip"),
    (r"reviews\.io|reviewsio",       "reviews",  "Reviews.io"),
    (r"fera\.ai|feraai",             "reviews",  "Fera"),
    (r"trustpilot",                  "reviews",  "Trustpilot"),
    (r"bazaarvoice",                 "reviews",  "Bazaarvoice"),
    (r"powerreviews",                "reviews",  "PowerReviews"),
    # loyalty / rewards
    (r"smile[-_.]?(io|loader|ui)",   "loyalty",  "Smile.io"),
    (r"loyaltylion",                 "loyalty",  "LoyaltyLion"),
    (r"swellrewards|yotpo[-_]loyalty", "loyalty", "Yotpo Loyalty"),
    (r"rivo[-_.]",                   "loyalty",  "Rivo"),
    (r"growave",                     "loyalty",  "Growave"),
    (r"joy[-_]loyalty|avada[-_]joy",  "loyalty",  "Joy Loyalty"),
    (r"friendbuy",                   "loyalty",  "Friendbuy"),
    (r"talkable",                    "loyalty",  "Talkable"),
    (r"referralcandy",               "loyalty",  "ReferralCandy"),
    # upsell / add-ons / recommendations
    (r"rebuy",                       "addons",   "Rebuy"),
    (r"aftersell",                   "addons",   "AfterSell"),
    (r"reconvert",                   "addons",   "ReConvert"),
    (r"zipify|oneclickupsell",       "addons",   "Zipify OCU"),
    (r"checkout[-_]blocks",          "addons",   "Checkout Blocks"),
    (r"selleasy",                    "addons",   "Selleasy"),
    (r"limespot",                    "addons",   "LimeSpot"),
    (r"glood",                       "addons",   "Glood"),
    (r"upcart",                       "addons",   "UpCart"),
    (r"in[-_]?cart[-_]?upsell",      "addons",   "In Cart Upsell"),
    (r"nosto",                       "addons",   "Nosto"),
    (r"dynamic[-_]?yield",           "addons",   "Dynamic Yield"),
    # returns / warranty / shipping protection (policy + post-purchase)
    (r"\bredo\b|redo-v\d",           "policies", "Redo"),
    (r"loopreturns|loop[-_]returns",  "policies", "Loop Returns"),
    (r"returngo|return[-_]go",       "policies", "ReturnGO",),
    (r"aftership",                   "policies", "AfterShip"),
    (r"corso",                       "policies", "Corso"),
    (r"\broute\b|routeapp",          "policies", "Route"),
    (r"narvar",                      "policies", "Narvar"),
    (r"extend[-_](protect|warranty)|extend\.com", "policies", "Extend"),
    (r"clyde",                       "policies", "Clyde"),
    (r"seel",                        "policies", "Seel"),
    # gift options
    (r"giftship",                    "gift",     "Giftship"),
    (r"gift[-_]?wrap",               "gift",     "Gift Wrap"),
    (r"giftnote|gift[-_]note",       "gift",     "GiftNote"),
    (r"govalo",                      "gift",     "Govalo"),
    (r"gift[-_]options",             "gift",     "Gift Options"),
    (r"\bwrapin\b",                  "gift",     "Wrapin"),
    # bundling
    (r"fastbundle|fast[-_]bundle",   "bundle",   "Fast Bundle"),
    (r"bundler[-_.]",                "bundle",   "Bundler"),
    (r"kaching[-_]?bundle",          "bundle",   "Kaching Bundles"),
    (r"simple[-_]bundles",           "bundle",   "Simple Bundles"),
    (r"bold[-_]bundles",             "bundle",   "Bold Bundles"),
    # free shipping / progress bar
    (r"hextom",                      "shipbar",  "Hextom"),
    (r"free[-_]?shipping[-_]?bar",   "shipbar",  "Free Shipping Bar"),
    (r"shipping[-_]?bar",            "shipbar",  "Shipping Bar"),
    (r"essential[-_]free[-_]ship",   "shipbar",  "Essential Free Shipping"),
    # trust badges
    (r"trust[-_]?badge",             "trust",    "Trust Badges"),
    (r"trustedsite|mcafeesecure",    "trust",    "TrustedSite"),
    (r"norton(secured|shopping)",    "trust",    "Norton Shopping"),
    (r"shopper[-_]?approved",        "trust",    "Shopper Approved"),
    # subscriptions (bonus, not one of the eight)
    (r"rechargepayments|recharge[-_]", "sub",    "Recharge"),
    (r"skio",                        "sub",      "Skio"),
    (r"loopsubscriptions",           "sub",      "Loop Subs"),
    (r"stay[-_]ai|stayai",           "sub",      "Stay AI"),
    (r"smartrr",                     "sub",      "Smartrr"),
    (r"appstle",                     "sub",      "Appstle"),
    # BNPL
    (r"shop[-_]pay[-_]install|shoppay", "bnpl",  "Shop Pay Installments"),
    (r"affirm",                      "bnpl",     "Affirm"),
    (r"klarna",                      "bnpl",     "Klarna"),
    (r"afterpay",                    "bnpl",     "Afterpay"),
    (r"sezzle",                      "bnpl",     "Sezzle"),
]
APPS = [(re.compile(p, re.I), k, n) for p, k, n in APPS]

POLICIES = ["shipping-policy", "refund-policy", "terms-of-service", "privacy-policy"]


def curl(url, timeout=20, body=True):
    jar = tempfile.NamedTemporaryFile(delete=False, suffix=".ck").name
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "-A", UA, "--compressed",
           "-c", jar, "-b", jar, "-o", "-" if body else "/dev/null",
           "-w", "\n__EFF__%{url_effective}\t%{http_code}\t%{size_download}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
        return r.stdout.decode("utf-8", "replace")
    except Exception:
        return ""
    finally:
        try:
            os.unlink(jar)
        except OSError:
            pass


def split(raw):
    if "__EFF__" not in raw:
        return raw, "", "0", "0"
    b, meta = raw.rsplit("\n__EFF__", 1)
    parts = (meta.split("\t") + ["", "", ""])[:3]
    return b, parts[0], parts[1], parts[2]


def scan(dom):
    out = {"domain": dom, "apps": defaultdict(set), "ext_slugs": [],
           "policies": [], "bundles": [], "err": ""}
    text = ""
    for path in ("/", "/collections/all", "/pages/faq"):
        b, _, code, _ = split(curl(f"https://{dom}{path}"))
        if code == "200":
            text += b
        if len(text) > 2_500_000:
            break
    if not text:
        out["err"] = "storefront unreadable"
        return out

    # app extension slugs are the strongest evidence: the merchant installed it
    for m in re.finditer(r"cdn\.shopify\.com/extensions/[0-9a-f-]{36}/([A-Za-z0-9_.\-]+)/", text):
        slug = m.group(1)
        if slug not in out["ext_slugs"]:
            out["ext_slugs"].append(slug)

    hay = text + " " + " ".join(out["ext_slugs"])
    for rx, key, name in APPS:
        if rx.search(hay):
            out["apps"][key].add(name)

    # published policy pages
    for p in POLICIES:
        _, eff, code, size = split(curl(f"https://{dom}/policies/{p}", body=False))
        if code == "200" and int(size or 0) > 2000 and "/policies/" in eff:
            out["policies"].append(p)

    # real bundle SKUs
    b, _, code, _ = split(curl(f"https://{dom}/products.json?limit=250"))
    if code == "200":
        try:
            for p in json.loads(b).get("products", []):
                t = p.get("title", "")
                if re.search(r"\bbundle\b|\bkit\b|\bset\b|\bduo\b|\btrio\b|\bpack\b", t, re.I):
                    out["bundles"].append(t[:60])
        except Exception:
            pass

    out["apps"] = {k: sorted(v) for k, v in out["apps"].items()}
    return out


doms = [d.strip() for d in open(sys.argv[1]) if d.strip()]
res = []
with cf.ThreadPoolExecutor(max_workers=8) as ex:
    for r in ex.map(scan, doms):
        res.append(r)
        keys = ",".join(sorted(r["apps"])) if r["apps"] else "-"
        print(f"{r['domain']:32s} apps[{keys}] pol={len(r['policies'])} "
              f"bund={len(r['bundles'])} ext={len(r['ext_slugs'])} {r['err']}", flush=True)

json.dump(res, open("/tmp/detect_results.json", "w"), indent=1)
print(f"\nscanned {len(res)}")
