#!/usr/bin/env python3
"""Retention and referral calculators.

Subcommands:
  metrics   churn, revenue churn, GRR/NRR, quick ratio from one period's numbers
  cohort    monthly retention table from a CSV (customer_id,start_month,end_month[,mrr])
  health    0-100 health score per account from a CSV of 0-100 component scores
  save      is a save offer worth it? (discount depth/length, save rate, post-save retention)
  dunning   value of improving failed-payment recovery
  referral  max reward, K-factor, referral ROI
"""
import argparse
import csv
import sys
from collections import defaultdict


def pct(x):
    return f"{x * 100:.1f}%"


def cmd_metrics(a):
    churn = a.churned / a.start_customers if a.start_customers else 0
    gross_rev_churn = (a.churned_mrr + a.contraction_mrr) / a.start_mrr
    net_rev_churn = (a.churned_mrr + a.contraction_mrr - a.expansion_mrr) / a.start_mrr
    grr = 1 - gross_rev_churn
    nrr = 1 - net_rev_churn
    lost = a.churned_mrr + a.contraction_mrr
    quick = (a.new_mrr + a.expansion_mrr) / lost if lost else float("inf")
    print(f"logo churn: {pct(churn)}/period  (annualized ≈ {pct(1 - (1 - churn) ** 12)} if monthly)")
    print(f"gross revenue churn: {pct(gross_rev_churn)}   net revenue churn: {pct(net_rev_churn)}")
    print(f"GRR: {pct(grr)}   NRR: {pct(nrr)}")
    print(f"quick ratio (new+expansion)/(churn+contraction): {quick:.2f}  (>= 4 strong, < 1 shrinking)")
    if a.involuntary is not None and a.churned:
        print(f"involuntary share of logo churn: {pct(a.involuntary / a.churned)}")
    if churn:
        print(f"implied average lifetime ≈ {1 / churn:.1f} periods")


def month_index(s):
    y, m = s.strip()[:7].split("-")
    return int(y) * 12 + int(m) - 1


def label(i):
    return f"{i // 12}-{i % 12 + 1:02d}"


def cmd_cohort(a):
    cohorts = defaultdict(list)
    with open(a.csv, newline="") as f:
        for row in csv.DictReader(f):
            s = month_index(row["start_month"])
            e = row.get("end_month", "").strip()
            e = month_index(e) if e else None
            mrr = float(row.get("mrr") or 1) if a.revenue else 1.0
            cohorts[s].append((e, mrr))
    if not cohorts:
        sys.exit("no rows")
    last = month_index(a.as_of) if a.as_of else max(
        max([e for e, _ in v if e is not None] + [k]) for k, v in cohorts.items())
    horizon = a.months
    head = "cohort    n     " + " ".join(f"M{m:<5}" for m in range(horizon + 1))
    print(head)
    for s in sorted(cohorts):
        rows = cohorts[s]
        base = sum(m for _, m in rows)
        cells = []
        for m in range(horizon + 1):
            if s + m > last:
                cells.append("  -   ")
                continue
            alive = sum(mrr for e, mrr in rows if e is None or e > s + m)
            cells.append(f"{alive / base * 100:5.1f}%")
        print(f"{label(s)}  {len(rows):<5} " + " ".join(cells))
    print("\nread: flattening curve = retained core exists; compare rows for improvement; "
          "M1 drop = activation problem.")


DEFAULT_WEIGHTS = {"logins": 0.30, "features": 0.25, "support": 0.15, "billing": 0.15, "engagement": 0.15}


def band(score):
    if score >= 80:
        return "healthy: expansion candidate"
    if score >= 60:
        return "watch: proactive check-in"
    if score >= 40:
        return "at risk: intervention play"
    return "critical: personal outreach"


def cmd_health(a):
    weights = dict(DEFAULT_WEIGHTS)
    if a.weights:  # replaces the defaults, so only the components you name count
        weights = {}
        for kv in a.weights.split(","):
            k, v = kv.split("=")
            weights[k.strip()] = float(v)
    with open(a.csv, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("no rows")
    absent = [k for k in weights if k not in rows[0]]
    if absent:
        print(f"note: no column for {', '.join(absent)}; scored on the remaining components", file=sys.stderr)
    out = []
    for r in rows:
        have = {k: w for k, w in weights.items() if str(r.get(k) or "").strip() != ""}
        if not have:
            out.append((0.0, r.get("account", "?"), ["no component data"]))
            continue
        score = sum(float(r[k]) * w for k, w in have.items()) / sum(have.values())
        missing = [k for k in weights if k in r and k not in have]
        flags = [f"missing {', '.join(missing)}"] if missing else []
        if r.get("export", "").lower() in ("1", "yes", "true"):
            score = min(score, 39)
            flags.append("data export")
        if r.get("seats_removed", "").lower() in ("1", "yes", "true"):
            flags.append("seats removed")
        out.append((score, r.get("account", "?"), flags))
    for score, acct, flags in sorted(out):
        extra = f"  [{', '.join(flags)}]" if flags else ""
        print(f"{acct:<24} {score:5.1f}  {band(score)}{extra}")


def cmd_save(a):
    # Without offer: customer churns now. With offer: a share accept; of those, a share are still
    # around after the discount ends and then follow normal churn.
    m = a.mrr
    base_life = 1 / a.monthly_churn
    disc_rev = m * (1 - a.discount) * a.months
    after_rev = m * base_life * a.post_retention
    value_per_accept = disc_rev + after_rev
    per_session = a.accept_rate * value_per_accept
    # Cost of training customers: some share of would-have-stayed users who learn to threaten cancel
    leak = a.abuse_share * m * a.discount * a.months
    print(f"value per accepted offer: ${value_per_accept:,.0f} "
          f"(discount period ${disc_rev:,.0f} + after ${after_rev:,.0f})")
    print(f"expected value per cancel session: ${per_session:,.0f}; abuse cost per session ≈ ${leak:,.0f}")
    print(f"net per cancel session: ${per_session - leak:,.0f}")
    if a.discount > 0.30:
        print("warning: discounts above ~30% tend to train cancel-for-discount behavior")
    if a.post_retention < 0.5:
        print("warning: under half of saved customers survive the offer period; fix the reason, not the price")


def cmd_dunning(a):
    now = a.failed_mrr * a.current
    target = a.failed_mrr * a.target
    gain_m = target - now
    life = 1 / a.monthly_churn if a.monthly_churn else 12
    print(f"recovered MRR: ${now:,.0f} → ${target:,.0f} per month (+${gain_m:,.0f})")
    keep = 1 - (a.monthly_churn or 0)
    cash = sum(gain_m * sum(keep ** t for t in range(12 - k)) for k in range(12))
    print(f"lifetime value of one month's extra recovery ≈ ${gain_m * life:,.0f} "
          f"(+${gain_m:,.0f} MRR × {life:.1f}-month average lifetime)")
    print(f"per year of sustained improvement ≈ ${gain_m * 12 * life:,.0f} lifetime value; "
          f"first-year cash ≈ ${cash:,.0f}")
    if a.cost:
        print(f"simple monthly ROI vs tooling: {gain_m / a.cost:.1f}x")


def cmd_referral(a):
    max_reward = a.ltv * a.margin - a.target_cac
    print(f"max total reward per referred customer: ${max_reward:,.0f} "
          f"(LTV ${a.ltv:,.0f} × margin {a.margin:.0%} − target CAC ${a.target_cac:,.0f})")
    if a.invites is not None and a.conv is not None:
        k = a.invites * a.conv
        print(f"K-factor: {a.invites} × {a.conv:.1%} = {k:.2f} "
              f"({'self-sustaining' if k > 1 else 'amplifier, not engine'})")
        if k < 1:
            print(f"each paid/organic customer yields ≈ {1 / (1 - k):.2f} customers including referral chains")
    if a.referred and a.reward is not None:
        cost = a.referred * a.reward + (a.fixed or 0)
        rev = a.referred * a.ltv * a.margin
        print(f"program cost ${cost:,.0f}; margin from referred ${rev:,.0f}; ROI {(rev - cost) / cost:.1f}x; "
              f"cost per referred customer ${cost / a.referred:,.0f}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    m = sp.add_parser("metrics")
    m.add_argument("--start-customers", type=float, required=True)
    m.add_argument("--churned", type=float, required=True)
    m.add_argument("--involuntary", type=float)
    m.add_argument("--start-mrr", type=float, required=True)
    m.add_argument("--churned-mrr", type=float, required=True)
    m.add_argument("--contraction-mrr", type=float, default=0)
    m.add_argument("--expansion-mrr", type=float, default=0)
    m.add_argument("--new-mrr", type=float, default=0)
    m.set_defaults(f=cmd_metrics)

    c = sp.add_parser("cohort")
    c.add_argument("csv")
    c.add_argument("--months", type=int, default=6)
    c.add_argument("--as-of", help="YYYY-MM; default = latest month in data")
    c.add_argument("--revenue", action="store_true", help="weight by mrr column")
    c.set_defaults(f=cmd_cohort)

    h = sp.add_parser("health")
    h.add_argument("csv", help="columns: account,logins,features,support,billing,engagement[,export,seats_removed]")
    h.add_argument("--weights", help="replaces the default weights; e.g. logins=0.4,features=0.3,support=0.1,billing=0.1,engagement=0.1")
    h.set_defaults(f=cmd_health)

    s = sp.add_parser("save")
    s.add_argument("--mrr", type=float, required=True)
    s.add_argument("--discount", type=float, default=0.25)
    s.add_argument("--months", type=int, default=3)
    s.add_argument("--accept-rate", type=float, default=0.2)
    s.add_argument("--post-retention", type=float, default=0.6,
                   help="share of accepters still paying when the discount ends")
    s.add_argument("--monthly-churn", type=float, default=0.04)
    s.add_argument("--abuse-share", type=float, default=0.02,
                   help="cancel sessions that are bargaining by customers who would have stayed")
    s.set_defaults(f=cmd_save)

    d = sp.add_parser("dunning")
    d.add_argument("--failed-mrr", type=float, required=True)
    d.add_argument("--current", type=float, required=True)
    d.add_argument("--target", type=float, required=True)
    d.add_argument("--monthly-churn", type=float, default=0.03)
    d.add_argument("--cost", type=float, default=0)
    d.set_defaults(f=cmd_dunning)

    r = sp.add_parser("referral")
    r.add_argument("--ltv", type=float, required=True)
    r.add_argument("--margin", type=float, default=0.75)
    r.add_argument("--target-cac", type=float, required=True)
    r.add_argument("--invites", type=float)
    r.add_argument("--conv", type=float)
    r.add_argument("--referred", type=float)
    r.add_argument("--reward", type=float, help="total reward cost per referred customer (both sides)")
    r.add_argument("--fixed", type=float, help="tooling + management cost for the period")
    r.set_defaults(f=cmd_referral)

    a = p.parse_args()
    try:
        a.f(a)
    except FileNotFoundError as e:
        sys.exit(f"cannot read {e.filename}: no such file")


if __name__ == "__main__":
    main()
