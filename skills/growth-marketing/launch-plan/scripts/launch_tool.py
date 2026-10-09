#!/usr/bin/env python3
"""launch_tool.py - calculators for launches.

Subcommands
  timeline  backward-planned launch calendar for a tier and launch date
  partners  score co-marketing partner candidates from a CSV
  tracker   validate a directory submission tracker CSV
  links     list links to your domain in a saved HTML page and their rel values

Standard library only. Run `launch_tool.py <cmd> -h` for options.
"""
import argparse
import csv
import datetime as dt
import re
import sys
import urllib.request
from html.parser import HTMLParser

# --------------------------------------------------------------------------
# timeline
# --------------------------------------------------------------------------
TASKS = {
    "major": [
        (-56, "Decide goal, tier and success metric; name one owner"),
        (-49, "Positioning and messaging locked (one-liner, 3 messages, proof)"),
        (-42, "Readiness gate: simple / lovable / complete review with product"),
        (-42, "Beta or early-access cohort live; start collecting quotes and metrics"),
        (-35, "Channel plan with owners: owned / rented / borrowed"),
        (-28, "Asset production starts: page, video, screenshots, emails, posts"),
        (-28, "Launch-platform account active daily (comment, follow makers)"),
        (-21, "Partner and creator commitments confirmed in writing"),
        (-21, "Supporter list built (customers, friends, communities) with personal note drafted"),
        (-14, "Upcoming/teaser page live; waitlist push"),
        (-14, "Press list and pitch drafted; embargo date set"),
        (-10, "Site QA on staging (forms, tracking, redirects, noindex off at switch)"),
        (-7, "All assets final; listing copy, first comment, FAQ, objection replies"),
        (-7, "Embargoed pitches out; directory batch 1 prepared"),
        (-3, "Heads-up email to list and supporters (ask for feedback, not votes)"),
        (-2, "Support macros, status page, on-call rota, rollback owner"),
        (-1, "Code and copy freeze; production smoke test in a clean browser"),
        (0, "LAUNCH: post, email, in-app, social, communities; reply to every comment fast"),
        (0, "Hourly dashboard check: traffic by source, signups, errors"),
        (1, "Thank-you notes; reply backlog cleared; fix top reported issues"),
        (2, "Launch recap post with honest numbers"),
        (3, "Directory batch 2; review requests to activated users"),
        (7, "Week-1 metrics vs goal; onboarding drop-off review"),
        (14, "Retrospective; update comparison and pricing pages; customer stories"),
        (30, "30-day results review; decide follow-on campaign"),
    ],
    "medium": [
        (-21, "Goal, owner and success metric; confirm tier"),
        (-14, "Positioning one-liner and 'you can now' statement"),
        (-14, "Asset list: changelog entry, email, post, short demo"),
        (-7, "Assets drafted; partner or integration co-announcement agreed"),
        (-5, "Site and tracking QA for new or changed pages"),
        (-2, "Support briefed; docs and help articles live"),
        (0, "LAUNCH: changelog, email to relevant segment, in-app, social"),
        (2, "Reply backlog; collect first reactions"),
        (7, "Adoption check: % of active accounts using it"),
        (14, "Retro; follow-up email to non-adopters"),
    ],
    "minor": [
        (-3, "Write 'you can now' line and confirm it is live for everyone"),
        (-1, "Help doc updated"),
        (0, "Changelog entry and in-app note"),
        (7, "Include in weekly or monthly product digest"),
    ],
}


def cmd_timeline(a):
    try:
        day0 = dt.date.fromisoformat(a.date)
    except ValueError:
        sys.exit("--date must be YYYY-MM-DD")
    rows = TASKS[a.tier]
    print(f"Launch {a.tier} on {day0.isoformat()} ({day0.strftime('%A')})")
    if a.tier == "major" and day0.weekday() not in (1, 2, 3):
        print("WARN: launch-platform days outside Tue-Thu usually get far less traffic")
    elif a.tier == "medium" and day0.weekday() >= 5:
        print("WARN: weekend launch; email and social reach fewer people and support is thin. Prefer Tue-Thu")
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    lead = (day0 - today).days
    need = -min(o for o, _ in rows)
    if lead < need:
        print(f"WARN: only {lead} days of lead time; this tier plans for {need}. "
              "Compress or drop tasks dated before today.")
    print(f"{'date':<11} {'T':>5}  task")
    for off, task in rows:
        d = day0 + dt.timedelta(days=off)
        flag = "  (past)" if d < today else ""
        print(f"{d.isoformat():<11} {off:>+5}  {task}{flag}")


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
# tracker
# --------------------------------------------------------------------------
TRACK_COLS = ["directory", "tier", "url", "category", "fit", "status", "submitted",
              "live_url", "link_rel", "variant", "notes"]
STATUSES = {"todo", "drafted", "approved", "submitted", "live", "rejected", "skipped"}


def cmd_tracker(a):
    with open(a.csv, newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        missing = [c for c in TRACK_COLS if c not in (rd.fieldnames or [])]
        if missing:
            sys.exit("missing columns: " + ", ".join(missing))
        rows = list(rd)
    counts, problems, variants = {}, [], {}
    for n, r in enumerate(rows, 2):
        st = r["status"].strip().lower()
        counts[st] = counts.get(st, 0) + 1
        if st not in STATUSES:
            problems.append(f"line {n} {r['directory']}: unknown status '{st}'")
        if not re.match(r"^(1[0-3]|[1-9])-[a-z]", r["tier"].strip()):
            problems.append(f"line {n} {r['directory']}: tier '{r['tier'].strip()}' should look like '2-software' (number-name, see directories.md)")
        if st == "live" and not r["live_url"].strip():
            problems.append(f"line {n} {r['directory']}: live but no live_url")
        if st == "live" and not r["link_rel"].strip():
            problems.append(f"line {n} {r['directory']}: live but link not verified (fill link_rel)")
        if st in ("submitted", "live") and not r["submitted"].strip():
            problems.append(f"line {n} {r['directory']}: no submitted date")
        if r["fit"].strip().lower() in ("no", "weak") and st not in ("skipped", "rejected"):
            problems.append(f"line {n} {r['directory']}: weak fit but not skipped")
        v = r["variant"].strip()
        if v:
            variants.setdefault(v, set()).add(r["tier"].strip())
    print("status counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    live = [r for r in rows if r["status"].strip().lower() == "live"]
    follow = [r for r in live if r["link_rel"].strip().lower() in ("follow", "dofollow", "none")]
    print(f"live {len(live)}; followed links {len(follow)}")
    for v, tiers in variants.items():
        if len(tiers) > 1:
            problems.append(f"variant '{v}' reused across tiers {sorted(tiers)}: vary the copy per audience")
    for p in problems:
        print("ISSUE: " + p)
    if not problems:
        print("tracker ok")
    sys.exit(1 if problems else 0)


# --------------------------------------------------------------------------
# links
# --------------------------------------------------------------------------
class _A(HTMLParser):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain.lower()
        self.hits = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        d = dict(attrs)
        href = (d.get("href") or "").lower()
        if self.domain in href:
            self.hits.append((d.get("href"), d.get("rel") or "(none: followed)"))


def cmd_links(a):
    if a.file:
        html = open(a.file, encoding="utf-8", errors="replace").read()
    else:
        req = urllib.request.Request(a.url, headers={"User-Agent": "Mozilla/5.0 link-check"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    p = _A(a.domain)
    p.feed(html)
    if not p.hits:
        print(f"no links to {a.domain} found in the HTML (listing may render client-side; check in a browser)")
        return
    for href, rel in p.hits:
        print(f"{rel:<28} {href}")


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("timeline")
    t.add_argument("--date", required=True, help="launch day YYYY-MM-DD")
    t.add_argument("--tier", choices=list(TASKS), default="major")
    t.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    t.set_defaults(fn=cmd_timeline)

    p = sub.add_parser("partners")
    p.add_argument("--csv", required=True,
                   help="columns: partner," + ",".join(PARTNER_W) + "[,idea] scored 1-5")
    p.set_defaults(fn=cmd_partners)

    k = sub.add_parser("tracker")
    k.add_argument("--csv", required=True, help="columns: " + ",".join(TRACK_COLS))
    k.set_defaults(fn=cmd_tracker)

    lk = sub.add_parser("links")
    g = lk.add_mutually_exclusive_group(required=True)
    g.add_argument("--file", help="saved HTML of the listing page")
    g.add_argument("--url", help="listing URL to fetch")
    lk.add_argument("--domain", required=True, help="your domain, e.g. example.com")
    lk.set_defaults(fn=cmd_links)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

