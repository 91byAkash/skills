#!/usr/bin/env python3
"""Paid-ads calculators and copy checks.

Subcommands:
  economics  breakeven CPL/CPC/ROAS and payback (raw and retention-adjusted) per plan
  limits     check ad copy against platform character limits and common AI/hype tells
  zero       what "0 conversions in N clicks" can and cannot tell you; break-even CVR
  meta       ad-count ceiling, test throughput, proven-ad inventory and test verdicts from a target cost per qualified lead
  scale      budget step plan (+20% every 5 days by default) with rollback trigger
  review     render a simple self-contained HTML review page from a concepts JSON file
"""
import argparse
import html
import json
import math
import re
import sys


# ---------- economics ----------
def cmd_economics(a):
    if a.acv and a.close:
        cpl = a.acv * a.close
        print(f"breakeven CPL = ACV ${a.acv:,.0f} × lead→close {a.close:.1%} = ${cpl:,.0f}")
        if a.margin_target:
            print(f"target CPL at {a.margin_target:.0%} safety margin = ${cpl * (1 - a.margin_target):,.0f}")
        if a.lp_cvr:
            print(f"breakeven CPC = CPL × LP conversion {a.lp_cvr:.1%} = ${cpl * a.lp_cvr:,.2f}")
    if a.aov and a.gross_margin:
        be_roas = 1 / a.gross_margin
        print(f"breakeven ROAS (first order) = 1 ÷ gross margin {a.gross_margin:.0%} = {be_roas:.2f}")
        if a.repeat_factor:
            print(f"breakeven ROAS with {a.repeat_factor:.1f}× lifetime orders = {be_roas / a.repeat_factor:.2f}")
    if a.cac and a.arpu:
        plans = list(zip(a.plan or [f"plan{i + 1}" for i in range(len(a.arpu))], a.arpu))
        print(f"\npayback at CAC ${a.cac:,.0f}:")
        for name, arpu in plans:
            raw = a.cac / (arpu * (a.gross_margin or 1))
            line = f"  {name:<12} ARPU ${arpu:,.0f}: {raw:5.1f} months"
            if a.retention:
                adj = a.cac / (arpu * (a.gross_margin or 1) * a.retention)
                line += f"  | retention-adjusted ({a.retention:.0%}): {adj:5.1f} months"
                raw = adj
            verdict = "fund" if raw <= 12 else "don't fund with paid; route to organic/product-led"
            if raw < 3:
                verdict = "fund and push harder (very fast payback)"
            print(line + f"  → {verdict}")
        if a.gross_margin:
            print("  (payback uses gross-margin ARPU)")
        else:
            print("  (payback on revenue ARPU, which flatters it; pass --gross-margin 0.8 etc. for gross-margin payback)")


# ---------- limits ----------
LIMITS = {
    # field: (hard max, recommended, min count, max count)
    "google-rsa": {"H": (30, None, 3, 15), "D": (90, None, 2, 4), "P": (15, None, 0, 2)},
    "pmax": {"H": (30, None, 3, 15), "L": (90, None, 1, 5), "D": (90, None, 2, 5), "B": (25, None, 1, 1)},
    "meta": {"T": (2200, 125, 1, 5), "H": (255, 40, 1, 5), "D": (255, 30, 0, 5)},
    "linkedin": {"T": (600, 150, 1, 1), "H": (200, 70, 1, 1), "D": (300, 100, 0, 1)},
    "linkedin-carousel": {"T": (255, None, 1, 1), "H": (45, None, 2, 10)},
    "tiktok": {"T": (100, 80, 1, 5)},
    "x": {"T": (280, None, 1, 1), "H": (70, None, 0, 1), "D": (200, None, 0, 1)},
}
FIELD_NAMES = {"H": "headline", "D": "description", "P": "path", "L": "long headline",
               "T": "primary/intro text", "B": "business name"}
TELLS = [
    (r"—", "em dash"),
    (r"\bit'?s not (just )?\w+[,;] it'?s\b", "contrast reveal"),
    (r"\bsay goodbye to\b", "stock phrase"),
    (r"\bunlock (the )?(power|potential)\b", "stock phrase"),
    (r"\bnext level\b", "stock phrase"),
    (r"\breimagined\b", "stock phrase"),
    (r"\bstop scrolling\b", "hook slop"),
    (r"\bget started today\b", "CTA slop"),
    (r"\bjoin thousands\b", "CTA slop (name the action and payoff)"),
    (r"\b(best|#1|leading|world-class|revolutionary)\b", "unsubstantiated superlative"),
    (r"!{2,}", "stacked exclamation"),
    (r"\b(guaranteed|cure[sd]?|risk-free)\b", "regulated-claim word: check policy"),
]
CTA_WORDS = r"\b(start|get|try|book|see|claim|download|join|sign up|shop|buy|request|watch|calculate|compare)\b"


def cmd_limits(a):
    spec = LIMITS[a.platform]
    items = {k: [] for k in spec}
    with open(a.file) as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            m = re.match(r"^\s*([A-Z])\s*[:|]\s*(.*)$", line)
            if not m or m.group(1) not in spec:
                print(f"line {ln}: skipped (use one of {', '.join(k + ':' for k in spec)})")
                continue
            items[m.group(1)].append(m.group(2).strip())
    problems = 0
    for key, (hard, rec, mn, mx) in spec.items():
        texts = items[key]
        name = FIELD_NAMES[key]
        if len(texts) < mn or len(texts) > mx:
            print(f"COUNT  {name}: {len(texts)} (allowed {mn}-{mx})")
            problems += 1
        seen = set()
        for i, t in enumerate(texts, 1):
            n = len(t)
            flag = ""
            if n > hard:
                flag = f"OVER by {n - hard}"
                problems += 1
            elif rec and n > rec:
                flag = f"truncates after ~{rec}"
            norm = re.sub(r"\W+", " ", t.lower()).strip()
            if norm in seen:
                flag += " DUPLICATE"
                problems += 1
            seen.add(norm)
            for pat, label in TELLS:
                if re.search(pat, t, re.I):
                    flag += f" [{label}]"
            if re.search(r"\b[A-Z]{4,}\b", t) and not re.search(r"\b(SOC|GDPR|HIPAA|API|CRM|SEO|ROI)\b", t):
                flag += " [all caps]"
            print(f"{name[:12]:<12} {i:>2} ({n:>3}) {t}{'  <- ' + flag.strip() if flag else ''}")
    if a.platform == "google-rsa":
        hs = items["H"]
        if hs and not any(re.search(CTA_WORDS, h, re.I) for h in hs):
            print("MIX    no CTA headline; add 2-3")
            problems += 1
        if a.keyword and not any(a.keyword.lower() in h.lower() for h in hs):
            print(f"MIX    no headline contains the keyword '{a.keyword}'")
            problems += 1
        if hs and len(hs) < 10:
            print("MIX    fewer than 10 headlines limits combinations; aim for 12-15 distinct ones")
    print(f"\n{'ok' if problems == 0 else str(problems) + ' problem(s)'}")
    sys.exit(1 if problems else 0)


# ---------- zero ----------
def cmd_zero(a):
    # One-sided 95% upper bound on CVR when 0 successes in n trials: 1 - 0.05^(1/n)
    rows = a.clicks or [5, 10, 30, 50, 100, 200]
    print("clicks  rules out CVR >=")
    for n in rows:
        print(f"{n:>6}  {1 - 0.05 ** (1 / n):6.1%}")
    if a.cpc and a.target_cpa:
        be = a.cpc / a.target_cpa
        need = math.ceil(math.log(0.05) / math.log(1 - be)) if 0 < be < 1 else None
        print(f"\nbreak-even CVR = CPC ${a.cpc:.2f} ÷ target CPA ${a.target_cpa:,.0f} = {be:.2%}")
        if need:
            print(f"clicks needed before 0 conversions shows the term is below break-even: ~{need}")
            if a.clicks_per_month:
                print(f"at {a.clicks_per_month:.0f} clicks/month that is ~{need / a.clicks_per_month:.1f} months"
                      f" (spend ≈ ${need * a.cpc:,.0f})")


# ---------- meta ----------
def cmd_meta(a):
    t = a.tcpl
    ceiling = a.daily_budget * 14 / (2 * t)
    print(f"ad-count ceiling = daily ${a.daily_budget:,.0f} × 14 ÷ (2 × TCPL ${t:,.0f}) = {ceiling:.0f} ads "
          f"(run ~{max(1, round(ceiling * 0.5))}-{max(1, round(ceiling * 0.7))})")
    monthly = a.daily_budget * 30.4
    thru = monthly * a.test_share / (3 * t)
    print(f"test throughput ≈ {thru:.1f} concept reads/month at {a.test_share:.0%} test budget "
          f"(often 1.5-2× with early delivery kills)")
    print(f"expected winners/month at ~1 in 6: {thru / 6:.1f}")
    inv = monthly / a.per_ad
    print(f"proven-ad inventory needed ≈ {inv:.0f} (each absorbs ~${a.per_ad:,.0f}/month before fatigue)")
    if a.spend is not None:
        print("\nverdict for one test ad (rolling 14 days):")
        if a.spend < 3 * t:
            print(f"  wait: spend ${a.spend:,.0f} < 3× TCPL (${3 * t:,.0f})")
            return
        if not a.leads:
            print("  swap and abandon concept: no leads at ≥3× TCPL")
            return
        q = a.qualified or 0
        rate = q / a.leads
        if q == 0:
            print("  swap: leads but none qualified; keep format, change angle")
            return
        if rate < 0.4:
            print(f"  swap: qualified rate {rate:.0%} < 40%; add ICP-filtering language")
            return
        cpq = a.spend / q
        status = "candidate winner" if cpq <= t else ("monitor" if cpq <= 1.5 * t else "swap: cost >1.5× TCPL")
        if 0.4 <= rate < 0.6:
            status += " (qualified rate 40-60%: monitor one more week)"
        print(f"  cost per qualified lead ${cpq:,.0f} vs TCPL ${t:,.0f}: {status}")


# ---------- scale ----------
def cmd_scale(a):
    b, day = a.start, 0
    print(f"day {day:>3}: ${b:,.0f}/day")
    while b < a.target:
        b = min(a.target, b * (1 + a.step))
        day += a.every
        print(f"day {day:>3}: ${b:,.0f}/day")
    print(f"\nreach ${a.target:,.0f}/day in ~{day} days. Rollback: if cost per result >1.5× target after a step, "
          f"cut 20-30%, hold 2 weeks, resume at +10%/week.")


# ---------- review ----------
PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>
<style>*{{box-sizing:border-box}}body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#222}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:1rem}}
.card{{border:1px solid #ddd;border-radius:10px;padding:1rem}}.tag{{font-size:.75rem;background:#eef;padding:2px 6px;border-radius:4px}}
.frame{{background:#f5f5f5;border-radius:8px;padding:.75rem;margin:.5rem 0;font-size:.9rem}}
img{{max-width:100%;border-radius:6px}}small{{color:#666}}label{{display:block;margin-top:.5rem}}</style></head>
<body><h1>{title}</h1><p>{note}</p><div class="grid">{cards}</div>
<p><small>Tick your picks, then print or save this page as PDF to send back.</small></p></body></html>"""


def cmd_review(a):
    data = json.load(open(a.file))
    cards = []
    for i, c in enumerate(data.get("concepts", []), 1):
        frames = "".join(
            f'<div class="frame"><b>{html.escape(fr.get("label", ""))}</b><br>'
            + (f'<img src="{html.escape(fr["image"])}" alt="">' if fr.get("image") else
               f'<i>{html.escape(fr.get("visual", ""))}</i>')
            + (f'<p>{html.escape(fr.get("headline", ""))}</p>' if fr.get("headline") else "") + "</div>"
            for fr in c.get("frames", []))
        heads = "".join(f"<li>{html.escape(h)} <small>({len(h)})</small></li>" for h in c.get("headlines", []))
        cards.append(
            f'<div class="card"><span class="tag">{html.escape(c.get("format", ""))}</span> '
            f'<span class="tag">{html.escape(c.get("stage", ""))}</span>'
            f'<h3>{i}. {html.escape(c.get("name", "Concept"))}</h3><p>{html.escape(c.get("primary_text", ""))}</p>'
            f'{frames}<ul>{heads}</ul><small>Grounded in: {html.escape(c.get("grounding", "MISSING"))}</small>'
            f'<label><input type="checkbox"> Pick</label><label>Notes <input style="width:100%"></label></div>')
    out = PAGE.format(title=html.escape(data.get("title", "Creative review")),
                      note=html.escape(data.get("note", "")), cards="".join(cards))
    if a.out:
        open(a.out, "w").write(out)
        print(f"wrote {a.out} ({len(cards)} concepts)")
    else:
        print(out)
    missing = [c.get("name") for c in data.get("concepts", []) if not c.get("grounding")]
    if missing:
        print(f"warning: no grounding source for: {', '.join(map(str, missing))}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    e = sp.add_parser("economics")
    e.add_argument("--acv", type=float)
    e.add_argument("--close", type=float, help="lead-to-close rate")
    e.add_argument("--lp-cvr", type=float)
    e.add_argument("--margin-target", type=float, help="safety margin below breakeven, e.g. 0.3")
    e.add_argument("--aov", type=float)
    e.add_argument("--gross-margin", type=float)
    e.add_argument("--repeat-factor", type=float, help="lifetime orders per customer")
    e.add_argument("--cac", type=float)
    e.add_argument("--arpu", type=float, nargs="+")
    e.add_argument("--plan", nargs="+")
    e.add_argument("--retention", type=float, help="annual retention for adjusted payback")
    e.set_defaults(f=cmd_economics)

    li = sp.add_parser("limits")
    li.add_argument("file", help="lines like 'H: headline', 'D: description', 'P: path', 'T: primary text'")
    li.add_argument("--platform", choices=sorted(LIMITS), default="google-rsa")
    li.add_argument("--keyword")
    li.set_defaults(f=cmd_limits)

    z = sp.add_parser("zero")
    z.add_argument("--clicks", type=int, nargs="+")
    z.add_argument("--cpc", type=float)
    z.add_argument("--target-cpa", type=float)
    z.add_argument("--clicks-per-month", type=float)
    z.set_defaults(f=cmd_zero)

    m = sp.add_parser("meta")
    m.add_argument("--tcpl", type=float, required=True, help="target cost per qualified lead")
    m.add_argument("--daily-budget", type=float, required=True)
    m.add_argument("--test-share", type=float, default=0.2)
    m.add_argument("--per-ad", type=float, default=5000, help="monthly spend one proven ad absorbs")
    m.add_argument("--spend", type=float)
    m.add_argument("--leads", type=int)
    m.add_argument("--qualified", type=int)
    m.set_defaults(f=cmd_meta)

    s = sp.add_parser("scale")
    s.add_argument("--start", type=float, required=True)
    s.add_argument("--target", type=float, required=True)
    s.add_argument("--step", type=float, default=0.2)
    s.add_argument("--every", type=int, default=5)
    s.set_defaults(f=cmd_scale)

    r = sp.add_parser("review")
    r.add_argument("file")
    r.add_argument("--out")
    r.set_defaults(f=cmd_review)

    a = p.parse_args()
    try:
        a.f(a)
    except FileNotFoundError as e:
        sys.exit(f"cannot read {e.filename}: no such file")


if __name__ == "__main__":
    main()
