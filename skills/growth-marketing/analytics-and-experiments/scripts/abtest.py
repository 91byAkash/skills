#!/usr/bin/env python3
"""A/B test calculator: sample size, duration, result analysis, SRM check.

Standard library only. Two-sided tests on conversion rates (proportions).

Examples
  abtest.py size --baseline 0.04 --mde 0.15                 # relative MDE (15% lift)
  abtest.py size --baseline 0.04 --mde 0.006 --absolute      # absolute MDE (+0.6 pts)
  abtest.py size --baseline 0.04 --mde 0.15 --variants 3 --power 0.9
  abtest.py duration --baseline 0.04 --mde 0.15 --daily 1800 --exposed 0.5
  abtest.py mde --baseline 0.04 --daily 1800 --days 28       # smallest lift detectable
  abtest.py analyze --control 9800 412 --variant 9750 468
  abtest.py srm --counts 10120 9880 --split 50 50       # exit 1 if SRM
  abtest.py table                                            # quick-reference table
"""
import argparse
import math
import sys
from statistics import NormalDist

N = NormalDist()


def z(p):
    return N.inv_cdf(p)


def n_per_variant(p1, p2, alpha=0.05, power=0.8, comparisons=1):
    """Per-variant sample size for a two-sided two-proportion z-test.

    comparisons > 1 applies a Bonferroni correction to alpha.
    """
    if not (0 < p1 < 1 and 0 < p2 < 1) or p1 == p2:
        raise ValueError("rates must be in (0,1) and differ")
    a = alpha / comparisons
    za, zb = z(1 - a / 2), z(power)
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (p2 - p1) ** 2)


def target_rate(baseline, mde, absolute):
    return baseline + mde if absolute else baseline * (1 + mde)


def cmd_size(a):
    p2 = target_rate(a.baseline, a.mde, a.absolute)
    comps = max(1, a.variants - 1)
    n = n_per_variant(a.baseline, p2, a.alpha, a.power, comps)
    print(f"baseline {a.baseline:.4%} -> target {p2:.4%} "
          f"(relative lift {p2 / a.baseline - 1:+.1%}, absolute {p2 - a.baseline:+.4%})")
    print(f"alpha {a.alpha} two-sided{' (Bonferroni over %d comparisons)' % comps if comps > 1 else ''}, power {a.power}")
    print(f"sample per variant: {n:,}")
    print(f"total ({a.variants} arms incl. control): {n * a.variants:,}")
    return n


def cmd_duration(a):
    n = cmd_size(a)
    eff = a.daily * a.exposed
    days = math.ceil(n * a.variants / eff)
    weeks = math.ceil(days / 7)
    print(f"eligible traffic/day in test: {eff:,.0f}")
    print(f"raw duration: {days} days -> run {max(weeks, 1) * 7} days ({max(weeks, 1)} full weeks, minimum 7)")
    if days > 56:
        print("VERDICT: not feasible (> 8 weeks). Raise the MDE, test upstream with more traffic, "
              "pool similar pages, drop variants, or decide on qualitative evidence.")
    elif days > 28:
        print("VERDICT: long (4-8 weeks). Only worth it for a high-impact change; watch for novelty and seasonality.")
    elif days >= 7:
        print("VERDICT: feasible.")
    else:
        print("VERDICT: easy; still run at least one full week to cover weekday effects.")


def cmd_mde(a):
    n = a.daily * a.exposed * a.days / a.variants
    lo, hi = 1e-4, 10.0
    comps = max(1, a.variants - 1)
    for _ in range(200):
        mid = (lo + hi) / 2
        p2 = a.baseline * (1 + mid)
        if p2 >= 1:
            hi = mid
            continue
        if n_per_variant(a.baseline, p2, a.alpha, a.power, comps) > n:
            lo = mid
        else:
            hi = mid
    print(f"{n:,.0f} users per arm over {a.days} days")
    print(f"smallest detectable relative lift: {hi:.1%} "
          f"({a.baseline:.3%} -> {a.baseline * (1 + hi):.3%})")
    if hi > 0.3:
        print("Lifts this large are rare for small tweaks; test bold changes only, or test upstream.")


def cmd_analyze(a):
    n1, c1 = a.control
    n2, c2 = a.variant
    p1, p2 = c1 / n1, c2 / n2
    pp = (c1 + c2) / (n1 + n2)
    se_pool = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    zs = (p2 - p1) / se_pool if se_pool else 0.0
    pval = 2 * (1 - N.cdf(abs(zs)))
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    zc = z(1 - a.alpha / 2)
    lo, hi = (p2 - p1) - zc * se, (p2 - p1) + zc * se
    print(f"control: {c1:,}/{n1:,} = {p1:.4%}")
    print(f"variant: {c2:,}/{n2:,} = {p2:.4%}")
    print(f"absolute diff: {p2 - p1:+.4%}  ({1 - a.alpha:.0%} CI {lo:+.4%} to {hi:+.4%})")
    if p1 > 0:
        print(f"relative lift: {p2 / p1 - 1:+.2%}  (CI approx {lo / p1:+.1%} to {hi / p1:+.1%})")
    else:
        print("relative lift: undefined (control has 0 conversions); use the absolute diff")
    if min(c1, c2, n1 - c1, n2 - c2) < 10:
        print("WARNING: fewer than 10 conversions (or non-conversions) in an arm; the normal approximation is unreliable. Keep collecting.")
    print(f"z = {zs:.3f}, p = {pval:.4f}")
    sig = pval < a.alpha
    if sig and p2 > p1:
        verdict = "variant wins (significant). Check guardrails and planned sample before shipping."
    elif sig:
        verdict = "variant loses (significant). Keep control; record why."
    else:
        verdict = "inconclusive. Do not call it; the CI shows the plausible range of effects."
    print("verdict:", verdict)
    if a.planned and min(n1, n2) < a.planned:
        print(f"WARNING: below planned sample ({min(n1, n2):,} < {a.planned:,}); treat as preliminary.")
    # SRM on the two arms, assuming 50/50 unless told otherwise
    srm_p = chi_square_p([n1, n2], [a.split, 100 - a.split])
    if srm_p < 0.001:
        print(f"WARNING: sample ratio mismatch (p={srm_p:.2g}). Fix assignment/tracking before trusting results.")


def chi_square_p(counts, weights):
    total = sum(counts)
    wsum = sum(weights)
    exp = [total * w / wsum for w in weights]
    stat = sum((o - e) ** 2 / e for o, e in zip(counts, exp))
    k = len(counts) - 1
    return chi2_sf(stat, k)


def chi2_sf(x, k):
    """Survival function of chi-square with k dof (regularized upper gamma)."""
    if x <= 0:
        return 1.0
    s = k / 2.0
    xx = x / 2.0
    # series for lower incomplete gamma when x small, continued fraction otherwise
    if xx < s + 1:
        term = total = 1.0 / s
        n = 1
        while abs(term) > 1e-14 * abs(total) and n < 1000:
            term *= xx / (s + n)
            total += term
            n += 1
        lower = total * math.exp(-xx + s * math.log(xx) - math.lgamma(s))
        return max(0.0, 1 - lower)
    b = xx + 1 - s
    c = 1 / 1e-300
    d = 1 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - s)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-14:
            break
    return h * math.exp(-xx + s * math.log(xx) - math.lgamma(s))


def cmd_srm(a):
    split = a.split or [1] * len(a.counts)
    if len(split) != len(a.counts):
        sys.exit("--split must have one weight per count")
    p = chi_square_p(a.counts, split)
    tot = sum(a.counts)
    for i, (c, w) in enumerate(zip(a.counts, split)):
        print(f"arm {i}: {c:,} observed vs {tot * w / sum(split):,.0f} expected")
    print(f"chi-square p = {p:.3g}")
    print("SRM detected: stop and debug assignment, redirects, bot filtering, or event loss."
          if p < 0.001 else "no SRM (p >= 0.001).")
    if p < 0.001:
        sys.exit(1)


def cmd_table(a):
    lifts = [0.05, 0.10, 0.20, 0.50]
    print("| Baseline | " + " | ".join(f"{int(l * 100)}% lift" for l in lifts) + " |")
    print("|---|" + "---|" * len(lifts))
    for b in [0.01, 0.02, 0.03, 0.05, 0.10, 0.20]:
        cells = [f"{n_per_variant(b, b * (1 + l), a.alpha, a.power):,}" for l in lifts]
        print(f"| {b:.0%} | " + " | ".join(cells) + " |")
    print(f"\nper variant; alpha {a.alpha} two-sided, power {a.power}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, need_mde=True):
        p.add_argument("--baseline", type=float, required=True, help="control conversion rate, e.g. 0.04")
        if need_mde:
            p.add_argument("--mde", type=float, required=True, help="relative lift (0.15) or absolute with --absolute")
            p.add_argument("--absolute", action="store_true", help="treat --mde as absolute points")
        p.add_argument("--alpha", type=float, default=0.05)
        p.add_argument("--power", type=float, default=0.8)
        p.add_argument("--variants", type=int, default=2, help="arms including control (default 2)")

    p = sub.add_parser("size"); common(p); p.set_defaults(f=cmd_size)
    p = sub.add_parser("duration"); common(p)
    p.add_argument("--daily", type=float, required=True, help="eligible visitors per day")
    p.add_argument("--exposed", type=float, default=1.0, help="share of traffic in the test (0-1)")
    p.set_defaults(f=cmd_duration)
    p = sub.add_parser("mde"); common(p, need_mde=False)
    p.add_argument("--daily", type=float, required=True)
    p.add_argument("--exposed", type=float, default=1.0)
    p.add_argument("--days", type=int, required=True)
    p.set_defaults(f=cmd_mde)
    p = sub.add_parser("analyze")
    p.add_argument("--control", type=int, nargs=2, metavar=("USERS", "CONVERSIONS"), required=True)
    p.add_argument("--variant", type=int, nargs=2, metavar=("USERS", "CONVERSIONS"), required=True)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--planned", type=int, default=0, help="planned sample per variant")
    p.add_argument("--split", type=float, default=50, help="planned %% of traffic to control (default 50)")
    p.set_defaults(f=cmd_analyze)
    p = sub.add_parser("srm")
    p.add_argument("--counts", type=int, nargs="+", required=True)
    p.add_argument("--split", type=float, nargs="+")
    p.set_defaults(f=cmd_srm)
    p = sub.add_parser("table")
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--power", type=float, default=0.8)
    p.set_defaults(f=cmd_table)
    a = ap.parse_args()
    b = getattr(a, "baseline", None)
    if b is not None and not 0 < b < 1:
        sys.exit(f"--baseline must be a rate between 0 and 1 (got {b}); for 4% pass 0.04")
    if a.cmd == "analyze":
        for arm, (n, c) in (("control", a.control), ("variant", a.variant)):
            if n <= 0 or not 0 <= c <= n:
                sys.exit(f"--{arm}: need USERS > 0 and 0 <= CONVERSIONS <= USERS (got {n} {c})")
    try:
        a.f(a)
    except ValueError as e:
        sys.exit(f"error: {e} (check --baseline/--mde: target rate must stay below 1)")


if __name__ == "__main__":
    main()
