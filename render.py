#!/usr/bin/env python3
import json

DATA = json.load(open("/tmp/library_data.json"))
OUT = "/Users/christenmcallister/shopify-plus/checkout-library.html"

TPL = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Checkout Library</title>
<style>
:root{
  --accent:#008060; --accent-dk:#004c3f; --accent-wash:#eef6f2;
  --ink:#12161a; --ink-2:#3d4650; --ink-3:#6a7480; --ink-4:#98a2ae;
  --line:#e4e8ec; --line-2:#eef1f4;
  --bg:#f7f8fa; --card:#fff;
  --warn:#a1560c; --warn-wash:#fdf6ec;
  --r:8px;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  background:var(--bg); color:var(--ink);
  font-size:14px; line-height:1.5;
  -webkit-font-smoothing:antialiased;
}
a{color:inherit}
.wrap{max-width:1240px;margin:0 auto;padding:0 28px}

/* ---------- masthead ---------- */
.mast{background:#0f1317;color:#fff;border-bottom:1px solid #000}
.mast .wrap{padding:30px 28px 26px}
.mast-top{display:flex;align-items:flex-start;justify-content:space-between;gap:32px;flex-wrap:wrap}
.eyebrow{
  font-size:10.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;
  color:#7f8b97;margin-bottom:9px
}
h1{font-size:25px;font-weight:680;letter-spacing:-.022em;line-height:1.15}
.mast p.lede{color:#aeb8c2;max-width:660px;margin-top:9px;font-size:13.5px;line-height:1.55}
.mast p.lede strong{color:#fff;font-weight:600}
.stamp{
  display:inline-flex;align-items:center;gap:7px;flex-shrink:0;
  border:1px solid #2b333b;border-radius:100px;padding:6px 13px;
  font-size:11.5px;color:#aeb8c2;background:#161b20;white-space:nowrap
}
.stamp .dot{width:6px;height:6px;border-radius:50%;background:#3fbf87;box-shadow:0 0 0 3px rgba(63,191,135,.16)}

.metrics{display:flex;gap:0;margin-top:24px;border-top:1px solid #22282e;flex-wrap:wrap}
.metric{padding:14px 30px 0 0;margin-right:30px}
.metric b{display:block;font-size:21px;font-weight:660;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.metric span{font-size:11px;color:#7f8b97;letter-spacing:.03em}

/* ---------- how-to panel ---------- */
.howto{background:var(--card);border-bottom:1px solid var(--line)}
.howto .wrap{padding:22px 28px}
.howto-grid{display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:26px;align-items:start}
.step{display:flex;gap:11px}
.step-n{
  flex-shrink:0;width:21px;height:21px;border-radius:50%;
  background:var(--accent-wash);color:var(--accent-dk);
  font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;
  margin-top:1px
}
.step h4{font-size:12.5px;font-weight:650;margin-bottom:3px}
.step p{font-size:12px;color:var(--ink-3);line-height:1.5}
.step code{font-family:var(--mono);font-size:11px;background:var(--line-2);padding:1px 4px;border-radius:3px;color:var(--ink-2)}
.addr{
  border-left:1px solid var(--line);padding-left:24px;min-width:216px
}
.addr h4{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-4);margin-bottom:7px}
.addr pre{
  font-family:var(--mono);font-size:11px;line-height:1.65;color:var(--ink-2);
  white-space:pre-wrap;margin-bottom:8px
}
.btn-copy{
  border:1px solid var(--line);background:#fff;border-radius:6px;padding:5px 11px;
  font-size:11.5px;font-weight:600;cursor:pointer;color:var(--ink-2);
  font-family:inherit;transition:.12s
}
.btn-copy:hover{border-color:var(--accent);color:var(--accent)}
.btn-copy.done{background:var(--accent-wash);border-color:var(--accent);color:var(--accent-dk)}

.note{
  margin-top:18px;padding:11px 14px;background:var(--warn-wash);
  border:1px solid #f0e2cd;border-radius:var(--r);
  font-size:12px;color:#6b4a1c;line-height:1.55
}
.note b{color:#4a3211}

/* ---------- section headings ---------- */
.sec{padding:34px 0 0}
.sec-hd{display:flex;align-items:baseline;justify-content:space-between;gap:20px;margin-bottom:15px;flex-wrap:wrap}
.sec-hd h2{font-size:16px;font-weight:660;letter-spacing:-.015em}
.sec-hd p{font-size:12.5px;color:var(--ink-3);margin-top:4px;max-width:640px;line-height:1.55}

/* ---------- showcase cards ---------- */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(286px,1fr));gap:12px}
.card{
  background:var(--card);border:1px solid var(--line);border-radius:var(--r);
  padding:15px 16px 13px;display:flex;flex-direction:column;
  transition:border-color .12s,box-shadow .12s
}
.card:hover{border-color:#cfd6dd;box-shadow:0 1px 3px rgba(16,24,32,.05)}
.card-hd{display:flex;align-items:baseline;justify-content:space-between;gap:10px}
.card-hd .nm{font-size:14px;font-weight:650;letter-spacing:-.01em}
.card .ind{font-size:11px;color:var(--ink-4);margin-top:2px}
.score{
  font-family:var(--mono);font-size:11px;font-weight:600;color:var(--accent-dk);
  background:var(--accent-wash);border-radius:4px;padding:2px 6px;flex-shrink:0;
  font-variant-numeric:tabular-nums
}
.card .go{margin-top:auto}

/* ---------- element pills + app line ---------- */
.pills{display:flex;flex-wrap:wrap;gap:4px;margin:11px 0 9px}
.pill{
  font-size:10.5px;font-weight:600;padding:2.5px 8px;border-radius:100px;
  background:var(--accent-wash);color:var(--accent-dk);white-space:nowrap
}
.pill.off{background:#f3f5f7;color:var(--ink-4);font-weight:500}
.appline{font-size:11px;color:var(--ink-3);line-height:1.6;flex:1;margin-bottom:11px}
.appline b{font-weight:600;color:var(--ink-4);font-size:10px;letter-spacing:.06em;text-transform:uppercase}
.appline .none{color:var(--ink-4);font-style:italic}

/* ---------- pair callout ---------- */
.pair{
  background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:var(--r);padding:14px 17px;margin-bottom:12px;
  display:flex;align-items:center;gap:18px;flex-wrap:wrap
}
.pair-txt{flex:1;min-width:280px}
.pair-txt h4{font-size:12.5px;font-weight:650;margin-bottom:3px}
.pair-txt p{font-size:12px;color:var(--ink-3);line-height:1.55}
.pair-txt p b{color:var(--ink-2);font-weight:600}
.pair-go{display:flex;gap:7px;flex-wrap:wrap}

/* ---------- coverage meter ----------
   Needs an explicit width: as a flex item its `flex:1` children resolve
   from a 0 basis and the whole bar collapses to nothing. */
.meter{display:flex;gap:2.5px}
.meter i{
  height:5px;flex:1 1 auto;min-width:3px;border-radius:2px;background:#e6eaee;
  transition:background .12s
}
.meter i.on{background:var(--accent)}
.meter.sm{width:72px;flex:0 0 72px}
.meter.sm i{height:4px}

/* ---------- buttons ---------- */
.go{
  display:inline-flex;align-items:center;gap:6px;
  border:1px solid var(--accent);background:var(--accent);color:#fff;
  border-radius:6px;padding:7px 13px;font-size:12px;font-weight:600;
  text-decoration:none;transition:.12s;white-space:nowrap
}
.go:hover{background:var(--accent-dk);border-color:var(--accent-dk)}
.go svg{opacity:.85}
.go-sm{
  display:inline-flex;align-items:center;gap:5px;
  border:1px solid var(--line);background:#fff;color:var(--ink-2);
  border-radius:6px;padding:5px 10px;font-size:11.5px;font-weight:600;
  text-decoration:none;transition:.12s;white-space:nowrap
}
.go-sm:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-wash)}
.go-sm svg{opacity:.5}

/* ---------- toolbar ---------- */
.toolbar{
  position:sticky;top:0;z-index:20;background:rgba(247,248,250,.94);
  backdrop-filter:saturate(180%) blur(12px);
  border-bottom:1px solid var(--line);margin-top:34px
}
.toolbar .wrap{padding:12px 28px}
.tb-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.search-box{position:relative;flex:1;min-width:240px;max-width:400px}
.search-box svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);opacity:.4;pointer-events:none}
#q{
  width:100%;padding:8px 12px 8px 33px;border:1px solid var(--line);
  border-radius:6px;font-size:13px;font-family:inherit;background:#fff;
  color:var(--ink);outline:none;transition:.12s
}
#q:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,128,96,.1)}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:6px;overflow:hidden;background:#fff}
.seg button{
  border:none;background:#fff;padding:7px 12px;font-size:12px;font-weight:550;
  cursor:pointer;font-family:inherit;color:var(--ink-3);
  border-right:1px solid var(--line);transition:.12s
}
.seg button:last-child{border-right:none}
.seg button:hover{background:var(--line-2);color:var(--ink)}
.seg button.on{background:var(--accent);color:#fff}
.tb-lbl{font-size:10.5px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-4)}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px;align-items:center}
.chip{
  border:1px solid var(--line);background:#fff;border-radius:100px;
  padding:4px 11px;font-size:11.5px;font-weight:550;cursor:pointer;
  font-family:inherit;color:var(--ink-2);transition:.12s;white-space:nowrap
}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.chip .n{opacity:.55;font-variant-numeric:tabular-nums;margin-left:3px}

/* ---------- library ---------- */
.count-line{font-size:12.5px;color:var(--ink-3);margin:18px 0 11px}
.count-line strong{color:var(--ink);font-weight:650}
.grp{background:var(--card);border:1px solid var(--line);border-radius:var(--r);margin-bottom:8px;overflow:hidden}
.grp-hd{
  display:flex;align-items:center;gap:12px;padding:11px 16px;cursor:pointer;
  user-select:none;transition:background .1s
}
.grp-hd:hover{background:#fafbfc}
.grp-nm{font-size:13px;font-weight:650;letter-spacing:-.01em}
.tag{
  font-size:9.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;
  padding:2px 7px;border-radius:3px;background:var(--line-2);color:var(--ink-3)
}
.tag.b2b{background:#f1eefe;color:#5b34c4}
.tag.regulated{background:#fdf3e7;color:#8a4c08}
.tag.subscription{background:#e8f6f2;color:#046b53}
.tag.luxury{background:#fdeef5;color:#9c1259}
.grp-meta{margin-left:auto;display:flex;align-items:center;gap:14px;flex-shrink:0}
.grp-n{font-size:11.5px;color:var(--ink-4);font-variant-numeric:tabular-nums}
.chev{color:var(--ink-4);transition:transform .18s;flex-shrink:0}
.grp.open .chev{transform:rotate(90deg)}
.grp-bd{display:none;border-top:1px solid var(--line-2)}
.grp.open .grp-bd{display:block}

.row{
  display:grid;grid-template-columns:26px 1fr 116px minmax(0,1.5fr) auto;
  gap:14px;align-items:center;padding:9px 16px;border-bottom:1px solid var(--line-2)
}
.row:last-child{border-bottom:none}
.row:hover{background:#fafbfc}
.row .nm{font-size:13px;font-weight:600;letter-spacing:-.005em}
.row .dom{font-size:11px;color:var(--ink-4);font-family:var(--mono)}
.row .ev{font-size:11px;color:var(--ink-3);line-height:1.55;overflow:hidden}
.row .ev b{color:var(--ink-2);font-weight:600}
.mwrap{display:flex;align-items:center;gap:7px}
.mwrap .sc{font-family:var(--mono);font-size:10.5px;color:var(--ink-4);font-variant-numeric:tabular-nums;flex-shrink:0}
.seen{
  width:15px;height:15px;border:1.5px solid var(--line);border-radius:4px;
  cursor:pointer;background:#fff;display:flex;align-items:center;justify-content:center;
  padding:0;transition:.12s
}
.seen:hover{border-color:var(--accent)}
.seen.on{background:var(--accent);border-color:var(--accent)}
.seen svg{display:none}
.seen.on svg{display:block}

.empty{text-align:center;padding:56px 24px;color:var(--ink-3);background:#fff;border:1px solid var(--line);border-radius:var(--r)}

/* ---------- method / excluded ---------- */
details.meth{background:#fff;border:1px solid var(--line);border-radius:var(--r);margin-bottom:8px}
details.meth summary{
  padding:12px 16px;cursor:pointer;font-size:12.5px;font-weight:650;
  list-style:none;display:flex;align-items:center;gap:8px
}
details.meth summary::-webkit-details-marker{display:none}
details.meth summary::after{content:"›";margin-left:auto;color:var(--ink-4);font-size:15px;transition:transform .18s}
details.meth[open] summary::after{transform:rotate(90deg)}
.meth-bd{padding:0 16px 15px;font-size:12px;color:var(--ink-2);line-height:1.65}
.meth-bd p{margin-bottom:9px;max-width:820px}
.meth-bd h5{font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-4);margin:14px 0 6px}
.meth-bd code{font-family:var(--mono);font-size:11px;background:var(--line-2);padding:1px 4px;border-radius:3px}
.domlist{display:flex;flex-wrap:wrap;gap:4px}
.domlist span{
  font-family:var(--mono);font-size:10.5px;color:var(--ink-3);
  background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:2px 6px
}
footer{padding:26px 0 40px;font-size:11.5px;color:var(--ink-4);line-height:1.7}
kbd{background:#fff;border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;padding:1px 5px;font-size:10.5px;font-family:var(--mono)}
mark{background:#fdf0a8;border-radius:2px;padding:0 1px;color:inherit}

@media(max-width:1000px){
  .howto-grid{grid-template-columns:1fr 1fr;gap:20px}
  .addr{border-left:none;padding-left:0;border-top:1px solid var(--line);padding-top:16px;grid-column:1/-1}
  .row{grid-template-columns:26px 1fr 106px auto;gap:11px}
  .row .ev{display:none}
}
@media(max-width:640px){
  .wrap{padding:0 16px}
  .mast .wrap,.howto .wrap,.toolbar .wrap{padding-left:16px;padding-right:16px}
  .howto-grid{grid-template-columns:1fr}
  .row{grid-template-columns:22px 1fr auto;gap:9px}
  .row .mwrap{display:none}
}

/* ---- checkout-level verified section (ck-*) --------------------------------
   Namespaced so it cannot collide with the storefront-evidence table above. */
.ckwrap{background:#f7f8fa;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:34px 0 38px;margin:36px 0 0}
.ck-lead{max-width:760px;margin:0 0 20px}
.ck-lead .badge-new{display:inline-block;font:700 10px/1 ui-sans-serif,system-ui;letter-spacing:.09em;text-transform:uppercase;color:#0a6b3d;background:#d9f2e4;border:1px solid #a8ddc2;border-radius:4px;padding:4px 7px;margin-bottom:9px}
.ck-lead p{margin:7px 0 0;font-size:13.5px;line-height:1.6;color:var(--muted)}
.ck-chips{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin:0 0 16px}
.ck-chips .tb-lbl{margin-right:3px}
.ck-when{font-size:11.5px;color:var(--ink-4);margin-left:8px}
.ck-chip{font:600 11.5px/1 ui-sans-serif,system-ui;color:#42474f;background:#fff;border:1px solid var(--line);border-radius:20px;padding:6px 11px;cursor:pointer}
.ck-chip:hover{border-color:#9aa2ad}
.ck-chip.on{background:#0a6b3d;border-color:#0a6b3d;color:#fff}
.ck-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:13px}
.ck-card{background:#fff;border:1px solid var(--line);border-radius:9px;padding:15px 16px 14px;display:flex;flex-direction:column}
.ck-card.hero{border-color:#a8ddc2;box-shadow:0 0 0 3px #eafaf1}
.ck-hd{display:flex;justify-content:space-between;align-items:flex-start;gap:9px;margin-bottom:3px}
.ck-nm{font:700 15px/1.25 ui-sans-serif,system-ui;color:var(--ink)}
.ck-cat{font-size:11.5px;color:var(--muted);margin-top:2px}
.ck-n{flex:0 0 auto;font:700 11px/1 ui-sans-serif,system-ui;color:#0a6b3d;background:#eafaf1;border-radius:20px;padding:5px 9px;white-space:nowrap}
.ck-blocks{margin:11px 0 0;border-top:1px dashed var(--line);padding-top:10px;display:flex;flex-direction:column;gap:8px}
.ck-b{font-size:12.5px;line-height:1.45}
.ck-b .bh{font-weight:650;color:var(--ink)}
.ck-b .ba{color:var(--muted)}
.ck-z{display:inline-flex;flex-wrap:wrap;gap:4px;margin-top:3px}
.ck-z span{font:600 10.5px/1 ui-sans-serif,system-ui;color:#3d4550;background:#eef0f3;border-radius:3px;padding:4px 6px}
.ck-more{font-size:12px;color:var(--muted);margin-top:2px}
.ck-blocks{flex:1 1 auto}
.ck-card .go{margin-top:13px}
.ck-note{max-width:860px;margin:20px 0 0;font-size:12.5px;line-height:1.6;color:var(--muted)}
.ck-note b{color:var(--ink)}
@media(max-width:620px){.ck-grid{grid-template-columns:1fr}}
</style>
</head>
<body>

<header class="mast">
  <div class="wrap">
    <div class="mast-top">
      <div>
        <div class="eyebrow">Shopify Plus &middot; Sales Reference</div>
        <h1>Checkout Library</h1>
        <p class="lede">Live examples of customized Shopify checkouts, for screensharing on merchant calls.
          Every link below drops a real in-stock product into that store's cart and
          <strong>opens their actual checkout</strong> &mdash; not their homepage.</p>
      </div>
      <div class="stamp"><span class="dot"></span><span id="stamp-txt">All links verified __DATE_H__</span></div>
    </div>
    <div class="metrics">
      <div class="metric"><b id="m1">0</b><span>Checkouts that open live</span></div>
      <div class="metric"><b id="m2">0</b><span>Industries</span></div>
      <div class="metric"><b>8</b><span>Elements tracked</span></div>
      <div class="metric"><b id="m4">0</b><span>Old entries removed</span></div>
    </div>
  </div>
</header>

<section class="howto">
  <div class="wrap">
    <div class="howto-grid">
      <div class="step"><div class="step-n">1</div><div>
        <h4>Open a live checkout</h4>
        <p>Click any <em>Open checkout</em> button. It uses a cart permalink
           (<code>/cart/&lt;variant&gt;:1</code>), so the store loads with an item already in the
           cart and lands you on <code>/checkouts/&hellip;</code>.</p></div></div>
      <div class="step"><div class="step-n">2</div><div>
        <h4>Reach the payment step</h4>
        <p>Paste the test address on the right. On a one-page checkout the payment section is
           already there; on a three-page checkout it appears once an address and rate exist.</p></div></div>
      <div class="step"><div class="step-n">3</div><div>
        <h4>Point out the blocks</h4>
        <p>The detected apps under each brand tell you what to look for &mdash; trust badges,
           reviews, gift options, upsells. Tick the box once you've eyeballed it yourself.</p></div></div>
      <div class="addr">
        <h4>Test address</h4>
        <pre id="addr-txt">Alex Demo
500 7th Avenue
New York, NY 10018
United States
415-555-0132
demo@example.com</pre>
        <button class="btn-copy" id="copy-addr">Copy test address</button>
      </div>
    </div>
    <div class="note">
      <b>On the payment step:</b> a link can't jump straight to it. Shopify only renders payment
      once contact details, a shipping address and a shipping rate exist, and a URL can't supply
      those &mdash; so the deepest a public link reaches is the checkout's first step. That is where
      every in-checkout extension lives, and the test address above gets you to payment in about
      ten seconds. If you need a payment step that is customized on demand, use the
      <strong>checkout-preview</strong> demo instead &mdash; this library is for showing real merchants' real checkouts.
    </div>
  </div>
</section>

<div class="wrap">
  <section class="sec">
    <div class="sec-hd">
      <div>
        <h2>Top examples to show a merchant</h2>
        <p>Widest coverage of the eight elements, and the ones worth opening on a call.
           The bar shows how many of the eight we found hard evidence for.</p>
      </div>
    </div>
    <div class="pair" id="pair"></div>
    <div class="cards" id="cards"></div>
  </section>
</div>

<div class="ckwrap">
  <div class="wrap">
    <div class="ck-lead">
      <span class="badge-new">Verified inside the checkout</span>
      <span class="ck-when">checkout documents read __CKDATE__</span>
      <h2>What these merchants actually put in their checkout</h2>
      <p>Everything above is evidence of what a merchant <em>runs</em> &mdash; read off their
         storefront. These __CKN__ stores are different: each one was walked into a live
         <code>/checkouts/&hellip;</code> session and the checkout document itself was read, so the
         app, the block and the checkout step are all known. __CKB__ blocks in total. This is the
         section to open when a merchant asks &ldquo;what would <em>my</em> checkout look like?&rdquo;</p>
    </div>
    <div class="ck-chips" id="ck-chips"><span class="tb-lbl">Element</span></div>
    <div class="ck-grid" id="ck-grid"></div>
    <div class="ck-note">
      <b>Read this the right way.</b> A row proves the extension is installed and registered
      for that step &mdash; not that it renders for every shopper, since apps apply their own
      conditions and some merchants A/B test placement. Where a block reports
      <b>App-placed</b>, the app chooses its own position at runtime. Blocks on the
      thank-you and order-status pages are excluded on purpose: those are available on every
      plan except Starter, so they are not evidence of Plus. Everything listed here sits on
      the information, shipping or payment steps, which is the part Plus opens up.
    </div>
  </div>
</div>

<div class="toolbar">
  <div class="wrap">
    <div class="tb-row">
      <div class="search-box">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
        <input id="q" type="text" placeholder="Search brand, industry or app&hellip;" autocomplete="off" spellcheck="false">
      </div>
      <span class="tb-lbl">Type</span>
      <div class="seg" id="seg-type"></div>
      <span class="tb-lbl">Sort</span>
      <div class="seg" id="seg-sort">
        <button data-sort="coverage" class="on">Coverage</button>
        <button data-sort="name">A&ndash;Z</button>
      </div>
    </div>
    <div class="chips" id="chips"><span class="tb-lbl">Element</span></div>
  </div>
</div>

<div class="wrap">
  <div class="count-line" id="count"></div>
  <div id="lib"></div>

  <section class="sec">
    <div class="sec-hd"><div><h2>Method &amp; exclusions</h2></div></div>
    <details class="meth">
      <summary>How each entry was verified</summary>
      <div class="meth-bd">
        <p><b>The link works.</b> For every store we read <code>/products.json</code>, picked an
        available, non-gift-card variant, built <code>https://&lt;domain&gt;/cart/&lt;variant&gt;:1</code>,
        followed it with a cookie jar, and kept the entry only if the browser ended up on a live
        <code>/checkouts/&hellip;</code> URL. __PROBED__ domains were tested; __VERIFIED__ passed and are
        listed above. The rest were removed rather than badged.</p>
        <p><b>What the elements mean.</b> Evidence is the app extensions and scripts a store actually
        loads, plus which <code>/policies/*</code> pages it publishes, plus real bundle/kit SKUs in its
        catalogue. That tells you <em>what the merchant runs</em>. It does not prove <em>where</em> they
        place it &mdash; app presence is a strong hint, not a guarantee of a checkout block. Click through
        and confirm before you screenshare; the tick box on each row is there to record that.</p>
        <p><b>Known blind spot.</b> Headless and custom storefronts (Gymshark, SKIMS) don't expose their
        app scripts this way, so they score low here while often running rich checkouts. Low coverage
        means "we couldn't see it", not "they don't have it".</p>
        <p><b>Freshness.</b> Variant IDs go out of stock. Re-run the probe if a link starts landing on a
        homepage or cart page &mdash; that is the signature of a dead variant.</p>
      </div>
    </details>
    <details class="meth">
      <summary>Removed &mdash; not on Shopify (__NNOTSHOP__)</summary>
      <div class="meth-bd">
        <p>These were in the old library. They serve a 200 with no Shopify signature in headers or
        markup &mdash; different platform. Don't put them back.</p>
        <div class="domlist">__NOTSHOP__</div>
      </div>
    </details>
    <details class="meth">
      <summary>Removed &mdash; couldn't verify (__NBLOCKED__)</summary>
      <div class="meth-bd">
        <p>Bot protection blocked the check (403/429) or no public <code>products.json</code>, so no
        working link could be built. Some are on Shopify; they're held back rather than shipped broken.</p>
        <div class="domlist">__BLOCKED__</div>
      </div>
    </details>
  </section>

  <footer>
    Internal sales reference &middot; generated __DATE_H__ &middot; evidence gathered from public storefronts.<br>
    <kbd>/</kbd> search &nbsp;&middot;&nbsp; <kbd>Esc</kbd> clear &nbsp;&middot;&nbsp; <kbd>A</kbd> expand or collapse all
  </footer>
</div>

<script>
const DATA = __DATA__;
const EL = DATA.elements, EXTRA = DATA.extra;
const ELKEYS = EL.map(e => e[0]), ELNAME = Object.fromEntries(EL.concat(EXTRA));
const TYPES = [['all','All'],['b2c','B2C'],['b2b','B2B'],['subscription','Subscription'],
               ['regulated','Regulated'],['luxury','Luxury']];
const EXT_ICON = '<svg width="10" height="10" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';
const TICK = '<svg width="9" height="9" fill="none" stroke="#fff" stroke-width="3" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>';

let type = 'all', el = null, sort = 'coverage', q = '';
const SEEN_KEY = 'ckl.seen.v2';
let seen = new Set();
try { seen = new Set(JSON.parse(localStorage.getItem(SEEN_KEY) || '[]')); } catch (e) {}
const saveSeen = () => { try { localStorage.setItem(SEEN_KEY, JSON.stringify([...seen])); } catch (e) {} };

const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const link = b => `https://${b.u}/cart/${b.v}:1`;

function hl(t, needle) {
  t = esc(t);
  if (!needle) return t;
  const i = t.toLowerCase().indexOf(needle);
  return i < 0 ? t : t.slice(0, i) + '<mark>' + t.slice(i, i + needle.length) + '</mark>' + t.slice(i + needle.length);
}
function meter(b, sm) {
  return `<div class="meter${sm ? ' sm' : ''}">` + ELKEYS.map(k =>
    `<i class="${b.ev[k] ? 'on' : ''}" title="${esc(ELNAME[k])}${b.ev[k] ? ': ' + esc(b.ev[k].join(', ')) : ' — no evidence found'}"></i>`
  ).join('') + '</div>';
}
/* App names that only restate the element label, or are derived evidence
   rather than a product, add noise — the meter already says the element is
   covered, so keep them out of the app line. */
const GENERIC = /^(trust badges|free shipping bar|shipping bar|gift wrap|gift options|giftnote|bundler)$/i;
const DERIVED = /(bundle\/kit SKUs|published)$/;
function appNames(b) {
  const out = [];
  for (const k of ELKEYS.concat(EXTRA.map(e => e[0]))) {
    for (const n of (b.ev[k] || [])) {
      if (GENERIC.test(n) || DERIVED.test(n)) continue;
      if (!out.includes(n)) out.push(n);
    }
  }
  return out;
}
function pills(b) {
  return '<div class="pills">' + EL.map(([k, l]) =>
    `<span class="pill${b.ev[k] ? '' : ' off'}" title="${b.ev[k] ? esc(b.ev[k].join(', ')) : 'no evidence found'}">${esc(l)}</span>`
  ).join('') + '</div>';
}
function appLine(b, needle, max) {
  const a = appNames(b);
  if (!a.length) return '<span class="none">no named apps detected</span>';
  const shown = a.slice(0, max), rest = a.length - shown.length;
  return shown.map(x => hl(x, needle)).join(' &middot; ')
         + (rest ? ` <span style="color:var(--ink-4)">+${rest}</span>` : '');
}
function matches(b, ind) {
  if (el && !b.ev[el]) return false;
  if (!q) return true;
  if (b.n.toLowerCase().includes(q) || b.u.includes(q) || ind.name.toLowerCase().includes(q)) return true;
  return Object.values(b.ev).some(v => v.some(x => x.toLowerCase().includes(q)));
}

function renderCards() {
  document.getElementById('cards').innerHTML = DATA.top.map(b => `
    <article class="card">
      <div class="card-hd">
        <div><div class="nm">${esc(b.n)}</div><div class="ind">${esc(b.ind)}</div></div>
        <span class="score">${b.c}/8</span>
      </div>
      ${pills(b)}
      <div class="appline"><b>Running</b><br>${appLine(b, '', 6)}</div>
      <a class="go" href="${link(b)}" target="_blank" rel="noopener">Open checkout ${EXT_ICON}</a>
    </article>`).join('');

  const p = DATA.pair;
  document.getElementById('pair').innerHTML = `
    <div class="pair-txt">
      <h4>No single merchant demos all eight</h4>
      <p>The best real-world example is <b>7 of 8</b>. To cover the full list on one call, pair
         <b>${esc(p.a.n)}</b> (${p.a.c}/8 &mdash; ${esc(p.aOnly)}) with
         <b>${esc(p.b.n)}</b> (${p.b.c}/8 &mdash; ${esc(p.bOnly)}). Together they hit all eight.</p>
    </div>
    <div class="pair-go">
      <a class="go-sm" href="${link(p.a)}" target="_blank" rel="noopener">${esc(p.a.n)} ${EXT_ICON}</a>
      <a class="go-sm" href="${link(p.b)}" target="_blank" rel="noopener">${esc(p.b.n)} ${EXT_ICON}</a>
    </div>`;
}

/* ---- checkout-level verified section ---------------------------------------
   Separate renderer and separate state from render() below: this data came out
   of live checkout documents, not the storefront, so the two must never be
   filtered or counted together. */
const CK = DATA.ck, CKNAME = Object.fromEntries(CK.elements);
let ckEl = null;

/* Only five blocks fit on a card, so they must be the ones worth pointing at.
   Cross-border plumbing (Global-e duties, address validation, alternative payment
   methods) is real but invisible on a call, and it outnumbers the merchandising
   blocks on several of these stores — Mack Weldon would show four Global-e rows
   before its cashback block. Merchandising leads; the rest falls into +N more. */
const CKMERCH = ['trust', 'reviews', 'shipbar', 'addons', 'gift', 'loyalty', 'fields', 'protect'];
const ckWeight = b => (b.e.some(k => CKMERCH.includes(k)) ? 0 : 1);
const ckSort = (rows, first) => rows.slice().sort((x, y) =>
  (first ? (y.e.includes(first) ? 1 : 0) - (x.e.includes(first) ? 1 : 0) : 0)
  || ckWeight(x) - ckWeight(y));

/* Aftersell and Rebuy register one widget on every step, which spills eight zone
   chips per block and buries the app name. Three zones is enough to say where to
   look; past six the honest statement is that the app is registered everywhere. */
function zones(z) {
  if (z.length >= 6) return `<span>registered on ${z.length} steps</span>`;
  const shown = z.slice(0, 3), rest = z.length - shown.length;
  return shown.map(x => `<span>${esc(x)}</span>`).join('')
    + (rest ? `<span style="background:none;color:var(--ink-4)">+${rest}</span>` : '');
}

function ckBlocks(s, limit) {
  const shown = s.ck.slice(0, limit), rest = s.ck.length - shown.length;
  return shown.map(b => `
    <div class="ck-b">
      <span class="bh">${esc(b.h === '—' ? b.a : b.h)}</span>
      ${b.h === '—' || !b.a || b.a === '—' ? '' : `<span class="ba"> &middot; ${esc(b.a)}</span>`}
      <span class="ck-z">${zones(b.z)}</span>
    </div>`).join('')
    + (rest ? `<div class="ck-more">+${rest} more block${rest === 1 ? '' : 's'}</div>` : '');
}

function renderCk() {
  document.getElementById('ck-chips').innerHTML = '<span class="tb-lbl">Element</span>'
    + `<button class="ck-chip${ckEl ? '' : ' on'}" data-ck="">All</button>`
    + CK.elements.filter(([k]) => CK.stores.some(s => s.el.includes(k)))
        .map(([k, l]) => `<button class="ck-chip${ckEl === k ? ' on' : ''}" data-ck="${k}">`
          + `${esc(l)} <span style="opacity:.6">${CK.stores.filter(s => s.el.includes(k)).length}</span></button>`)
        .join('');

  const list = ckEl ? CK.stores.filter(s => s.el.includes(ckEl)) : CK.stores;
  document.getElementById('ck-grid').innerHTML = list.map((s, i) => {
    /* Re-order so the block matching the active filter leads the card — on a call
       you clicked "Reviews & ratings" to see reviews, not the store's first block. */
    const rows = { ...s, ck: ckSort(s.ck, ckEl) };
    return `
    <article class="ck-card${!ckEl && i < 3 ? ' hero' : ''}">
      <div class="ck-hd">
        <div><div class="ck-nm">${esc(s.n)}</div><div class="ck-cat">${esc(s.cat)} &middot; ${esc(s.u)}</div></div>
        <span class="ck-n">${s.ck.length} block${s.ck.length === 1 ? '' : 's'}</span>
      </div>
      <div class="ck-blocks">${ckBlocks(rows, 5)}</div>
      <a class="go" href="https://${s.u}/cart/${s.v}:1" target="_blank" rel="noopener">Open checkout ${EXT_ICON}</a>
    </article>`;
  }).join('');

  document.querySelectorAll('#ck-chips .ck-chip').forEach(b => b.onclick = () => {
    ckEl = b.dataset.ck || null;
    renderCk();
  });
}

function render() {
  const groups = DATA.industries.map(ind => {
    if (type !== 'all' && !ind.tags.includes(type)) return null;
    const bs = ind.brands.filter(b => matches(b, ind));
    if (!bs.length) return null;
    const sorted = bs.slice().sort(sort === 'name'
      ? (x, y) => x.n.localeCompare(y.n)
      : (x, y) => y.c - x.c || x.n.localeCompare(y.n));
    return { ind, bs: sorted };
  }).filter(Boolean);

  const nB = groups.reduce((a, g) => a + g.bs.length, 0);
  document.getElementById('count').innerHTML =
    `<strong>${nB}</strong> checkout${nB === 1 ? '' : 's'} across <strong>${groups.length}</strong> ` +
    `industr${groups.length === 1 ? 'y' : 'ies'}` +
    (el ? ` &middot; showing only stores with evidence of <strong>${esc(ELNAME[el])}</strong>` : '') +
    (q ? ` &middot; matching &ldquo;<strong>${esc(q)}</strong>&rdquo;` : '');

  const lib = document.getElementById('lib');
  if (!groups.length) {
    lib.innerHTML = `<div class="empty">Nothing matches that filter. <button class="btn-copy" onclick="window.__reset()">Reset filters</button></div>`;
    return;
  }
  const openAll = !!(q || el);
  lib.innerHTML = groups.map(g => `
    <section class="grp${openAll ? ' open' : ''}">
      <div class="grp-hd">
        <span class="grp-nm">${hl(g.ind.name, q)}</span>
        ${g.ind.tags.map(t => `<span class="tag ${t}">${esc(t === 'b2c' ? 'B2C' : t === 'b2b' ? 'B2B' : t)}</span>`).join('')}
        <span class="grp-meta">
          <span class="grp-n">${g.bs.length} store${g.bs.length === 1 ? '' : 's'}</span>
          <svg class="chev" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.6" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
        </span>
      </div>
      <div class="grp-bd">
        ${g.bs.map(b => `
          <div class="row">
            <button class="seen ${seen.has(b.u) ? 'on' : ''}" data-seen="${esc(b.u)}"
                    title="Mark as personally confirmed">${TICK}</button>
            <div><div class="nm">${hl(b.n, q)}</div><div class="dom">${hl(b.u, q)}</div></div>
            <div class="mwrap"><span class="sc">${b.c}/8</span>${meter(b, true)}</div>
            <div class="ev">${appLine(b, q, 5)}</div>
            <a class="go-sm" href="${link(b)}" target="_blank" rel="noopener">Open checkout ${EXT_ICON}</a>
          </div>`).join('')}
      </div>
    </section>`).join('');
}

/* ---- chrome ---- */
document.getElementById('seg-type').innerHTML =
  TYPES.map(([v, l]) => `<button data-type="${v}"${v === 'all' ? ' class="on"' : ''}>${l}</button>`).join('');

const counts = {};
DATA.industries.forEach(i => i.brands.forEach(b => ELKEYS.forEach(k => { if (b.ev[k]) counts[k] = (counts[k] || 0) + 1; })));
document.getElementById('chips').insertAdjacentHTML('beforeend',
  EL.map(([k, l]) => `<button class="chip" data-el="${k}">${l}<span class="n">${counts[k] || 0}</span></button>`).join(''));

document.getElementById('seg-type').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  type = b.dataset.type;
  document.querySelectorAll('#seg-type button').forEach(x => x.classList.toggle('on', x === b));
  render();
});
document.getElementById('seg-sort').addEventListener('click', e => {
  const b = e.target.closest('button'); if (!b) return;
  sort = b.dataset.sort;
  document.querySelectorAll('#seg-sort button').forEach(x => x.classList.toggle('on', x === b));
  render();
});
document.getElementById('chips').addEventListener('click', e => {
  const b = e.target.closest('.chip'); if (!b) return;
  el = (el === b.dataset.el) ? null : b.dataset.el;
  document.querySelectorAll('.chip').forEach(x => x.classList.toggle('on', el === x.dataset.el));
  render();
});
document.getElementById('q').addEventListener('input', e => { q = e.target.value.toLowerCase().trim(); render(); });

document.getElementById('lib').addEventListener('click', e => {
  const s = e.target.closest('.seen');
  if (s) {
    const d = s.dataset.seen;
    seen.has(d) ? seen.delete(d) : seen.add(d);
    s.classList.toggle('on', seen.has(d));
    saveSeen();
    return;
  }
  const hd = e.target.closest('.grp-hd');
  if (hd) hd.closest('.grp').classList.toggle('open');
});

document.getElementById('copy-addr').addEventListener('click', async e => {
  const btn = e.currentTarget, txt = document.getElementById('addr-txt').textContent;
  try { await navigator.clipboard.writeText(txt); } catch (err) {
    const t = document.createElement('textarea');
    t.value = txt; document.body.appendChild(t); t.select();
    try { document.execCommand('copy'); } catch (e2) {}
    t.remove();
  }
  btn.textContent = 'Copied'; btn.classList.add('done');
  setTimeout(() => { btn.textContent = 'Copy test address'; btn.classList.remove('done'); }, 1600);
});

window.__reset = () => {
  q = ''; el = null; type = 'all';
  document.getElementById('q').value = '';
  document.querySelectorAll('.chip').forEach(x => x.classList.remove('on'));
  document.querySelectorAll('#seg-type button').forEach(x => x.classList.toggle('on', x.dataset.type === 'all'));
  render();
};

document.addEventListener('keydown', e => {
  const typing = /^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName);
  if (e.key === '/' && !typing) { e.preventDefault(); document.getElementById('q').focus(); }
  if (e.key === 'Escape') { document.getElementById('q').blur(); window.__reset(); }
  if ((e.key === 'a' || e.key === 'A') && !typing) {
    const gs = [...document.querySelectorAll('.grp')];
    const anyClosed = gs.some(g => !g.classList.contains('open'));
    gs.forEach(g => g.classList.toggle('open', anyClosed));
  }
});

document.getElementById('m1').textContent = DATA.counts.verified;
document.getElementById('m2').textContent = DATA.industries.length;
document.getElementById('m4').textContent = DATA.counts.probed - DATA.counts.verified;
renderCards();
renderCk();
render();
</script>
</body>
</html>
"""

d = __import__("datetime").date.fromisoformat(DATA["generated"])
date_h = d.strftime("%-d %b %Y")
ex = DATA["excluded"]
html = (TPL
        .replace("__DATA__", json.dumps(DATA, separators=(",", ":")))
        .replace("__DATE_H__", date_h)
        .replace("__PROBED__", str(DATA["counts"]["probed"]))
        .replace("__VERIFIED__", str(DATA["counts"]["verified"]))
        .replace("__NNOTSHOP__", str(len(ex["notShopify"])))
        .replace("__NBLOCKED__", str(len(ex["blocked"])))
        .replace("__NOTSHOP__", "".join(f"<span>{x}</span>" for x in ex["notShopify"]))
        # the ck sweep is newer than the storefront sweep above, so it carries its
        # own date — the mast's "verified" stamp does not cover it
        .replace("__CKDATE__", __import__("datetime").date.today().strftime("%-d %b %Y"))
        .replace("__CKN__", str(DATA["ck"]["counts"]["stores"]))
        .replace("__CKB__", str(DATA["ck"]["counts"]["blocks"]))
        .replace("__BLOCKED__", "".join(f"<span>{x}</span>" for x in ex["blocked"])))

open(OUT, "w", encoding="utf-8").write(html)
print("wrote", OUT, len(html), "bytes")
