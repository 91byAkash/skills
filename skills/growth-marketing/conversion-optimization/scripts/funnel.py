#!/usr/bin/env python3
"""Funnel leak finder and upside calculator (standard library only).

Find the step that loses the most, and what a lift at each step is worth.

Usage:
  funnel.py --steps "Landing:12000" "Checkout start:900" "Purchase:380" --value 49
  funnel.py --steps "Signup:2000" "Onboarding done:1100" "Activated:640" "Paid:96" --value 600 --lift 0.10
  funnel.py --csv funnel.csv --value 49           # csv with columns step,count
  funnel.py upsell --orders 380 --aov 49 --take 0.18 --upsell-price 29 --downsell-take 0.08 --downsell-price 15

Benchmarks printed beside steps are rough cold-paid-traffic ranges; replace with the
account's own history when you have it.
"""
import argparse
import csv
import sys

BENCH = {
    "checkout": (0.05, 0.15, "landing → checkout start"),
    "purchase": (0.30, 0.60, "checkout start → purchase"),
    "opt": (0.20, 0.40, "opt-in page conversion"),
    "activ": (0.20, 0.40, "signup → activation (varies widely)"),
}


def parse_steps(items):
    out = []
    for it in items:
        name, _, n = it.rpartition(":")
        try:
            out.append((name.strip(), float(n.replace(",", ""))))
        except ValueError:
            sys.exit(f'bad step "{it}": use "Name:count"')
    return out


def bench_for(name):
    low = name.lower()
    for key, b in BENCH.items():
        if key in low:
            return b
    return None


def funnel(a):
    steps = parse_steps(a.steps) if a.steps else []
    if a.csv:
        with open(a.csv) as f:
            steps = [(r["step"], float(r["count"])) for r in csv.DictReader(f)]
    if len(steps) < 2:
        sys.exit("need at least two steps")
    top = steps[0][1]
    final = steps[-1][1]
    print(f"{'step':<28}{'count':>10}{'step conv':>11}{'cumulative':>12}{'lost':>10}")
    worst = None
    below = []
    bad_order = False
    for i, (name, n) in enumerate(steps):
        if i == 0:
            print(f"{name:<28}{n:>10,.0f}{'':>11}{'100.0%':>12}{'':>10}")
            continue
        prev = steps[i - 1][1]
        conv = n / prev if prev else 0
        lost = prev - n
        b = bench_for(name)
        note = f"   (typical {b[0]:.0%}-{b[1]:.0%} {b[2]})" if b else ""
        if b and conv < b[0]:
            below.append(f"{name} ({conv:.1%} vs typical >= {b[0]:.0%})")
        if n > prev:
            note += "   <-- more than the previous step: check event definitions and date windows"
            bad_order = True
        print(f"{name:<28}{n:>10,.0f}{conv:>11.1%}{n / top:>12.2%}{lost:>10,.0f}{note}")
        if worst is None or conv < worst[1]:
            worst = (name, conv)
    print()
    print(f"overall: {final / top:.2%} ({final:,.0f} of {top:,.0f})")
    msg = f"a {a.lift:.0%} relative lift at ANY single step adds ~{final * a.lift:,.0f} final conversions (multiplicative funnel)"
    if a.value:
        msg += f"; value ≈ {final * a.lift * a.value:,.0f} per period at {a.value:,.2f} each"
    print(msg + ("" if a.value else "; pass --value to price it"))
    if below:
        print("below typical range: " + "; ".join(below) + ". Start with the earliest one.")
    print(f"lowest step conversion: {worst[0]} ({worst[1]:.1%}). Audit that step first unless an earlier step"
          f" is below its benchmark (see above) or much cheaper to fix.")
    if top < 1000 or final < 30:
        print("note: volume is too low to separate real problems from noise; rank fixes by friction, not by these rates.")
    if bad_order:
        sys.exit("error: a step has more users than the step before it; fix the funnel data before trusting these numbers")


def upsell(a):
    base = a.orders * a.aov
    up = a.orders * a.take * a.upsell_price
    declined = a.orders * (1 - a.take)
    down = declined * a.downsell_take * a.downsell_price
    total = base + up + down
    print(f"base revenue: {base:,.2f} ({a.orders:,.0f} orders × {a.aov:,.2f})")
    print(f"upsell: {a.take:.0%} take × {a.upsell_price:,.2f} = {up:,.2f}")
    if a.downsell_price:
        print(f"downsell (to decliners): {a.downsell_take:.0%} × {a.downsell_price:,.2f} = {down:,.2f}")
    print(f"new AOV: {total / a.orders:,.2f} (+{total / base - 1:.1%})")
    if a.cpa:
        print(f"CPA {a.cpa:,.2f}: margin per order before {a.aov * a.margin - a.cpa:,.2f}, "
              f"after {(total / a.orders) * a.margin - a.cpa:,.2f} at {a.margin:.0%} gross margin")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    ap.add_argument("--steps", nargs="+", help='"Name:count" in funnel order')
    ap.add_argument("--csv")
    ap.add_argument("--value", type=float, default=0.0, help="value of one final conversion")
    ap.add_argument("--lift", type=float, default=0.10, help="relative lift to price out (default 0.10)")
    u = sub.add_parser("upsell")
    u.add_argument("--orders", type=float, required=True)
    u.add_argument("--aov", type=float, required=True)
    u.add_argument("--take", type=float, required=True)
    u.add_argument("--upsell-price", type=float, required=True)
    u.add_argument("--downsell-take", type=float, default=0.0)
    u.add_argument("--downsell-price", type=float, default=0.0)
    u.add_argument("--cpa", type=float, default=0.0)
    u.add_argument("--margin", type=float, default=0.7)
    a = ap.parse_args()
    if a.cmd == "upsell":
        upsell(a)
    else:
        funnel(a)


if __name__ == "__main__":
    main()
