#!/usr/bin/env python3
"""Pricing and offer math (standard library only).

Subcommands
  unit        LTV, LTV:CAC, CAC payback from ARPA, margin, churn, CAC
  increase    break-even churn/loss for a price increase on existing customers
  discount    extra conversions needed to make a discount pay for itself
  annual      effective discount and cash impact of an annual plan
  crossover   GMV where a %-of-revenue platform overtakes a flat-fee one
  vw          Van Westendorp price points from a CSV of survey answers
  guarantee   refund-cost stress test for a guarantee

Examples
  pricing_calc.py unit --arpa 79 --margin 0.8 --churn 0.03 --cac 450
  pricing_calc.py increase --old 49 --new 59 --customers 1200
  pricing_calc.py discount --price 99 --discount 0.2 --margin 0.8
  pricing_calc.py annual --monthly 35 --annual-monthly 29
  pricing_calc.py crossover --flat 199 --base 49 --rate 0.02
  pricing_calc.py vw --csv answers.csv   # columns: too_cheap,cheap,expensive,too_expensive
  pricing_calc.py guarantee --price 997 --refund-rate 0.08 --delivery-cost 150 --buyers 100
"""
import argparse
import csv
import sys


def unit(a):
    if not 0 < a.churn < 1:
        sys.exit("--churn must be a monthly rate between 0 and 1 (e.g. 0.02); with no churn data, use 0.03 and say so")
    gm = a.arpa * a.margin
    life = 1 / a.churn
    ltv = gm * life
    print(f"gross margin per account/month: {gm:,.2f}")
    print(f"expected lifetime: {life:,.1f} months (1 / {a.churn:.1%} monthly churn)")
    print(f"LTV (gross-margin): {ltv:,.0f}")
    if a.cac:
        ratio = ltv / a.cac
        payback = a.cac / gm
        print(f"LTV:CAC = {ratio:.1f}  (healthy ≥ 3; < 1 loses money; > 5 may mean under-investing in growth)")
        print(f"CAC payback = {payback:.1f} months  (SMB self-serve aim ≤ 12; mid-market ≤ 18; enterprise ≤ 24)")
    if a.churn < 0.01:
        print("note: churn < 1%/month makes simple LTV explode; cap lifetime at 3-5 years for decisions.")


def increase(a):
    lift = a.new / a.old - 1
    # revenue neutral if retained share r satisfies r*new = old
    breakeven_loss = 1 - a.old / a.new
    print(f"price change: {a.old:,.2f} → {a.new:,.2f} ({lift:+.1%})")
    print(f"revenue-neutral if you lose up to {breakeven_loss:.1%} of affected customers")
    if a.customers:
        lost = a.customers * breakeven_loss
        print(f"= {lost:,.0f} of {a.customers:,.0f} customers; every customer kept beyond that is pure gain")
        for loss in (0.02, 0.05, 0.10):
            mrr = a.customers * (1 - loss) * a.new - a.customers * a.old
            print(f"  if {loss:.0%} leave: MRR change {mrr:+,.0f}/month")
    print("roll out to new customers first, then 5-10% of existing, watch churn and tickets for a cycle.")


def discount(a):
    new_price = a.price * (1 - a.discount)
    m_old = a.price * a.margin
    m_new = new_price - a.price * (1 - a.margin)  # unit cost unchanged
    if m_new <= 0:
        sys.exit("discount wipes out the margin entirely")
    need = m_old / m_new - 1
    print(f"price {a.price:,.2f} → {new_price:,.2f} ({a.discount:.0%} off), unit margin {m_old:,.2f} → {m_new:,.2f}")
    print(f"you need {need:+.0%} more sales just to earn the same gross profit")
    print("and discount-acquired customers often churn faster; prefer bonuses, guarantees, or upgrade-only discounts.")


def annual(a):
    disc = 1 - a.annual_monthly / a.monthly
    months_free = 12 * disc
    print(f"annual discount: {disc:.1%} (≈ {months_free:.1f} months free); typical range 15-20% ('2 months free' = 16.7%)")
    print(f"cash up front per annual customer: {a.annual_monthly * 12:,.2f} vs {a.monthly:,.2f}/month")
    if a.monthly_churn:
        mrev = a.monthly * sum((1 - a.monthly_churn) ** i for i in range(12))
        print(f"expected first-year revenue from a monthly customer at {a.monthly_churn:.1%} churn: {mrev:,.2f} "
              f"vs annual {a.annual_monthly * 12:,.2f}")


def crossover(a):
    x = (a.flat - a.base) / a.rate
    print(f"%-of-revenue plan ({a.base:,.0f} + {a.rate:.1%} of GMV) costs more than flat {a.flat:,.0f} above GMV {x:,.0f}/month")
    for g in (x / 2, x, x * 2, x * 5):
        print(f"  GMV {g:>10,.0f}: flat {a.flat:,.0f} vs % plan {a.base + a.rate * g:,.0f}")


def vw(a):
    rows = []
    skipped = 0

    def num(v):
        return float(str(v).replace("$", "").replace(",", "").strip())

    with open(a.csv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({k: num(r[k]) for k in ("too_cheap", "cheap", "expensive", "too_expensive")})
            except (KeyError, ValueError, TypeError):
                skipped += 1
    if skipped:
        print(f"skipped {skipped} row(s) with missing or non-numeric answers")
    n = len(rows)
    if not n:
        sys.exit("no usable rows; need columns too_cheap,cheap,expensive,too_expensive")
    if n < 30:
        print(f"warning: only {n} valid responses; aim for 100-300 per segment")
    # drop illogical answers
    rows = [r for r in rows if r["too_cheap"] <= r["cheap"] <= r["expensive"] <= r["too_expensive"]]
    prices = sorted({v for r in rows for v in r.values()})
    m = len(rows)

    def share(key, p, ge):
        return sum(1 for r in rows if (r[key] <= p if ge else r[key] >= p)) / m

    curves = []
    for p in prices:
        curves.append((p,
                       share("too_cheap", p, False),   # % saying too cheap at or above p (falls with p)
                       share("cheap", p, False),       # % saying bargain at or above p (falls)
                       share("expensive", p, True),    # % saying expensive at or below p (rises)
                       share("too_expensive", p, True)))  # % saying too expensive at or below p (rises)

    def cross(i_fall, i_rise):
        for p, *v in curves:
            if v[i_rise] >= v[i_fall]:
                return p
        return None

    pmc = cross(0, 2)   # too cheap vs expensive
    opp = cross(0, 3)   # too cheap vs too expensive
    idp = cross(1, 2)   # cheap vs expensive
    pme = cross(1, 3)   # cheap vs too expensive
    print(f"valid logical responses: {m} of {n}")
    print(f"Point of marginal cheapness (PMC):     {pmc}")
    print(f"Optimal price point (OPP):             {opp}")
    print(f"Indifference price point (IDP):        {idp}")
    print(f"Point of marginal expensiveness (PME): {pme}")
    print(f"acceptable range PMC-PME; price inside OPP-IDP unless positioning says premium.")


def guarantee(a):
    refunds = a.buyers * a.refund_rate
    cost = refunds * (a.price + a.delivery_cost_refunded)
    rev = a.buyers * a.price
    print(f"{a.buyers:,.0f} buyers × {a.price:,.2f} = {rev:,.0f}")
    print(f"refund rate {a.refund_rate:.0%} → {refunds:,.1f} refunds costing {cost:,.0f} ({cost / rev:.1%} of revenue)")
    for rr in (0.10, 0.20):
        c = a.buyers * rr * (a.price + a.delivery_cost_refunded)
        print(f"  stress test at {rr:.0%}: {c:,.0f} ({c / rev:.1%} of revenue)")
    print("a guarantee pays if the conversion lift exceeds this cost; check with a test, not a hunch.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("unit"); p.add_argument("--arpa", type=float, required=True); p.add_argument("--margin", type=float, default=0.8)
    p.add_argument("--churn", type=float, required=True, help="monthly logo/revenue churn, e.g. 0.03"); p.add_argument("--cac", type=float, default=0); p.set_defaults(f=unit)
    p = s.add_parser("increase"); p.add_argument("--old", type=float, required=True); p.add_argument("--new", type=float, required=True)
    p.add_argument("--customers", type=float, default=0); p.set_defaults(f=increase)
    p = s.add_parser("discount"); p.add_argument("--price", type=float, required=True); p.add_argument("--discount", type=float, required=True)
    p.add_argument("--margin", type=float, default=0.8); p.set_defaults(f=discount)
    p = s.add_parser("annual"); p.add_argument("--monthly", type=float, required=True); p.add_argument("--annual-monthly", type=float, required=True)
    p.add_argument("--monthly-churn", type=float, default=0); p.set_defaults(f=annual)
    p = s.add_parser("crossover"); p.add_argument("--flat", type=float, required=True); p.add_argument("--base", type=float, required=True)
    p.add_argument("--rate", type=float, required=True); p.set_defaults(f=crossover)
    p = s.add_parser("vw"); p.add_argument("--csv", required=True); p.set_defaults(f=vw)
    p = s.add_parser("guarantee"); p.add_argument("--price", type=float, required=True); p.add_argument("--refund-rate", type=float, required=True)
    p.add_argument("--delivery-cost", dest="delivery_cost_refunded", type=float, default=0, help="non-recoverable cost per refunded buyer")
    p.add_argument("--buyers", type=float, default=100); p.set_defaults(f=guarantee)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
