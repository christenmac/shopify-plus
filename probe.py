#!/usr/bin/env python3
"""For each domain: find an in-stock variant, build a cart permalink,
follow it, and record whether it lands inside a live /checkouts/ session."""
import json, os, re, subprocess, sys, tempfile, concurrent.futures as cf

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SKIP_TITLE = re.compile(r'gift ?card|content:|sample|donation|test', re.I)


def curl(url, head_only=False, timeout=25):
    # A cart permalink hands back a cart cookie on the first hop; without a
    # jar the cart is empty by the time we reach /checkout and the store
    # bounces us to the homepage. This is the whole reason the old links broke.
    jar = tempfile.NamedTemporaryFile(delete=False, suffix=".ck").name
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "-A", UA,
           "--compressed", "-c", jar, "-b", jar,
           "-o", "/dev/null" if head_only else "-",
           "-w", "\n__EFF__%{url_effective}\t%{http_code}"]
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


def variant_for(dom):
    """Pick a cheap-ish, available, non-gift-card variant."""
    for url in (f"https://{dom}/products.json?limit=40",
                f"https://www.{dom}/products.json?limit=40"):
        body = curl(url)
        body = body.split("\n__EFF__")[0]
        try:
            data = json.loads(body)
        except Exception:
            continue
        cands = []
        for p in data.get("products", []):
            t = p.get("title", "")
            if SKIP_TITLE.search(t):
                continue
            if p.get("product_type", "").lower() in ("gift card", "gift cards"):
                continue
            for v in p.get("variants", []):
                if not v.get("available"):
                    continue
                try:
                    price = float(v.get("price") or 0)
                except Exception:
                    price = 0
                if price <= 0:
                    continue
                cands.append((price, v["id"], t))
        if cands:
            cands.sort()
            # middle-priced item: avoids weird $0.01 test SKUs and $5k outliers
            return cands[len(cands) // 3]
    return None


def probe(dom):
    out = {"domain": dom, "variant": None, "ok": False, "final": "", "note": ""}
    v = variant_for(dom)
    if not v:
        out["note"] = "no public products.json"
        return out
    price, vid, title = v
    out["variant"] = vid
    out["product"] = title[:60]
    out["price"] = price
    link = f"https://{dom}/cart/{vid}:1"
    body = curl(link, head_only=True)
    m = re.search(r"__EFF__(\S+)\t(\d+)", body)
    if not m:
        out["note"] = "permalink request failed"
        return out
    final, code = m.group(1), m.group(2)
    out["final"] = final
    if "/checkouts/" in final and code == "200":
        out["ok"] = True
    elif "/cart" in final:
        out["note"] = "landed on cart page"
    else:
        out["note"] = f"landed {code} {final[:70]}"
    return out


doms = [d.strip() for d in open(sys.argv[1]) if d.strip()]
res = []
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for r in ex.map(probe, doms):
        res.append(r)
        flag = "OK " if r["ok"] else "-- "
        print(flag, r["domain"], r.get("variant") or "", r["note"], flush=True)

json.dump(res, open("/tmp/probe_results.json", "w"), indent=1)
print(f"\n{sum(1 for r in res if r['ok'])}/{len(res)} land in live checkout")
