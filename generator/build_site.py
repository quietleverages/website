#!/usr/bin/env python3
"""Quiet Leverages multi-page site generator.
python3 generator/build_site.py  -> ../site/ (index.html, <slug>.html x25, site.css, site.js, reviews.json, img/)
Flat structure on purpose: every link is relative with no '../'.
"""
import re, json, glob, os, shutil, html
from build import CSS as BASE_CSS, E, CHK, STORE

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(ROOT, "..", "site"))
PILLAR = {"work": "Work", "money": "Money", "people": "People", "reset": "Reset"}

SUMMARY = {
 "friendship-audit": "A ten-minute check of who is in your life, who is fading, and three texts to send this week.",
 "stay-or-go": "Should I quit my job? Decide on paper, not at 2 a.m.",
 "what-to-fund-first": "Seven money steps in the order that works. Find your step, automate it, stop second-guessing.",
 "friendship-practice": "One small social drill a day for thirty days, with sixty scripts for the moments that matter.",
 "raise-kit": "Seven days of preparation, one four-line ask, and what to say to every pushback.",
 "couples-money-reset": "Five conversations, one account structure, and a twenty-minute monthly money date.",
 "quiet-reset-2027": "Pick three. Keep the other nine on maintenance. A year planner for your whole life.",
 "career-kit": "Thirteen weeks, one move a week. A career that funds your life instead of draining it.",
 "year-end-review-worksheet": "Close the year honestly before you plan the next one.",
 "12-dimension-life-audit": "Score twelve areas of your life, then choose the three that would lift the rest.",
 "undated-90-day-planner": "One quarter, three priorities, thirteen fifteen-minute Sunday reviews.",
 "52-week-sunday-review-journal": "Fifteen minutes every Sunday, for a whole year.",
 "life-vision-worksheet": "Write the ordinary Tuesday you want in ten years, then work back from it.",
 "ai-prompts-for-life-planning": "Thirty prompts that make an AI a useful planning partner rather than a cheerleader.",
 "60-friendship-scripts": "Sixty ready-to-adapt lines for making and keeping friends as an adult.",
 "30-day-friendship-challenge": "Thirty small social drills, one a day, from saying hello to hosting.",
 "hard-conversation-worksheet": "Prepare the conversation you have been avoiding: facts, story, and what you want afterwards.",
 "small-gathering-planner": "Host a small gathering that people remember, starting with one sentence about why.",
 "monthly-money-date": "A twenty-minute monthly money date for couples, with a timed agenda.",
 "debt-payoff-planner": "Rank your debts by avalanche or snowball and see exactly where the extra money goes.",
 "emergency-and-sinking-funds-tracker": "Size your emergency fund properly and turn predictable costs into small monthly transfers.",
 "grown-up-paperwork-checklist": "The four documents every adult needs, plus a one-page list of where everything is kept.",
 "salary-negotiation-prep": "A seven-day plan to prepare for a raise conversation, plus what to say to every pushback.",
 "career-evidence-log": "Log your work wins every Friday so reviews, raises and interviews start from evidence.",
 "90-day-career-reset": "Thirteen weeks, one career move a week, with honest decision gates along the way.",
}
FREE = ["friendship-audit", "stay-or-go", "what-to-fund-first"]
KITS = ["friendship-practice", "raise-kit", "couples-money-reset", "career-kit"]
FLAG = "quiet-reset-2027"

FACTS = {
 "friendship-audit": [("10 min","to complete"),("25","people you can map"),("3","texts to send this week")],
 "stay-or-go": [("6","criteria scored for stay and go"),("1","decision date set"),("2","formats: PDF and Google Sheet")],
 "what-to-fund-first": [("7","money steps, in order"),("2","automatic transfers sized"),("2","formats: PDF and Google Sheet")],
 "friendship-practice": [("30","daily drills"),("60","ready-to-adapt scripts"),("4","Sunday scorecards")],
 "raise-kit": [("7","days of preparation"),("7","pushbacks, each with a response"),("4","lines in the ask")],
 "couples-money-reset": [("5","conversations with opening lines"),("3","account models"),("20 min","monthly money date")],
 "quiet-reset-2027": [("48","page planner"),("12","life dimensions scored"),("105 min","a week, in total")],
 "career-kit": [("13","weeks, one move each"),("14","scripts"),("5","worksheets")],
 "year-end-review-worksheet": [("12","questions in three parts"),("5","pages"),("3","areas chosen for next year")],
 "12-dimension-life-audit": [("12","dimensions scored 1 to 5"),("4","pages"),("3","areas picked, nine kept on maintenance")],
 "undated-90-day-planner": [("13","weekly review blocks"),("3","priorities per quarter"),("1","Day-90 decision record")],
 "52-week-sunday-review-journal": [("52","weekly review blocks"),("4","quarter summaries"),("15 min","per Sunday")],
 "life-vision-worksheet": [("10","years out, one ordinary Tuesday"),("4","questions"),("3","pages")],
 "ai-prompts-for-life-planning": [("30","prompts"),("7","sections"),("3","AI tools it works with")],
 "60-friendship-scripts": [("60","scripts"),("8","moments covered")],
 "30-day-friendship-challenge": [("30","drills, one a day"),("4","weekly themes")],
 "hard-conversation-worksheet": [("2","preparation pages"),("1","recap page for afterwards"),("4","kinds of relationship it covers")],
 "small-gathering-planner": [("1","sentence to set the purpose"),("10 min","opening planned"),("1","follow-up page")],
 "monthly-money-date": [("20 min","monthly agenda"),("6","timed parts"),("12","monthly record boxes")],
 "debt-payoff-planner": [("2","payoff methods, avalanche and snowball"),("~7%","APR flag on costly debt"),("2","files: PDF and Google Sheet")],
 "emergency-and-sinking-funds-tracker": [("2","jobs: emergency fund and sinking funds"),("2","files: PDF and Google Sheet")],
 "grown-up-paperwork-checklist": [("4","documents every adult needs"),("1","page to locate everything"),("0","passwords stored")],
 "salary-negotiation-prep": [("7","day prep plan"),("7","pushbacks with calm responses"),("1","page brief")],
 "career-evidence-log": [("2","files: PDF and Google Sheet"),("1","entry each Friday")],
 "90-day-career-reset": [("13","weekly moves"),("5","decision gates"),("5","areas: direction, craft, influence, leadership, reinvention")],
}

def facts_html(slug):
    f = FACTS.get(slug)
    if not f:
        return ""
    cells = "".join(f'<div><span class="n">{E(n)}</span><p>{E(t)}</p></div>' for n, t in f)
    return f'<div class="wrap"><div class="facts" style="--cols:{len(f)}"><span class="fl">In the download</span>{cells}</div></div>'

EXTRA_CSS = r"""
html{-webkit-text-size-adjust:100%}
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0}
/* nav */
.bar .navlinks{display:flex;gap:22px;margin-inline:auto 22px}
.bar .navlinks a{text-decoration:none;font-size:.95rem;color:var(--muted);font-weight:500}
.bar .navlinks a:hover{color:var(--ink)}
@media (max-width:760px){.bar .navlinks{display:none}}
/* chips + rating */
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}
.chip{font-family:var(--mono);font-size:12px;letter-spacing:.04em;padding:6px 10px;border-radius:6px;border:1px solid var(--rule);background:var(--surface);color:var(--muted)}
.ratingrow{display:flex;align-items:center;gap:10px;margin-top:16px;font-size:.95rem}
.stars{color:var(--accent);letter-spacing:2px;font-size:1.1rem}
/* reviews */
.reviews{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:18px}
.review{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:24px;display:grid;gap:12px;align-content:start;min-width:0}
.review q{font-family:var(--display);font-size:1.15rem;line-height:1.4;quotes:none}
.review .who{font-family:var(--mono);font-size:12px;color:var(--muted);letter-spacing:.04em}
/* compare */
.compare{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:0;border:1px solid var(--rule);border-radius:14px;overflow:hidden;background:var(--surface)}
.compare > div{padding:24px;display:grid;gap:6px;align-content:start;min-width:0}
.compare > div + div{border-left:1px solid var(--rule)}
.compare .label{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.compare .amt{font-family:var(--display);font-size:2rem;font-weight:600}
.compare .win{background:var(--tint)}
.compare .win .amt{color:var(--accent)}
.compare s{color:var(--muted)}
@media (max-width:640px){.compare > div + div{border-left:0;border-top:1px solid var(--rule)}}
/* sticky buy bar (mobile) */
.sticky{position:fixed;left:0;right:0;bottom:0;z-index:30;background:var(--bg);border-top:1px solid var(--rule);padding:10px 16px calc(10px + env(safe-area-inset-bottom,0px));display:none;transform:translateY(110%);transition:transform .2s ease}
.sticky.on{transform:none}
.sticky .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px}
.sticky .t{min-width:0;display:grid}
.sticky .t b{font-family:var(--display);font-size:1.02rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sticky .t span{font-family:var(--mono);font-size:.8rem;color:var(--muted)}
.sticky .btn{min-height:46px;padding:10px 20px;white-space:nowrap}
@media (max-width:760px){.sticky{display:block}body.has-sticky{padding-bottom:76px}}
/* storefront */
.shero{padding-block:clamp(44px,8vw,96px) clamp(36px,6vw,64px);display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(28px,5vw,64px);align-items:center}
.shero > *{min-width:0}
.shero h1{font-size:clamp(2.3rem,5.8vw,4rem);margin-block:14px 18px}
.fan{position:relative;aspect-ratio:1/1;max-width:480px;width:100%;margin-inline:auto}
.fan img{position:absolute;width:56%;height:auto;border-radius:6px;border:1px solid var(--rule);background:#fff;box-shadow:0 16px 36px rgba(24,33,58,.2)}
.fan img:nth-child(1){left:2%;top:12%;transform:rotate(-7deg)}
.fan img:nth-child(2){right:2%;top:2%;transform:rotate(5deg)}
.fan img:nth-child(3){left:22%;bottom:0;transform:rotate(-1deg);z-index:2}
.statstrip{display:grid;grid-template-columns:repeat(3,1fr);border-block:1px solid var(--rule)}
.statstrip > div{padding:28px 24px;display:grid;gap:6px;min-width:0}
.statstrip > div + div{border-left:1px solid var(--rule)}
.statstrip .n{font-family:var(--display);font-size:2.8rem;font-weight:600;line-height:1;color:var(--accent)}
.statstrip p{font-size:.97rem;color:var(--muted)}
@media (max-width:760px){.statstrip{grid-template-columns:1fr}.statstrip > div + div{border-left:0;border-top:1px solid var(--rule)}}
@media (max-width:820px){.shero{grid-template-columns:1fr}.fan{max-width:360px}}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:26px}
.pill{font:inherit;font-weight:600;font-size:.95rem;padding:10px 18px;border-radius:999px;border:1px solid var(--rule);background:var(--surface);color:var(--ink);cursor:pointer;min-height:44px}
.pill[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,290px),1fr));gap:20px}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:14px;overflow:hidden;display:grid;grid-template-rows:auto 1fr;text-decoration:none;color:inherit;min-width:0;transition:transform .15s ease,box-shadow .15s ease}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(24,33,58,.14)}
.card[hidden]{display:none}
.card .th{background:var(--tint);padding:20px 20px 0;display:flex;justify-content:center;align-items:flex-end;height:210px;overflow:hidden}
.card .th img{width:68%;height:auto;border-radius:4px 4px 0 0;border:1px solid var(--rule);border-bottom:0;background:#fff;box-shadow:0 -4px 20px rgba(24,33,58,.12);align-self:flex-end}
.card .tc{align-self:center;font-family:var(--display);font-weight:600;font-size:1.4rem;text-align:center;padding:0 16px 24px}
.card .bd{padding:18px 20px 20px;display:grid;gap:8px;align-content:start}
.card .tag{font-family:var(--mono);font-size:11.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.card h3{font-size:1.15rem}
.card p{color:var(--muted);font-size:.93rem}
.card .pr{display:flex;justify-content:space-between;align-items:center;margin-top:6px;font-weight:700}
.card .pr span:last-child{color:var(--accent);font-size:.95rem}
.cards.k4{grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr))}
.freecards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:20px}
.groupnote{color:var(--muted);margin:-8px 0 22px;max-width:46em}
.flag{background:var(--ink);color:var(--bg);border-radius:18px;padding:clamp(28px,5vw,56px);display:grid;grid-template-columns:1fr 1fr;gap:clamp(24px,4vw,48px);align-items:center}
.flag > *{min-width:0}
.flag h2{color:var(--bg)}
.flag p{color:var(--bg);opacity:.85;margin-top:12px}
.flag .btn{margin-top:22px}
.flag img{width:100%;max-width:340px;margin-inline:auto;display:block;border-radius:6px;box-shadow:0 18px 40px rgba(0,0,0,.35)}
@media (max-width:820px){.flag{grid-template-columns:1fr}}
.method{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.method > div{border-top:3px solid var(--accent);padding-top:16px;display:grid;gap:6px;align-content:start}
.method h3{font-size:1.15rem}
.method p{color:var(--muted);font-size:.97rem}
@media (max-width:760px){.method{grid-template-columns:1fr}}
.foot{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:28px}
.foot > *{min-width:0}
.foot h4{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;margin:0 0 10px;color:var(--ink)}
.foot ul{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.foot a{text-decoration:none}
.foot a:hover{text-decoration:underline}
@media (max-width:760px){.foot{grid-template-columns:1fr 1fr}}

.facts{display:grid;grid-template-columns:auto repeat(var(--cols,3),1fr);gap:0;align-items:stretch;border-bottom:1px solid var(--rule)}
.facts > *{padding:22px 22px;min-width:0}
.facts .fl{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);align-self:center;padding-left:0}
.facts > div{display:grid;gap:2px;border-left:1px solid var(--rule)}
.facts .n{font-family:var(--display);font-size:2rem;font-weight:600;line-height:1.1;color:var(--accent)}
.facts p{font-size:.92rem;color:var(--muted)}
@media (max-width:760px){.facts{grid-template-columns:repeat(var(--cols,3),1fr)}.facts .fl{grid-column:1/-1;padding:16px 0 0}.facts > div{border-left:0;border-top:1px solid var(--rule);padding:14px 10px 18px 0}.facts .n{font-size:1.6rem}}
@media (max-width:420px){.facts{grid-template-columns:1fr}}

/* ===== motion (200-450ms, reduced-motion safe) ===== */
:root{--ease:cubic-bezier(.2,.7,.2,1)}
@keyframes qlUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes qlIn{from{opacity:0;transform:scale(.97)}to{opacity:1;transform:none}}
@keyframes qlFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes qlFade{from{opacity:0}to{opacity:1}}
body{animation:qlFade .3s ease both}
.hero > div:first-child > *,.shero > div:first-child > *{animation:qlUp .55s var(--ease) both}
.hero > div:first-child > *:nth-child(1),.shero > div:first-child > *:nth-child(1){animation-delay:.04s}
.hero > div:first-child > *:nth-child(2),.shero > div:first-child > *:nth-child(2){animation-delay:.1s}
.hero > div:first-child > *:nth-child(3),.shero > div:first-child > *:nth-child(3){animation-delay:.18s}
.hero > div:first-child > *:nth-child(4),.shero > div:first-child > *:nth-child(4){animation-delay:.26s}
.hero > div:first-child > *:nth-child(5),.shero > div:first-child > *:nth-child(5){animation-delay:.32s}
.hero > div:first-child > *:nth-child(n+6),.shero > div:first-child > *:nth-child(n+6){animation-delay:.38s}
.hero .cover{animation:qlIn .7s var(--ease) .12s both}
.fan img{animation:qlUp .7s var(--ease) both,qlFloat 7s ease-in-out 1s infinite}
.fan img:nth-child(2){animation-delay:.12s,1.4s}
.fan img:nth-child(3){animation-delay:.24s,1.8s}
/* scroll reveals: only hidden once JS has marked them, so the page is complete without JS */
.js .rv{opacity:0;transform:translateY(16px);transition:opacity .45s var(--ease),transform .45s var(--ease);transition-delay:var(--d,0ms)}
.js .rv.in{opacity:1;transform:none}
/* top progress bar */
.progress{position:fixed;left:0;top:0;height:3px;width:100%;transform-origin:0 50%;transform:scaleX(0);background:var(--accent);z-index:60;pointer-events:none}
.bar{transition:box-shadow .25s ease}
.bar.scrolled{box-shadow:0 6px 18px rgba(24,33,58,.08)}
/* buttons: lift + light sweep */
.btn{position:relative;overflow:hidden;cursor:pointer;transition:transform .2s var(--ease),box-shadow .2s var(--ease),background-color .2s ease}
.btn.accent::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.28) 50%,transparent 65%);transform:translateX(-120%);transition:transform .6s var(--ease);pointer-events:none}
.btn.accent:hover::after{transform:translateX(120%)}
.btn:active{transform:translateY(0) scale(.98)}
/* cards + media */
.card .th img{transition:transform .45s var(--ease)}
.card:hover .th img{transform:translateY(-6px) scale(1.03)}
.gallery img{transition:transform .35s var(--ease),box-shadow .35s var(--ease)}
.gallery figure:hover img{transform:translateY(-4px);box-shadow:0 14px 28px rgba(24,33,58,.18)}
.benefit,.proofcard,.review{transition:transform .25s var(--ease),box-shadow .25s var(--ease),border-color .25s ease}
.benefit:hover,.proofcard:hover{transform:translateY(-3px);box-shadow:0 10px 24px rgba(24,33,58,.08);border-color:var(--accent)}
.cover{transform-style:preserve-3d;will-change:transform}
.cover.tilt{transition:transform .12s ease-out}
.cover.tilt-reset{transition:transform .5s var(--ease)}
.pill{transition:background-color .2s ease,color .2s ease,transform .15s ease}
.pill:hover{transform:translateY(-1px)}
.card.pop{animation:qlIn .35s var(--ease) both}
details[open] > p{animation:qlUp .3s var(--ease) both}
summary{transition:color .2s ease}
summary:hover{color:var(--accent)}
summary::after{transition:transform .25s var(--ease)}
details[open] summary::after{transform:translateY(-50%) rotate(180deg)}
.brand,.navlinks a{transition:color .2s ease}
section{scroll-margin-top:76px}
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation:none!important;transition:none!important}
  .js .rv{opacity:1!important;transform:none!important}
  .progress{display:none}
}
.pairs{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:18px}

/* free download dialog */
dialog.getfree{border:1px solid var(--rule);border-radius:16px;background:var(--surface);color:var(--ink);padding:0;width:min(92vw,520px);max-height:92vh;overflow:auto;box-shadow:0 30px 80px rgba(10,14,30,.35)}
dialog.getfree::backdrop{background:rgba(14,18,32,.55);backdrop-filter:blur(3px)}
dialog.getfree[open]{animation:qlUp .28s cubic-bezier(.2,.8,.2,1) both}
.gf-body,.gf-done{padding:32px 28px 26px;display:grid;gap:14px}
.gf-x{position:absolute;top:8px;right:8px;margin:0}
.gf-close{background:none;border:0;font-size:30px;line-height:1;width:44px;height:44px;cursor:pointer;color:var(--muted);border-radius:10px}
.gf-close:hover{color:var(--ink);background:var(--band)}
.gf-sub{color:var(--muted)}
.gf-form{display:grid;gap:14px;margin-top:4px}
.gf-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:480px){.gf-row{grid-template-columns:1fr}}
.gf-form label{display:grid;gap:6px;font-size:.88rem;font-weight:700}
.gf-form input{font:inherit;font-weight:400;font-size:1rem;min-height:50px;padding:10px 14px;border:2px solid var(--rule);border-radius:10px;background:var(--bg);color:var(--ink)}
.gf-form input:focus{outline:none;border-color:var(--accent)}
.gf-form input[aria-invalid="true"]{border-color:#c0392b}
.gf-err{color:#b3261e;font-size:.92rem;margin:0}
.gf-submit{width:100%;border:0;cursor:pointer}
.gf-submit[disabled]{opacity:.65;cursor:progress;transform:none}
.gf-form .micro{color:var(--muted);font-size:.82rem;text-align:center}
.gf-done{text-align:left}
.gf-body[hidden],.gf-done[hidden],.gf-err[hidden]{display:none}
.gf-body>*,.gf-done>*,.gf-form>*,.gf-row>*{min-width:0}
.gf-form input{width:100%;min-width:0}
dialog.getfree{overflow-x:hidden}
#gf-frame{display:none}
@media (prefers-reduced-motion:reduce){dialog.getfree[open]{animation:none}}
"""

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://quietleverages.com/{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Quiet Leverages"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://quietleverages.com/{canon}">{ogimg}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#18213a">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Red+Hat+Text:wght@400;500;700&family=Red+Hat+Mono:wght@400;500&display=swap">
<script>document.documentElement.classList.add("js")</script>
<link rel="stylesheet" href="site.css">
</head><body class="{cls}">
<div class="progress" id="progress" aria-hidden="true"></div>
"""

def load():
    prods = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        d = json.load(open(f))
        prods[d["slug"]] = d
    return prods

def img_rel(p):
    return "img/" + os.path.basename(p)

def copy_imgs(prods):
    os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
    for d in prods.values():
        for p in d.get("previews", []):
            src = p if os.path.isabs(p) else os.path.join(ROOT, p)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(SITE, "img", os.path.basename(p)))

def nav(active=""):
    return ('<header class="bar"><div class="wrap"><a class="brand" href="index.html">Quiet <span>Leverages</span></a>'
            '<nav class="navlinks" aria-label="Main"><a href="index.html#free">Free tools</a><a href="index.html#shop">All tools</a><a href="quiet-reset-2027.html">The Quiet Reset</a></nav>'
            '<div class="barright"><a class="btn accent" href="index.html#free">Start free</a></div></div></header>')

def footer(prods, disclaimer="General education only."):
    def lst(slugs):
        return "".join(f'<li><a href="{s}.html">{E(prods[s]["title"])}</a></li>' for s in slugs if s in prods)
    return f'''<footer><div class="wrap foot">
<div><p><b style="color:var(--ink)">Quiet Leverages</b></p><p style="margin-top:8px">We read widely, test each idea against an ordinary week, and keep only what still works on a tired Tuesday.</p><p style="margin-top:10px">Every purchase is a digital download, sold on Gumroad.</p></div>
<div><h4>Free</h4><ul>{lst(FREE)}</ul></div>
<div><h4>Kits</h4><ul>{lst(KITS)}</ul></div>
<div><h4>Flagship</h4><ul>{lst([FLAG])}<li><a href="index.html#shop">All 25 tools</a></li></ul></div>
</div><div class="wrap" style="margin-top:22px"><p>{E(disclaimer)} Personal use only.</p></div></footer>'''

def link_for(prods, slug):
    return f"{slug}.html" if slug in prods else STORE + slug

def card(d, hero=True):
    sl = d["slug"]
    pv = d.get("previews", [])
    th = f'<img src="{img_rel(pv[0])}" alt="">' if pv else f'<div class="tc">{E(d["title"])}</div>'
    price = d["price"]
    return (f'<a class="card p-{d["pillar"]}" data-pillar="{d["pillar"]}" href="{sl}.html"><div class="th">{th}</div>'
            f'<div class="bd"><span class="tag">{PILLAR[d["pillar"]]}</span><h3>{E(d["title"])}</h3><p>{E(SUMMARY.get(sl, d["sub"]))}</p>'
            f'<div class="pr"><span>{E(price)}</span><span>View details</span></div></div></a>')

STICKY_JS_HOOK = '<div class="sticky" id="sticky" aria-hidden="true"><div class="wrap"><div class="t"><b>{title}</b><span>{price}</span></div><a class="btn accent" href="{url}" data-buy="1" target="_blank" rel="noopener">{cta}</a></div></div>'

def _product_page(d, prods):
    sl = d["slug"]
    url = d.get("url") or (STORE + sl)
    free = d.get("free", False)
    price = d["price"]
    cta = d.get("cta") or ("Get it free" if free else f"Get it for {price}")
    pv = d.get("previews", [])
    labels = d.get("preview_labels", [])
    alts = d.get("preview_alts", [])
    pillar = d["pillar"]

    price_html = lambda: f'<span class="price-tag">{("<s>"+E(d["priceOld"])+"</s>") if d.get("priceOld") else ""}{E(price)}</span>'
    if pv:
        cover = f'<div class="cover"><div class="stack"><img src="{img_rel(pv[0])}" alt="{E(alts[0] if alts else d["title"]+" first page")}"></div><span class="tag">{E(d.get("covertag","Real page from the product"))}</span></div>'
    else:
        cover = f'<div class="cover"><div class="typecover"><div class="rule"></div><div class="t">{E(d["title"])}</div><div class="by">Quiet Leverages</div></div></div>'

    uvp = "".join(f'<div><h3>{E(u["h"])}</h3><p>{E(u["p"])}</p></div>' for u in d["uvp"])
    four = len(d["benefits"]) == 4
    benefits = "".join(f'<div class="benefit"><div class="chk">{CHK}</div><h3>{E(b["h"])}</h3><p>{E(b["p"])}</p></div>' for b in d["benefits"])
    inside = "".join(f"<li>{b}</li>" for b in d["inside"])
    gal = ""
    if len(pv) > 1:
        figs = ""
        for i, u in enumerate(pv[1:], 1):
            lab = labels[i] if i < len(labels) else ""
            alt = alts[i] if i < len(alts) else (lab or f'{d["title"]} page {i+1}')
            figs += f'<figure><img loading="lazy" src="{img_rel(u)}" alt="{E(alt)}"><figcaption>{E(lab)}</figcaption></figure>'
        gal = f'<div class="gallery" style="margin-top:36px">{figs}</div>'

    problem = ""
    if d.get("stat"):
        s = d["stat"]
        problem = f'<section><div class="wrap problem"><div class="bignum">{E(s["n"])}</div><div><p>{E(s["t"])}</p><span class="src">{E(s["src"])}</span></div></div></section>'

    steps = ""
    if d.get("steps"):
        st = d["steps"]
        items = "".join(f'<li><h3>{E(i["h"])}</h3><p>{E(i["p"])}</p></li>' for i in st["items"])
        steps = f'<section class="alt"><div class="wrap"><div class="sechead"><span class="eyebrow">{E(st.get("eyebrow","How it works"))}</span><h2>{E(st["title"])}</h2></div><ol class="steps">{items}</ol></div></section>'

    forwho = ""
    if d.get("forwho"):
        fw = d["forwho"]
        y = "".join(f"<li>{E(i)}</li>" for i in fw["yes"]); n = "".join(f"<li>{E(i)}</li>" for i in fw["no"])
        forwho = f'<section><div class="wrap"><div class="sechead"><span class="eyebrow">Fit check</span><h2>{E(fw.get("title","Is this for you?"))}</h2></div><div class="forwho"><div class="yes"><h3>Use this if</h3><ul>{y}</ul></div><div class="no"><h3>Skip it if</h3><ul>{n}</ul></div></div></div></section>'

    pr = d.get("proof", {})
    cards = "".join(f'<div class="proofcard"><div class="n">{E(s["n"])}</div><p>{E(s["t"])}</p><span class="src">{E(s["src"])}</span></div>' for s in pr.get("stats", []))
    note = f'<div class="proofnote">{E(pr["note"])}<span>{E(pr.get("noteBy","Quiet Leverages house rule"))}</span></div>' if pr.get("note") else ""
    proof = (f'<section class="alt" id="proof"><div class="wrap"><div class="sechead"><span class="eyebrow">Social proof</span><h2>{E(pr.get("title","The numbers behind the problem"))}</h2></div>'
             f'<div class="proofgrid">{cards}</div>{note}'
             f'<div id="reviews-wrap" hidden style="margin-top:40px"><div class="sechead"><span class="eyebrow">Reader reviews</span><h2>What readers say about {E(d["title"])}</h2></div><div class="reviews" id="reviews"></div></div>'
             f'</div></section>')

    # real price comparison, only where the catalog gives true numbers
    compare = ""
    if sl == "quiet-reset-2027":
        compare = '''<section><div class="wrap"><div class="sechead"><span class="eyebrow">The arithmetic</span><h2>The three kits alone cost more than the early-bird price</h2><p>Prices are from the Gumroad listings. The bundle also holds the planner, the 90-day reset, the AI Coach Pack, the Sunday reviews, three playbooks and three quick tools.</p></div>
<div class="compare"><div><span class="label">Three kits, bought separately</span><span class="amt">$57</span><p style="color:var(--muted);font-size:.95rem">The 30-Day Friendship Practice, The Raise Kit and The Couples Money Reset at $19 each.</p></div>
<div class="win"><span class="label">The Quiet Reset 2027, early-bird</span><span class="amt">$47</span><p style="font-size:.95rem">Everything in the download, until December 31. Use code EARLYBIRD.</p></div>
<div><span class="label">After the early-bird</span><span class="amt">$67</span><p style="color:var(--muted);font-size:.95rem">Standard price once the early-bird ends.</p></div></div></div></section>'''
    elif sl == "career-kit":
        compare = '''<section><div class="wrap"><div class="sechead"><span class="eyebrow">The arithmetic</span><h2>Two more tools are already inside</h2><p>The Career Kit includes The Raise Kit and The Stay-or-Go Worksheet.</p></div>
<div class="compare"><div><span class="label">The Raise Kit on its own</span><span class="amt">$19</span></div><div><span class="label">The Stay-or-Go Worksheet on its own</span><span class="amt">Free</span></div><div class="win"><span class="label">The Career Kit, with both included</span><span class="amt">$39</span></div></div></div></section>'''

    of = d.get("offer", {})
    offer_items = "".join(f"<li>{E(i)}</li>" for i in of.get("items", []))
    offer = (f'<section id="get"><div class="wrap"><div class="offer"><div><span class="eyebrow" style="color:var(--bg);opacity:.7">{E(of.get("eyebrow","What you get"))}</span>'
             f'<h2 style="margin-top:10px">{E(of.get("h","Start today"))}</h2><p>{E(of.get("p",""))}</p><ul>{offer_items}</ul></div>'
             f'<div class="buybox">{price_html()}<a class="btn accent" href="{E(url)}" data-buy="1" target="_blank" rel="noopener">{E(cta)}</a><p class="micro">{E(d.get("priceNote","Instant download on Gumroad."))}</p></div></div></div></section>')

    faq = "".join(f'<details><summary>{E(f["q"])}</summary><p>{E(f["a"])}</p></details>' for f in d["faq"])

    # on-site next steps: the listed related product + two siblings in the same pillar
    pair_slugs = []
    if d.get("related"): pair_slugs.append(d["related"]["slug"])
    for s, o in prods.items():
        if s != sl and o["pillar"] == pillar and s not in pair_slugs and len(pair_slugs) < 3 and s in KITS + FREE + [FLAG]:
            pair_slugs.append(s)
    pairs = "".join(card(prods[s]) for s in pair_slugs if s in prods)
    related = ""
    if d.get("related") and d["related"]["slug"] not in prods:
        r = d["related"]
        related = f'<div class="related" style="margin-bottom:24px"><div><span class="eyebrow">Next step</span><h3>{E(r["name"])} <span style="font-family:var(--mono);font-size:.9rem;color:var(--muted);font-weight:400">{E(r["price"])}</span></h3><p style="color:var(--muted);margin-top:6px">{E(r["blurb"])}</p></div><a class="btn ghost" href="{E(STORE + r["slug"])}" target="_blank" rel="noopener">See {E(r["name"])}</a></div>'
    pairsec = f'<section style="padding-block:0 clamp(44px,7vw,84px)"><div class="wrap"><div class="sechead"><span class="eyebrow">Pairs well with</span><h2>The next step after this one</h2></div>{related}<div class="pairs">{pairs}</div></div></section>' if (pairs or related) else ""

    fin = d.get("final", {})
    finalsec = (f'<section><div class="wrap final"><h2>{E(fin.get("h", d["h1"]))}</h2><p>{E(fin.get("p", d["sub"]))}</p>'
                f'<a class="btn accent" href="{E(url)}" data-buy="1" target="_blank" rel="noopener">{E(cta)}</a><p class="micro" style="margin:0">{E(d.get("priceNote","Instant download on Gumroad."))}</p></div></section>')

    og = (f'<meta property="og:image" content="https://quietleverages.com/{img_rel(pv[0])}">' if pv else "")
    page = HEAD.format(title=E(d["title"] + " | Quiet Leverages"), desc=E(SUMMARY.get(sl, d["sub"])), cls=f"p-{pillar} has-sticky page-product", canon=sl + ".html", ogimg=og)
    page += nav()
    page += f'''<main id="top" data-slug="{sl}">
<div class="wrap hero"><div><span class="eyebrow">{E(d["eyebrow"])}</span><h1>{E(d["h1"])}</h1><p class="sub">{E(d["sub"])}</p>
<div class="cta-row" id="herocta">{price_html()}<a class="btn accent" href="{E(url)}" data-buy="1" target="_blank" rel="noopener">{E(cta)}</a><a class="btn ghost" href="#inside">See what's inside</a></div>
<div class="ratingrow" id="rating" hidden></div>
<p class="micro">{d.get("heroMicro","<b>Instant download.</b> Print it or use it on a tablet.")}</p>
<div class="chips"><span class="chip">Real pages shown below</span><span class="chip">{E(PILLAR[pillar])} · Quiet Leverages</span><span class="chip">Sold on Gumroad</span></div></div>{cover}</div>
<div class="wrap"><div class="uvp">{uvp}</div></div>
{facts_html(sl)}
{problem}
<section class="alt"><div class="wrap"><div class="sechead"><span class="eyebrow">What it does for you</span><h2>{E(d.get("benefitsTitle","What changes after you fill it in"))}</h2></div><div class="benefits" style="{'grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr))' if four else ''}">{benefits}</div></div></section>
<section id="inside"><div class="wrap"><div class="inside"><div class="sechead" style="margin:0"><span class="eyebrow">What's inside</span><h2>{E(d.get("insideTitle","Everything in the download"))}</h2><p>{E(d.get("insideLead",""))}</p></div><ul>{inside}</ul></div>{gal}</div></section>
{steps}
{forwho}
{proof}
{compare}
{offer}
<section class="alt"><div class="wrap narrow"><div class="sechead"><span class="eyebrow">Questions</span><h2>Before you decide</h2></div><div class="faq">{faq}</div></div></section>
{pairsec}
{finalsec}
</main>
{footer(prods, d.get("disclaimer","General education only."))}
{STICKY_JS_HOOK.format(title=E(d["title"]), price=E(price), url=E(url), cta=E("Get it free" if free else "Buy now"))}
<a class="gumroad-button" id="gr-open" href="{E(url)}" data-gumroad-overlay-checkout="true" tabindex="-1" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden">Checkout</a>
<script src="https://gumroad.com/js/gumroad.js" onload="window.__gr=1"></script>
<script src="site.js"></script>
</body></html>'''
    return page

def index_page(prods):
    fan = "".join(f'<img src="{img_rel(prods[s]["previews"][0])}" alt="">' for s in ("quiet-reset-2027", "raise-kit", "friendship-audit") if prods[s].get("previews"))
    free_cards = "".join(card(prods[s]) for s in FREE)
    kit_cards = "".join(card(prods[s]) for s in KITS)
    small = [s for s in prods if s not in FREE + KITS + [FLAG]]
    small_cards = "".join(card(prods[s]) for s in small)
    flag = prods[FLAG]
    fimg = img_rel(flag["previews"][0]) if flag.get("previews") else ""
    pills = '<button class="pill" aria-pressed="true" data-f="all">All</button>' + "".join(f'<button class="pill" aria-pressed="false" data-f="{k}">{v}</button>' for k, v in PILLAR.items())
    page = HEAD.format(title="Quiet Leverages | Fill-in tools for work, money and people", desc="Worksheets, trackers, scripts and planners for work, money and people. Start with a free tool.", cls="p-reset page-home", canon="", ogimg='<meta property="og:image" content="https://quietleverages.com/img/qr-1.jpg">')
    page += nav()
    page += f'''<main id="top">
<div class="wrap shero"><div><span class="eyebrow">Fill-in tools · Work · Money · People</span>
<h1>Tools you fill in on a Sunday. Not books you read and forget.</h1>
<p class="sub">Worksheets, trackers, scripts and planners for the places a good year leaks: your job, your money and your friendships. Start with a free one.</p>
<div class="cta-row"><a class="btn accent" href="#free">Start with a free tool</a><a class="btn ghost" href="#shop">Browse all 25 tools</a></div>
<p class="micro"><b>Instant download.</b> Print them or use them on a tablet. Sold on Gumroad.</p>
<div class="chips"><span class="chip">3 free tools</span><span class="chip">4 kits</span><span class="chip">1 year planner</span><span class="chip">17 small tools</span></div></div>
<div class="fan" aria-hidden="true">{fan}</div></div>
<div class="wrap"><div class="statstrip">
<div><span class="n">29%</span><p>of adults aged 30-44 are frequently or always lonely, the highest of any age group.</p><span class="src">Harvard Making Caring Common, 2024</span></div>
<div><span class="n">48%</span><p>of workers say they stay in their job out of fear and economic uncertainty.</p><span class="src">Monster, Oct 2025</span></div>
<div><span class="n">88%</span><p>of US adults began 2026 feeling financial stress.</p><span class="src">NEFE, Jan 2026</span></div></div></div>

<section id="free"><div class="wrap"><div class="sechead"><span class="eyebrow">Start here · Free</span><h2>Three free tools, one for each place life leaks</h2><p>Each takes one sitting. Pick the one that matches the thing on your mind this week.</p></div><div class="freecards">{free_cards}</div></div></section>

<section class="alt" id="shop"><div class="wrap"><div class="sechead"><span class="eyebrow">The shop</span><h2>Every tool, by the part of life it covers</h2></div>
<div class="pills" role="group" aria-label="Filter by area">{pills}</div>
<h3 style="margin-bottom:14px">Kits, $19-39</h3><p class="groupnote">A guide, a tracker and the scripts, built to be run over days or weeks.</p>
<div class="cards k4" id="kits">{kit_cards}</div>
<h3 style="margin:44px 0 14px">Small tools, $7-12</h3><p class="groupnote">One job each. A cheap first step, and each links to the kit that goes further.</p>
<div class="cards" id="small">{small_cards}</div>
<p id="empty" class="groupnote" hidden style="margin-top:20px">No tools in this group yet.</p></div></section>

<section><div class="wrap"><div class="flag"><div><span class="eyebrow" style="color:var(--bg);opacity:.7">The flagship · Opens Nov 24</span><h2 style="margin-top:10px">The Quiet Reset 2027</h2><p>Score twelve areas of your life, pick three to work on, and keep the other nine on a simple maintenance minimum. Two 45-minute blocks and a fifteen-minute Sunday review each week: 105 minutes, and that is the whole commitment.</p><p><b>$47 early-bird until December 31</b>, then $67. The three kits inside cost $57 on their own.</p><a class="btn accent" href="quiet-reset-2027.html">See what is inside</a></div>{('<img src="'+fimg+'" alt="The Quiet Reset 2027 planner cover">') if fimg else ""}</div></div></section>

<section class="alt"><div class="wrap"><div class="sechead"><span class="eyebrow">How we build them</span><h2>Read widely. Test it. Keep what survives.</h2><p>Every tool starts from reading, then gets checked against an ordinary week before it ships.</p></div>
<div class="method"><div><h3>We read widely</h3><p>The Social Architecture Playbook, The Finance Architect and The Career Playbook sit behind the tools.</p></div><div><h3>We test it on an ordinary week</h3><p>If a step needs a free weekend and perfect motivation, it does not make it in.</p></div><div><h3>We keep what works on a tired Tuesday</h3><p>Short steps, plain words and scripts you can say out loud.</p></div></div>
<div class="statstrip" style="margin-top:32px;background:var(--surface);border:1px solid var(--rule);border-radius:12px"><div><span class="n">50</span><p>career books behind The Career Playbook, grouped into five pillars across twenty chapters.</p></div><div><span class="n">25</span><p>tools across work, money and people, three of them free.</p></div><div><span class="n">48</span><p>pages in The Quiet Reset 2027 planner, linked for use on a tablet.</p></div></div>
<div class="proofnote" style="margin-top:28px">Every page on this site shows real pages from the product. No mockups, and no invented reviews.<span>Quiet Leverages house rule</span></div></div></section>

<section id="reviews-wrap" hidden><div class="wrap"><div class="sechead"><span class="eyebrow">Reader reviews</span><h2>What readers say</h2></div><div class="reviews" id="reviews"></div></div></section>

<section class="alt"><div class="wrap narrow"><div class="sechead"><span class="eyebrow">Questions</span><h2>Before you pick one</h2></div><div class="faq">
<details><summary>Which tool should I start with?</summary><p>Start with the free tool that matches what is on your mind: the Friendship Audit for people, the Stay-or-Go Worksheet for work, or What to Fund First for money. Each takes one sitting.</p></details>
<details><summary>Where do I buy, and what do I get?</summary><p>Every tool is a digital download sold on Gumroad. You get the files straight after checkout, usually a printable PDF and, on some tools, a Google Sheet or Notion import.</p></details>
<details><summary>Do I need to print anything?</summary><p>No. Print the PDFs if you like writing by hand, or fill them in on a tablet with any PDF app.</p></details>
<details><summary>Is this financial, legal or career advice?</summary><p>No. Everything is general education. The money tools are not financial advice, and the career tools are not employment or legal advice.</p></details>
<details><summary>What is the difference between a kit and a small tool?</summary><p>A small tool does one job, such as a worksheet or a tracker. A kit gives you a guide, a tracker and scripts to run over several days or weeks.</p></details>
<details><summary>Who are these for?</summary><p>Mostly mid-career managers and senior individual contributors, roughly 30-45, who are doing most things right and still feel a little behind. People earlier or later in their careers use them too.</p></details>
</div></div></section>

<section><div class="wrap final"><h2>Pick one thing to fill in this week.</h2><p>Free tools take one sitting and need no setup.</p><a class="btn accent" href="#free">Start with a free tool</a></div></section>
</main>
{footer(prods)}
<script src="site.js"></script>
</body></html>'''
    return page

JS = r"""
(function(){
  var doc=document, body=doc.body;
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]});}
  // filter pills (storefront)
  var pills=doc.querySelectorAll('.pill');
  if(pills.length){
    var cards=doc.querySelectorAll('.cards .card'), empty=doc.getElementById('empty');
    pills.forEach(function(p){p.addEventListener('click',function(){
      var f=p.getAttribute('data-f'), shown=0;
      pills.forEach(function(q){q.setAttribute('aria-pressed',q===p?'true':'false')});
      cards.forEach(function(c){var ok=f==='all'||c.getAttribute('data-pillar')===f;c.hidden=!ok;if(ok)shown++});
      if(empty)empty.hidden=shown>0;
    })});
  }
  // sticky buy bar: show once the hero CTA has scrolled away
  var st=doc.getElementById('sticky'), hc=doc.getElementById('herocta');
  if(st&&hc&&'IntersectionObserver' in window){
    new IntersectionObserver(function(es){es.forEach(function(e){st.classList.toggle('on',!e.isIntersecting&&e.boundingClientRect.top<0)})}).observe(hc);
  }
  // reviews: render only real entries from reviews.json
  var wrap=doc.getElementById('reviews-wrap'), list=doc.getElementById('reviews');
  if(wrap&&list&&window.fetch){
    var main=doc.querySelector('main'), slug=main&&main.getAttribute('data-slug');
    fetch('reviews.json',{cache:'no-store'}).then(function(r){return r.ok?r.json():null}).then(function(j){
      if(!j||!j.items)return;
      var items=j.items.filter(function(i){return i&&i.text&&i.rating&&(!slug||i.slug===slug)});
      if(!slug)items=items.slice(0,3);
      if(!items.length)return;
      list.innerHTML=items.map(function(i){
        var s=new Array(Math.max(1,Math.min(5,Math.round(i.rating)))+1).join('★');
        return '<figure class="review" style="margin:0"><div class="stars" aria-label="'+esc(i.rating)+' out of 5">'+s+'</div><q>'+esc(i.text)+'</q><figcaption class="who">'+esc(i.name||'Reader')+(i.source?' · '+esc(i.source):'')+'</figcaption></figure>';
      }).join('');
      wrap.hidden=false;
      var r=doc.getElementById('rating');
      if(r&&slug){
        var avg=items.reduce(function(a,i){return a+Number(i.rating)},0)/items.length;
        r.innerHTML='<span class="stars" aria-hidden="true">★★★★★</span><span><b>'+avg.toFixed(1)+'</b> from '+items.length+' reader review'+(items.length>1?'s':'')+'</span>';
        r.hidden=false;
      }
    }).catch(function(){});
  }
})();
(function(){
  var doc=document, reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Gumroad overlay checkout: route styled buy buttons into Gumroad's overlay; plain link if its script is missing
  var hidden=doc.getElementById('gr-open');
  doc.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[data-buy]');
    if(!a||!hidden||!window.__gr)return;
    e.preventDefault(); hidden.click();
  });
  // header shadow + progress bar
  var bar=doc.querySelector('.bar'), prog=doc.getElementById('progress'), tick=false;
  function onScroll(){
    if(tick)return; tick=true;
    requestAnimationFrame(function(){
      var y=window.scrollY||0, h=doc.documentElement.scrollHeight-window.innerHeight;
      if(bar)bar.classList.toggle('scrolled',y>8);
      if(prog&&h>0)prog.style.transform='scaleX('+Math.min(1,y/h)+')';
      tick=false;
    });
  }
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
  if(reduce)return;
  // scroll reveals with stagger
  var sel='.sechead,.benefit,.proofcard,.steps li,.forwho > div,.card,.gallery figure,.facts > div,.uvp > div,.method > div,.compare > div,.review,details,.offer,.flag,.related,.final > *,.statstrip > div,.proofnote,.bignum,.problem > div';
  var els=[].slice.call(doc.querySelectorAll(sel));
  els.forEach(function(el){
    var sibs=el.parentElement?[].slice.call(el.parentElement.children).filter(function(c){return c.matches(sel)}):[el];
    el.style.setProperty('--d',Math.min(sibs.indexOf(el),6)*60+'ms');
    el.classList.add('rv');
  });
  function count(el){
    var m=/^([^0-9]*)([0-9][0-9,]*(?:\.[0-9]+)?)(.*)$/.exec(el.textContent.trim());
    if(!m)return;
    var target=parseFloat(m[2].replace(/,/g,'')), dec=(m[2].split('.')[1]||'').length, comma=m[2].indexOf(',')>-1;
    if(!isFinite(target)||target>20000)return;
    var t0=null, dur=900;
    function fmt(v){var t=v.toFixed(dec);return comma?Number(t).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec}):t}
    el.textContent=m[1]+fmt(0)+m[3];
    function step(ts){
      if(t0===null)t0=ts;
      var p=Math.min(1,(ts-t0)/dur), e=1-Math.pow(1-p,3);
      el.textContent=m[1]+fmt(target*e)+m[3];
      if(p<1)requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  function reveal(el){
    el.classList.add('in');
    el.querySelectorAll('.n,.bignum').forEach(count);
    if(el.matches('.n,.bignum'))count(el);
  }
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){if(e.isIntersecting){reveal(e.target);io.unobserve(e.target)}});
    },{rootMargin:'0px 0px -8% 0px',threshold:.08});
    els.forEach(function(el){io.observe(el)});
    setTimeout(function(){els.forEach(function(el){el.classList.add('in')})},3500); // safety net
  } else { els.forEach(function(el){el.classList.add('in')}); }
  // pointer tilt on the cover image (desktop, fine pointers only)
  var cover=doc.querySelector('.hero .cover');
  if(cover&&matchMedia('(hover:hover) and (pointer:fine)').matches){
    cover.addEventListener('mousemove',function(e){
      var r=cover.getBoundingClientRect(), x=(e.clientX-r.left)/r.width-.5, y=(e.clientY-r.top)/r.height-.5;
      cover.classList.remove('tilt-reset'); cover.classList.add('tilt');
      cover.style.transform='perspective(900px) rotateY('+(x*7).toFixed(2)+'deg) rotateX('+(-y*7).toFixed(2)+'deg)';
    });
    cover.addEventListener('mouseleave',function(){
      cover.classList.remove('tilt'); cover.classList.add('tilt-reset'); cover.style.transform='';
    });
  }
  // re-animate cards when the shop filter changes
  doc.querySelectorAll('.pill').forEach(function(p){p.addEventListener('click',function(){
    doc.querySelectorAll('.cards .card:not([hidden])').forEach(function(c,i){c.classList.remove('pop');void c.offsetWidth;c.style.animationDelay=(i*35)+'ms';c.classList.add('pop')});
  })});
})();


(function(){
  function init(){
  var dlg=document.getElementById('getfree'); if(!dlg||!dlg.showModal)return;
  var form=document.getElementById('gf-form'), frame=document.getElementById('gf-frame');
  var body=document.getElementById('gf-body'), done=document.getElementById('gf-done');
  var err=document.getElementById('gf-err'), btn=document.getElementById('gf-btn'), sent=false;
  function open(){body.hidden=false;done.hidden=true;sent=false;btn.disabled=false;btn.textContent='Send it to me';err.hidden=true;dlg.showModal();var f=form.querySelector('input');f&&f.focus()}
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[data-free]'); if(!a)return;
    e.preventDefault(); open();
  });
  dlg.addEventListener('click',function(e){if(e.target===dlg)dlg.close()});
  document.getElementById('gf-ok').addEventListener('click',function(){dlg.close()});
  function fail(msg,el){err.textContent=msg;err.hidden=false;if(el){el.setAttribute('aria-invalid','true');el.focus()}}
  form.addEventListener('submit',function(e){
    var f=form.elements, ok=true; err.hidden=true;
    [].forEach.call(form.querySelectorAll('input'),function(i){i.removeAttribute('aria-invalid')});
    var fn=f['fields[first_name]'], ln=f['fields[last_name]'], em=f['email_address'];
    if(!fn.value.trim()){e.preventDefault();return fail('Please add your first name.',fn)}
    if(!ln.value.trim()){e.preventDefault();return fail('Please add your last name.',ln)}
    if(!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em.value.trim())){e.preventDefault();return fail('That email does not look right.',em)}
    em.value=em.value.trim(); sent=true; btn.disabled=true; btn.textContent='Sending…';
    setTimeout(function(){ if(sent&&body.hidden===false) finish() },6000);
  });
  frame.addEventListener('load',function(){ if(sent) finish() });
  function finish(){
    if(done.hidden===false)return;
    document.getElementById('gf-addr').textContent=form.elements['email_address'].value;
    body.hidden=true; done.hidden=false;
  }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init); else init();
})();
"""

NOT_FOUND = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Page not found | Quiet Leverages</title><meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Red+Hat+Text:wght@400;700&display=swap">
<link rel="stylesheet" href="/site.css"></head><body class="p-reset"><div class="wrap" style="min-height:70vh;display:grid;place-content:center;gap:18px;text-align:center;justify-items:center">
<span class="eyebrow">404</span><h1>That page is not here.</h1><p class="sub" style="max-width:30em">The link may be old, or the tool may have moved. The shop has everything.</p><a class="btn accent" href="/">Back to the shop</a></div></body></html>"""


FREE_FORMS = {"friendship-audit": 9991643, "stay-or-go": 9991648, "what-to-fund-first": 9991657}

FREE_MODAL = """<dialog class="getfree" id="getfree" aria-labelledby="gf-title" data-form="{form}" data-slug="{slug}">
<form method="dialog" class="gf-x"><button aria-label="Close" class="gf-close">&times;</button></form>
<div class="gf-body" id="gf-body">
<span class="eyebrow">Free download</span>
<h2 id="gf-title">{title}</h2>
<p class="gf-sub">Tell us where to send it. The PDF and the Google Sheet version arrive in your inbox in a minute or two.</p>
<form id="gf-form" class="gf-form" action="https://app.kit.com/forms/{form}/subscriptions" method="post" target="gf-frame" novalidate>
<div class="gf-row"><label>First name<input name="fields[first_name]" autocomplete="given-name" required></label>
<label>Last name<input name="fields[last_name]" autocomplete="family-name" required></label></div>
<label>Email<input name="email_address" type="email" autocomplete="email" inputmode="email" required></label>
<p class="gf-err" id="gf-err" role="alert" hidden></p>
<button class="btn accent gf-submit" type="submit" id="gf-btn">Send it to me</button>
<p class="micro">We email the download and the occasional note from Quiet Leverages. Unsubscribe in one click.</p>
</form>
</div>
<div class="gf-done" id="gf-done" hidden>
<span class="eyebrow">Sent</span>
<h2>Check your inbox.</h2>
<p class="gf-sub">Your {title} is on its way to <b id="gf-addr"></b>. It usually lands within a minute. If you do not see it, look in Promotions or Spam.</p>
<p class="gf-sub">Already on our list from another tool? The email is sent once, so grab your files here:</p>
<a class="btn accent" href="{dl}" download>Download now</a>
<button class="btn ghost" type="button" id="gf-ok">Back to the page</button>
</div>
<iframe name="gf-frame" id="gf-frame" title="" hidden></iframe>
</dialog>"""

def product_page(d, prods):
    html = _product_page(d, prods)
    sl = d["slug"]
    if sl not in FREE_FORMS:
        # visible buy links go straight to checkout (skips Gumroad's product page); overlay still preferred when it loads
        base = STORE + sl
        direct = base + ("/EARLYBIRD" if sl == FLAG else "") + "?wanted=true"
        html = html.replace('href="%s" data-buy="1"' % base, 'href="%s" data-buy="1"' % direct)
        if sl == FLAG:
            html = html.replace('id="gr-open" href="%s"' % base, 'id="gr-open" href="%s/EARLYBIRD"' % base)
        return html
    html = html.replace('data-buy="1" target="_blank" rel="noopener"', 'data-free="%s"' % sl)
    html = re.sub(r'<a class="gumroad-button"[^>]*>[^<]*</a>\s*', '', html)
    html = re.sub(r'<script src="https://gumroad\.com/js/gumroad\.js"[^>]*></script>\s*', '', html)
    html = re.sub(r'href="https://quietleverages\.gumroad\.com/l/%s"([^>]*data-free)' % re.escape(sl), r'href="#getfree"\1', html)
    dls = json.load(open(os.path.join(ROOT, "downloads.json")))
    dl = dls[sl].replace("https://quietleverages.com/", "")
    modal = FREE_MODAL.replace("{dl}", dl).replace("{form}", str(FREE_FORMS[sl])).replace("{slug}", sl).replace("{title}", E(d["title"]))
    return html.replace("</body>", modal + "\n</body>", 1)

def write_extras(prods):
    open(os.path.join(SITE, "CNAME"), "w").write("quietleverages.com\n")
    open(os.path.join(SITE, "404.html"), "w").write(NOT_FOUND)
    open(os.path.join(SITE, "robots.txt"), "w").write("User-agent: *\nAllow: /\nDisallow: /downloads/\nSitemap: https://quietleverages.com/sitemap.xml\n")
    urls = ["https://quietleverages.com/"] + ["https://quietleverages.com/" + s + ".html" for s in prods]
    open(os.path.join(SITE, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join("<url><loc>%s</loc></url>\n" % u for u in urls) + "</urlset>\n")

def main():
    prods = load()
    # keep any real reviews the owner has added to site/reviews.json
    rv_path = os.path.join(SITE, "reviews.json")
    kept_reviews = open(rv_path).read() if os.path.exists(rv_path) else None
    if os.path.exists(SITE): shutil.rmtree(SITE)
    os.makedirs(SITE)
    copy_imgs(prods)
    dl=os.path.normpath(os.path.join(ROOT,"downloads"))
    if os.path.isdir(dl): shutil.copytree(dl, os.path.join(SITE,"downloads"))
    open(os.path.join(SITE, "site.css"), "w").write(BASE_CSS + EXTRA_CSS)
    open(os.path.join(SITE, "site.js"), "w").write(JS)
    open(rv_path, "w").write(kept_reviews if kept_reviews else json.dumps({"_note": "Add only real reviews, e.g. copied from Gumroad. Sections stay hidden while items is empty.", "items": []}, indent=2))
    open(os.path.join(SITE, "index.html"), "w").write(index_page(prods))
    for s, d in prods.items():
        open(os.path.join(SITE, s + ".html"), "w").write(product_page(d, prods))
    write_extras(prods)
    n = len(prods)
    print("built", n, "products; size", sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(SITE) for f in fs)//1024, "KB")

if __name__ == "__main__":
    main()
