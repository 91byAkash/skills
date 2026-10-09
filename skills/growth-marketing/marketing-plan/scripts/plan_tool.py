#!/usr/bin/env python3
"""plan_tool.py - calculators for marketing plans.

Subcommands
  ice       rank ideas from a CSV by impact x confidence x ease
  budget    goal-based or revenue-based marketing budget
  sizing    bottom-up / search-led / channel-led SOM with a triangulation check
  partners  score co-marketing partner candidates from a CSV
  rubric    total and shape of a 17-area current-state score CSV

Standard library only. Run `plan_tool.py <cmd> -h` for options.
"""
import argparse
import csv
import sys


# --------------------------------------------------------------------------
# ice
# --------------------------------------------------------------------------
def _num(row, key, lo=1, hi=10):
    try:
        v = float(row[key])
    except (KeyError, ValueError):
        raise SystemExit(f"row {row.get('idea') or row.get('partner') or row.get('area') or '?'}: '{key}' missing or not a number")
    if not lo <= v <= hi:
        raise SystemExit(f"row {row.get('idea') or row.get('partner') or row.get('area') or '?'}: '{key}'={v} outside {lo}-{hi}")
    return v


def cmd_ice(a):
    with open(a.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        i, c, e = _num(r, "impact"), _num(r, "confidence"), _num(r, "ease")
        cost = float(r.get("cost") or 0)
        out.append((i * c * e, r["idea"], i, c, e, cost, r.get("stage", "")))
    out.sort(key=lambda t: -t[0])
    spent = 0.0
    print(f"{'rank':<5}{'score':>6}  {'I':>3}{'C':>3}{'E':>3} {'cost':>8}  {'stage':<13}idea")
    for n, (s, idea, i, c, e, cost, stage) in enumerate(out, 1):
        tag = ""
        if a.budget is not None:
            if spent + cost <= a.budget:
                spent += cost
                tag = "  [funded]"
            else:
                tag = "  [over budget]"
        print(f"{n:<5}{s:>6.0f}  {i:>3.0f}{c:>3.0f}{e:>3.0f} {cost:>8.0f}  {stage:<13}{idea}{tag}")
    if a.budget is not None:
        print(f"funded cost {spent:,.0f} of budget {a.budget:,.0f}")
    low = [t[1] for t in out if t[3] <= 3]
    if low:
        print("Low confidence (<=3): run as small tests with a kill rule first: " + "; ".join(low))


# --------------------------------------------------------------------------
# budget
# --------------------------------------------------------------------------
def cmd_budget(a):
    ann = a.arpc * 12
    if a.method == "goal":
        if a.new_arr is None:
            sys.exit("goal method needs --new-arr")
        customers = a.new_arr / ann
        raw = customers * a.cac
        core = raw / a.retention
        total = core * (1 + a.buffer)
        print(f"ARR per new customer   {ann:,.0f}")
        print(f"customers needed       {customers:,.0f}")
        print(f"acquisition cost       {raw:,.0f}")
        print(f"churn-adjusted budget  {core:,.0f}  (/ {a.retention:.0%} retention)")
        print(f"{'+' + format(a.buffer, '.0%') + ' experiments':<23}{total:,.0f}  (~{total / 12:,.0f}/month)")
        if a.arr:
            pct = total / a.arr
            print(f"as % of current ARR    {pct:.0%}")
            if pct > 0.40:
                print("WARN: above ~40% of ARR. The goal is likely unfunded: lower it, "
                      "improve CAC or retention, or show the funding source.")
    else:
        if a.arr is None or a.pct is None:
            sys.exit("revenue method needs --arr and --pct")
        spend = a.arr * a.pct
        customers = spend / a.cac
        gross = customers * ann
        net = gross * a.retention
        print(f"annual budget          {spend:,.0f}  ({a.pct:.0%} of {a.arr:,.0f} ARR)")
        print(f"customers acquired     {customers:,.0f}")
        print(f"gross new ARR          {gross:,.0f}")
        print(f"net new ARR            {net:,.0f}  (x {a.retention:.0%} retention)")
        print(f"end-of-year ARR goal   {a.arr + net:,.0f}")
    if a.cac > 0:
        payback = a.cac / (a.arpc * a.margin)
        print(f"CAC payback            {payback:.1f} months at {a.margin:.0%} gross margin")


# --------------------------------------------------------------------------
# sizing
# --------------------------------------------------------------------------
def cmd_sizing(a):
    results = []
    if a.buyers and a.spend:
        sam = a.buyers * a.spend
        lo, hi = sam * a.capture[0], sam * a.capture[-1]
        print(f"bottom-up   SAM {sam:,.0f}/yr; SOM {lo:,.0f}-{hi:,.0f} at "
              f"{a.capture[0]:.1%}-{a.capture[-1]:.1%} capture")
        results.append(("bottom-up", lo, hi))
    if a.search:
        vol, share, v2t, t2p = a.search
        accts = vol * share * v2t * t2p * 12
        val = accts * (a.spend or 0)
        print(f"search-led  ~{accts:,.0f} accounts/yr -> {val:,.0f}/yr (one channel: a floor, not a SOM)")
    total = 0.0
    for ch in a.channel or []:
        try:
            name, per_month = ch.split(":")
            per_month = float(per_month)
        except ValueError:
            sys.exit("--channel format is name:new_accounts_per_month")
        v = per_month * 12 * (a.spend or 0)
        total += v
        print(f"channel     {name}: {per_month:g} accounts/month -> {v:,.0f}/yr")
    if a.channel:
        print(f"channel-led total {total:,.0f}/yr (capped by today's budget and headcount)")
        results.append(("channel-led", total, total))
    if len(results) == 2:
        mid = [(lo + hi) / 2 for _, lo, hi in results]
        ratio = max(mid) / min(mid) if min(mid) else float("inf")
        print(f"bottom-up vs channel-led midpoint ratio {ratio:.1f}x")
        if ratio > 3:
            print("WARN: more than 3x apart; one assumption is broken. Find it before quoting a number.")
        elif mid[0] > mid[1]:
            print("Demand exceeds what current channels reach: a budget/channel constraint, not a demand one.")
        else:
            print("Estimates broadly agree; quote the overlap as the working range.")


# --------------------------------------------------------------------------
# partners
# --------------------------------------------------------------------------
PARTNER_W = {"audience_fit": 3, "audience_size": 1, "brand": 2,
             "engagement": 2, "reciprocity": 1.5, "ease": 1.5}


def cmd_partners(a):
    with open(a.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    wsum = sum(PARTNER_W.values())
    out = []
    for r in rows:
        sc = {k: _num(r, k, 1, 5) for k in PARTNER_W}
        total = sum(sc[k] * w for k, w in PARTNER_W.items()) / wsum
        gate = "reject: audience fit" if sc["audience_fit"] < 3 else (
            "reject: brand" if sc["brand"] < 3 else "")
        out.append((total, r.get("partner", "?"), gate, r.get("idea", "")))
    out.sort(key=lambda t: -t[0])
    print(f"{'score':>5}  {'partner':<32}verdict")
    for total, name, gate, idea in out:
        verdict = gate or ("pursue" if total >= 3.8 else "maybe" if total >= 3 else "park")
        extra = f"  idea: {idea}" if idea and not gate else ""
        print(f"{total:>5.2f}  {name:<32}{verdict}{extra}")


# --------------------------------------------------------------------------
# rubric
# --------------------------------------------------------------------------
def cmd_rubric(a):
    with open(a.csv, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    scored = []
    for r in rows:
        s = str(r.get("score", "")).strip()
        if s.lower() in ("", "na", "n/a"):
            continue
        scored.append((float(s), r["area"]))
    if len(rows) != 17:
        print(f"WARN: expected 17 areas, got {len(rows)}")
    tot = sum(s for s, _ in scored)
    mx = 5 * len(scored)
    print(f"total {tot:.0f}/{mx} ({tot / mx:.0%}) across {len(scored)} scored areas")
    srt = sorted(scored)
    print("strongest: " + ", ".join(f"{n} {s:.0f}" for s, n in srt[::-1][:3]))
    exempt = [x.strip().lower() for x in a.exempt.split(",") if x.strip()]
    weak = [(s, n) for s, n in srt if n.lower() not in exempt]
    print("weakest:   " + ", ".join(f"{n} {s:.0f}" for s, n in weak[:3]))
    low_ex = [n for s, n in srt if n.lower() in exempt and s <= 1]
    if low_ex:
        print("low but stage-appropriate (not counted as gaps): " + ", ".join(low_ex))


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("ice")
    i.add_argument("--csv", required=True, help="columns: idea,impact,confidence,ease[,cost,stage]")
    i.add_argument("--budget", type=float, help="fund ideas in rank order until this is spent")
    i.set_defaults(fn=cmd_ice)

    b = sub.add_parser("budget")
    b.add_argument("method", choices=["goal", "revenue"])
    b.add_argument("--new-arr", type=float, help="goal: new ARR wanted this year")
    b.add_argument("--arr", type=float, help="current ARR")
    b.add_argument("--pct", type=float, help="revenue: share of ARR to spend (0.05-0.40)")
    b.add_argument("--arpc", type=float, required=True, help="avg monthly revenue per customer")
    b.add_argument("--cac", type=float, required=True, help="blended CAC (all marketing cost / new customers)")
    b.add_argument("--retention", type=float, default=0.85, help="annual customer retention")
    b.add_argument("--buffer", type=float, default=0.15, help="experimental layer on top")
    b.add_argument("--margin", type=float, default=0.8, help="gross margin for payback")
    b.set_defaults(fn=cmd_budget)

    s = sub.add_parser("sizing")
    s.add_argument("--buyers", type=float, help="reachable buyers (accounts)")
    s.add_argument("--spend", type=float, help="expected annual spend per account")
    s.add_argument("--capture", type=float, nargs="+", default=[0.01, 0.02])
    s.add_argument("--search", type=float, nargs=4, metavar=("VOL", "SHARE", "V2T", "T2P"),
                   help="monthly searches, click share, visit-to-trial, trial-to-paid")
    s.add_argument("--channel", action="append", help="name:new_accounts_per_month (repeat)")
    s.set_defaults(fn=cmd_sizing)

    p = sub.add_parser("partners")
    p.add_argument("--csv", required=True,
                   help="columns: partner," + ",".join(PARTNER_W) + "[,idea] scored 1-5")
    p.set_defaults(fn=cmd_partners)

    r = sub.add_parser("rubric")
    r.add_argument("--csv", required=True, help="columns: area,score (0-5 or NA)")
    r.add_argument("--exempt", default="Paid ads,International",
                   help="areas where a low score reflects stage, not failure")
    r.set_defaults(fn=cmd_rubric)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

