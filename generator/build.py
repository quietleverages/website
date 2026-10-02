#!/usr/bin/env python3
"""Quiet Leverages landing page generator.
Usage: python3 build.py data/<slug>.json  -> out/<slug>.html
Image paths in "previews" are read and embedded as data: URIs.
"""
import json, sys, html, base64, os, mimetypes

STORE = "https://quietleverages.gumroad.com/l/"   # CONFIRM store subdomain with owner
E = lambda s: html.escape(str(s), quote=True)

CSS = r"""
:root{
  --bg:#f5f6f8; --surface:#ffffff; --ink:#18213a; --muted:#566074; --rule:#dce0e8; --band:#eaedf3;
  --accent:#2f6fa8; --accent-ink:#ffffff; --tint:#e8f0f8;
  --btn-bg:#18213a; --btn-fg:#ffffff;
  --display:"Fraunces", Georgia, "Times New Roman", serif;
  --body:"Red Hat Text", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono:"Red Hat Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
.p-work{--accent:#2f6fa8;--tint:#e8f0f8}
.p-money{--accent:#8a6d14;--tint:#f5efdd}
.p-people{--accent:#c0532f;--tint:#f9e9e3}
.p-reset{--accent:#5b4a8a;--tint:#eeebf6}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121520; --surface:#1a1f2d; --ink:#e7e9ef; --muted:#9aa2b5; --rule:#2c3244; --band:#232a3a;
  --accent-ink:#121520; --btn-bg:#e7e9ef; --btn-fg:#121520; color-scheme:dark}
  :root:not([data-theme="light"]) .p-work{--accent:#79aee0;--tint:#1c2a3d}
  :root:not([data-theme="light"]) .p-money{--accent:#e0bf5c;--tint:#2e2916}
  :root:not([data-theme="light"]) .p-people{--accent:#f0967a;--tint:#35221c}
  :root:not([data-theme="light"]) .p-reset{--accent:#b3a3e6;--tint:#262238}}
:root[data-theme="dark"]{
  --bg:#121520; --surface:#1a1f2d; --ink:#e7e9ef; --muted:#9aa2b5; --rule:#2c3244; --band:#232a3a;
  --accent-ink:#121520; --btn-bg:#e7e9ef; --btn-fg:#121520; color-scheme:dark}
:root[data-theme="dark"] .p-work{--accent:#79aee0;--tint:#1c2a3d}
:root[data-theme="dark"] .p-money{--accent:#e0bf5c;--tint:#2e2916}
:root[data-theme="dark"] .p-people{--accent:#f0967a;--tint:#35221c}
:root[data-theme="dark"] .p-reset{--accent:#b3a3e6;--tint:#262238}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.6;padding-inline:20px;padding-block:0 0}
a{color:inherit;text-underline-offset:3px}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:3px;border-radius:4px}
.wrap{max-width:1040px;margin:0 auto}
.narrow{max-width:700px;margin:0 auto}
h1,h2,h3{font-family:var(--display);font-weight:600;line-height:1.12;margin:0;text-wrap:balance;letter-spacing:-.01em}
h1{font-size:clamp(2.2rem,5.4vw,3.6rem)}
h2{font-size:clamp(1.65rem,3.4vw,2.35rem)}
h3{font-size:1.2rem;line-height:1.25}
p{margin:0}
.eyebrow{font-family:var(--mono);font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:500}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:54px;padding:14px 28px;border-radius:10px;background:var(--btn-bg);color:var(--btn-fg);font-weight:700;font-size:1.05rem;text-decoration:none;border:2px solid var(--btn-bg);transition:transform .15s ease,box-shadow .15s ease}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(24,33,58,.22)}
.btn.accent{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.btn.ghost{background:transparent;color:var(--ink);border-color:var(--rule)}
.btn.ghost:hover{border-color:var(--ink);box-shadow:none}
.btn small{font-weight:500;opacity:.85;font-size:.88rem}
/* top bar */
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:20;background:var(--bg);border-bottom:1px solid var(--rule);margin-inline:-20px;padding:10px 20px}
.bar .wrap{display:flex;align-items:center;justify-content:space-between;gap:14px}
.brand{font-family:var(--display);font-weight:600;font-size:1.05rem;text-decoration:none;white-space:nowrap}
.brand span{color:var(--accent)}
.bar .btn{min-height:42px;padding:8px 18px;font-size:.95rem}
.bar .barprice{font-family:var(--mono);font-size:.9rem;color:var(--muted);margin-right:12px}
.barright{display:flex;align-items:center}
@media (max-width:520px){.bar .barprice{display:none}.brand{font-size:.95rem}}
/* hero */
.hero{padding-block:clamp(40px,7vw,84px) clamp(40px,6vw,72px);display:grid;grid-template-columns:1.1fr .9fr;gap:clamp(28px,5vw,64px);align-items:center}
.hero > *{min-width:0}
.hero h1{margin-block:14px 18px}
.hero .sub{font-size:1.2rem;color:var(--muted);max-width:34em}
.cta-row{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:28px}
.micro{font-size:.9rem;color:var(--muted);margin-top:14px}
.micro b{color:var(--ink)}
.price-tag{display:inline-flex;align-items:baseline;gap:8px;font-family:var(--display);font-size:1.7rem;font-weight:600;margin-right:6px}
.price-tag s{font-size:1.05rem;color:var(--muted);font-weight:400}
.cover{position:relative;border-radius:14px;background:var(--tint);padding:clamp(18px,3vw,30px);border:1px solid var(--rule)}
.cover .stack{position:relative;display:grid;gap:0}
.cover img{display:block;width:100%;height:auto;border-radius:6px;border:1px solid var(--rule);background:#fff;box-shadow:0 14px 34px rgba(24,33,58,.18)}
.cover img + img{display:none}
.cover .tag{position:absolute;right:14px;bottom:-14px;background:var(--accent);color:var(--accent-ink);font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;padding:7px 12px;border-radius:6px}
.typecover{aspect-ratio:3/4;max-height:460px;margin-inline:auto;border-radius:6px;background:var(--surface);border:1px solid var(--rule);box-shadow:0 14px 34px rgba(24,33,58,.14);padding:clamp(18px,3vw,30px);display:flex;flex-direction:column;justify-content:space-between}
.typecover .t{font-family:var(--display);font-weight:600;font-size:clamp(1.7rem,3.4vw,2.5rem);line-height:1.05}
.typecover .rule{height:6px;width:64px;background:var(--accent);border-radius:3px}
.typecover .by{font-family:var(--mono);font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
@media (max-width:820px){.hero{grid-template-columns:1fr}.cover{order:-1;max-width:420px;width:100%;margin-inline:auto}}
/* sections */
section{padding-block:clamp(44px,7vw,84px)}
section.alt{background:var(--band);margin-inline:-20px;padding-inline:20px}
.sechead{max-width:700px;margin-bottom:32px;display:grid;gap:12px}
.sechead p{color:var(--muted);font-size:1.08rem}
/* UVP */
.uvp{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-block:1px solid var(--rule);padding-block:0}
.uvp > div{padding:26px 24px;display:grid;gap:8px;align-content:start;min-width:0}
.uvp > div + div{border-left:1px solid var(--rule)}
.uvp h3{font-size:1.1rem}
.uvp p{color:var(--muted);font-size:.98rem}
@media (max-width:760px){.uvp{grid-template-columns:1fr}.uvp > div + div{border-left:0;border-top:1px solid var(--rule)}}
/* problem */
.problem{display:grid;grid-template-columns:auto 1fr;gap:clamp(20px,4vw,48px);align-items:center}
.bignum{font-family:var(--display);font-weight:600;font-size:clamp(4rem,11vw,7.5rem);line-height:.9;color:var(--accent);letter-spacing:-.03em}
.problem p{font-size:1.2rem;max-width:30em}
.src{display:block;font-size:.8rem;color:var(--muted);margin-top:10px;font-family:var(--mono)}
@media (max-width:600px){.problem{grid-template-columns:1fr}}
/* benefits */
.benefits{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:18px}
.benefit{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:24px;display:grid;gap:8px;align-content:start;min-width:0}
.benefit .chk{width:30px;height:30px;border-radius:8px;background:var(--tint);color:var(--accent);display:grid;place-items:center;margin-bottom:6px}
.benefit p{color:var(--muted);font-size:.98rem}
/* inside list */
.inside{display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,5vw,56px);align-items:start}
.inside > *{min-width:0}
.inside ul{list-style:none;margin:0;padding:0;display:grid;gap:0}
.inside li{padding:14px 0 14px 34px;border-bottom:1px solid var(--rule);position:relative}
.inside li::before{content:"";position:absolute;left:4px;top:21px;width:14px;height:8px;border-left:3px solid var(--accent);border-bottom:3px solid var(--accent);transform:rotate(-45deg) scale(.9)}
.inside li b{font-weight:700}
@media (max-width:820px){.inside{grid-template-columns:1fr}}
.gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));gap:14px}
.gallery figure{margin:0;display:grid;gap:8px}
.gallery img{width:100%;height:auto;display:block;border-radius:6px;border:1px solid var(--rule);background:#fff;box-shadow:0 8px 20px rgba(24,33,58,.12)}
.gallery figcaption{font-family:var(--mono);font-size:12px;color:var(--muted);letter-spacing:.04em}
/* steps */
.steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:18px;counter-reset:s}
.steps li{counter-increment:s;border-top:3px solid var(--accent);padding-top:16px;display:grid;gap:6px;align-content:start}
.steps li::before{content:"Step " counter(s);font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.steps p{color:var(--muted);font-size:.97rem}
/* for who */
.forwho{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.forwho > div{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:24px;min-width:0}
.forwho h3{margin-bottom:12px}
.forwho ul{margin:0;padding:0;list-style:none;display:grid;gap:10px}
.forwho li{padding-left:24px;position:relative;font-size:.98rem}
.forwho .yes li::before{content:"+";position:absolute;left:0;color:var(--accent);font-weight:700;font-family:var(--mono)}
.forwho .no li::before{content:"\2013";position:absolute;left:0;color:var(--muted);font-weight:700;font-family:var(--mono)}
@media (max-width:700px){.forwho{grid-template-columns:1fr}}
/* proof */
.proofgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:18px}
.proofcard{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:24px;display:grid;gap:8px;align-content:start;min-width:0}
.proofcard .n{font-family:var(--display);font-size:2.6rem;font-weight:600;color:var(--accent);line-height:1}
.proofnote{margin-top:22px;padding:22px 24px;border-radius:12px;background:var(--tint);font-family:var(--display);font-size:1.15rem;line-height:1.4}
.proofnote span{display:block;font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-top:8px}
/* offer */
.offer{background:var(--ink);color:var(--bg);border-radius:18px;padding:clamp(28px,5vw,56px);display:grid;grid-template-columns:1.2fr .8fr;gap:clamp(24px,4vw,48px);align-items:center}
.offer > *{min-width:0}
.offer h2{color:var(--bg)}
.offer p{color:var(--bg);opacity:.82;margin-top:12px}
.offer ul{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:8px;font-size:.98rem}
.offer li{padding-left:24px;position:relative;opacity:.92}
.offer li::before{content:"";position:absolute;left:2px;top:.5em;width:11px;height:6px;border-left:2px solid var(--bg);border-bottom:2px solid var(--bg);transform:rotate(-45deg)}
.buybox{background:var(--bg);color:var(--ink);border-radius:14px;padding:26px;display:grid;gap:14px;text-align:center}
.buybox .price-tag{justify-content:center;font-size:2.4rem;margin:0}
.buybox .btn{width:100%}
.buybox .micro{margin:0}
.offer .hl{--accent:var(--accent)}
@media (max-width:820px){.offer{grid-template-columns:1fr}}
/* faq */
.faq{display:grid;gap:0;border-top:1px solid var(--rule)}
details{border-bottom:1px solid var(--rule)}
summary{cursor:pointer;list-style:none;padding:20px 40px 20px 0;font-weight:700;font-size:1.08rem;position:relative}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";position:absolute;right:6px;top:50%;transform:translateY(-50%);font-family:var(--mono);font-size:1.5rem;color:var(--accent);font-weight:400}
details[open] summary::after{content:"\2013"}
details p{padding:0 0 22px;color:var(--muted);max-width:42em}
/* related */
.related{display:flex;flex-wrap:wrap;gap:18px;align-items:center;justify-content:space-between;border:1px solid var(--rule);border-radius:12px;padding:22px 24px;background:var(--surface)}
.related > div{min-width:0;flex:1 1 280px}
.related .eyebrow{display:block;margin-bottom:6px}
/* final */
.final{text-align:center;display:grid;gap:18px;justify-items:center}
.final p{color:var(--muted);max-width:32em}
footer{border-top:1px solid var(--rule);margin-inline:-20px;padding:32px 20px 40px;font-size:.85rem;color:var(--muted)}
footer .wrap{display:grid;gap:10px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""

def img_uri(path):
    mt = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        return f"data:{mt};base64," + base64.b64encode(f.read()).decode()

CHK = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def build(d):
    slug = d["slug"]
    url = d.get("url") or (STORE + slug)
    free = d.get("free", False)
    price = d["price"]
    cta = d.get("cta") or ("Get it free" if free else f"Get it for {price}")
    previews = [img_uri(p) for p in d.get("previews", []) if os.path.exists(p)]
    labels = d.get("preview_labels", [])
    pillar = d.get("pillar", "work")

    def price_html():
        old = f"<s>{E(d['priceOld'])}</s>" if d.get("priceOld") else ""
        return f'<span class="price-tag">{old}{E(price)}</span>'

    # hero cover
    if previews:
        cover = f'<div class="cover"><div class="stack"><img src="{previews[0]}" alt="{E(d.get("preview_alts",[d["title"]+" first page"])[0])}"></div><span class="tag">{E(d.get("covertag","Real page from the product"))}</span></div>'
    else:
        cover = f'<div class="cover"><div class="typecover"><div class="rule"></div><div class="t">{E(d["title"])}</div><div class="by">Quiet Leverages</div></div></div>'

    uvp = "".join(f'<div><h3>{E(u["h"])}</h3><p>{E(u["p"])}</p></div>' for u in d["uvp"])
    benefits = "".join(f'<div class="benefit"><div class="chk">{CHK}</div><h3>{E(b["h"])}</h3><p>{E(b["p"])}</p></div>' for b in d["benefits"])
    inside = "".join(f'<li>{b}</li>' for b in d["inside"])  # allow <b> in trusted copy
    gal = ""
    if len(previews) > 1:
        figs = ""
        for i, u in enumerate(previews[1:], 1):
            lab = labels[i] if i < len(labels) else ""
            figs += f'<figure><img loading="lazy" src="{u}" alt="{E(lab or d["title"]+" page "+str(i+1))}"><figcaption>{E(lab)}</figcaption></figure>'
        gal = f'<div class="gallery" style="margin-top:36px">{figs}</div>'

    problem = ""
    if d.get("stat"):
        s = d["stat"]
        problem = f'''<section><div class="wrap problem"><div class="bignum">{E(s["n"])}</div><div><p>{E(s["t"])}</p><span class="src">{E(s["src"])}</span></div></div></section>'''

    steps = ""
    if d.get("steps"):
        st = d["steps"]
        items = "".join(f'<li><h3>{E(i["h"])}</h3><p>{E(i["p"])}</p></li>' for i in st["items"])
        steps = f'''<section class="alt"><div class="wrap"><div class="sechead"><span class="eyebrow">{E(st.get("eyebrow","How it works"))}</span><h2>{E(st["title"])}</h2></div><ol class="steps">{items}</ol></div></section>'''

    forwho = ""
    if d.get("forwho"):
        fw = d["forwho"]
        y = "".join(f"<li>{E(i)}</li>" for i in fw["yes"])
        n = "".join(f"<li>{E(i)}</li>" for i in fw["no"])
        forwho = f'''<section><div class="wrap"><div class="sechead"><span class="eyebrow">Fit check</span><h2>{E(fw.get("title","Is this for you?"))}</h2></div><div class="forwho"><div class="yes"><h3>Use this if</h3><ul>{y}</ul></div><div class="no"><h3>Skip it if</h3><ul>{n}</ul></div></div></div></section>'''

    pr = d.get("proof", {})
    cards = "".join(f'<div class="proofcard"><div class="n">{E(s["n"])}</div><p>{E(s["t"])}</p><span class="src">{E(s["src"])}</span></div>' for s in pr.get("stats", []))
    note = ""
    if pr.get("note"):
        note = f'<div class="proofnote">{E(pr["note"])}<span>{E(pr.get("noteBy","Quiet Leverages house rule"))}</span></div>'
    proof = f'''<section class="alt"><div class="wrap"><div class="sechead"><span class="eyebrow">Why we built it</span><h2>{E(pr.get("title","The numbers behind the problem"))}</h2></div><div class="proofgrid">{cards}</div>{note}</div></section>'''

    offer_items = "".join(f"<li>{E(i)}</li>" for i in d.get("offer", {}).get("items", []))
    of = d.get("offer", {})
    offer = f'''<section id="get"><div class="wrap"><div class="offer"><div><span class="eyebrow" style="color:var(--bg);opacity:.7">{E(of.get("eyebrow","What you get"))}</span><h2 style="margin-top:10px">{E(of.get("h","Start today"))}</h2><p>{E(of.get("p",""))}</p><ul>{offer_items}</ul></div><div class="buybox">{price_html()}<a class="btn accent" href="{E(url)}" target="_blank" rel="noopener">{E(cta)}</a><p class="micro">{E(d.get("priceNote","Instant download on Gumroad."))}</p></div></div></div></section>'''

    faq = "".join(f'<details><summary>{E(f["q"])}</summary><p>{E(f["a"])}</p></details>' for f in d["faq"])

    related = ""
    if d.get("related"):
        r = d["related"]
        related = f'''<section style="padding-block:0 clamp(44px,7vw,84px)"><div class="wrap"><div class="related"><div><span class="eyebrow">{E(r.get("eyebrow","Next step"))}</span><h3>{E(r["name"])} <span style="font-family:var(--mono);font-size:.9rem;color:var(--muted);font-weight:400">{E(r["price"])}</span></h3><p style="color:var(--muted);margin-top:6px">{E(r["blurb"])}</p></div><a class="btn ghost" href="{E(STORE + r["slug"])}" target="_blank" rel="noopener">See {E(r["name"])}</a></div></div></section>'''

    final = d.get("final", {})
    finalsec = f'''<section><div class="wrap final"><h2>{E(final.get("h", d["h1"]))}</h2><p>{E(final.get("p", d["sub"]))}</p><a class="btn accent" href="{E(url)}" target="_blank" rel="noopener">{E(cta)}</a><p class="micro" style="margin:0">{E(d.get("priceNote","Instant download on Gumroad."))}</p></div></section>'''

    disclaimer = d.get("disclaimer", "General education only.")
    page = f'''<title>{E(d["title"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Red+Hat+Text:wght@400;500;700&family=Red+Hat+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="p-{pillar}">
<header class="bar"><div class="wrap"><a class="brand" href="#top">Quiet <span>Leverages</span></a><div class="barright"><span class="barprice">{E(d["title"])} · {E(price)}</span><a class="btn accent" href="#get">{E("Get it free" if free else "Buy now")}</a></div></div></header>
<main id="top">
<div class="wrap hero"><div><span class="eyebrow">{E(d["eyebrow"])}</span><h1>{E(d["h1"])}</h1><p class="sub">{E(d["sub"])}</p>
<div class="cta-row">{price_html()}<a class="btn accent" href="{E(url)}" target="_blank" rel="noopener">{E(cta)}</a><a class="btn ghost" href="#inside">See what's inside</a></div>
<p class="micro">{d.get("heroMicro","<b>Instant download.</b> Print it or use it on a tablet.")}</p></div>{cover}</div>
<div class="wrap"><div class="uvp">{uvp}</div></div>
{problem}
<section class="alt"><div class="wrap"><div class="sechead"><span class="eyebrow">What it does for you</span><h2>{E(d.get("benefitsTitle","What changes after you fill it in"))}</h2></div><div class="benefits" style="{"grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr))" if len(d["benefits"])==4 else ""}">{benefits}</div></div></section>
<section id="inside"><div class="wrap"><div class="inside"><div class="sechead" style="margin:0"><span class="eyebrow">What's inside</span><h2>{E(d.get("insideTitle","Everything in the download"))}</h2><p>{E(d.get("insideLead",""))}</p></div><ul>{inside}</ul></div>{gal}</div></section>
{steps}
{forwho}
{proof}
{offer}
<section class="alt"><div class="wrap narrow"><div class="sechead"><span class="eyebrow">Questions</span><h2>Before you decide</h2></div><div class="faq">{faq}</div></div></section>
{related}
{finalsec}
</main>
<footer><div class="wrap"><p><b style="color:var(--ink)">Quiet Leverages.</b> We read widely, test each idea against an ordinary week, and keep only what still works on a tired Tuesday.</p><p>{E(disclaimer)}</p></div></footer>
</div>'''
    return page

if __name__ == "__main__":
    src = sys.argv[1]
    d = json.load(open(src))
    out = os.path.join(os.path.dirname(os.path.abspath(src)), "..", "out", d["slug"] + ".html")
    open(out, "w").write(build(d))
    print("wrote", os.path.normpath(out), os.path.getsize(out)//1024, "KB")
