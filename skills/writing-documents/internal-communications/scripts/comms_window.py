#!/usr/bin/env python3
"""Work out the date windows for a periodic update and print ready-made search filters.

Usage: comms_window.py [--end 2026-10-08] [--days 7] [--json]

Prints:
  look-back window (Progress / Problems / newsletter / FAQ sources) and look-ahead window (Plans)
  the header date label, e.g. "(Oct 2-8)"
  search filters for mail (after:/before: with slashes, before is exclusive) and chat (after:/before: are exclusive on both ends)
--end defaults to today (local time). The look-back window ends on --end inclusive.
"""
import argparse, datetime as dt, json


def label(a, b):
    if a.year != b.year:
        return f"({a:%b %-d, %Y} - {b:%b %-d, %Y})"
    if a.month == b.month:
        return f"({a:%b} {a.day}-{b.day})"
    return f"({a:%b} {a.day} - {b:%b} {b.day})"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--end", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    back_start = a.end - dt.timedelta(days=a.days - 1)
    ahead_end = a.end + dt.timedelta(days=a.days)
    one = dt.timedelta(days=1)
    out = {
        "look_back": [back_start.isoformat(), a.end.isoformat()],
        "look_ahead": [(a.end + one).isoformat(), ahead_end.isoformat()],
        "header_label": label(back_start, a.end),
        "mail_filter": f"after:{back_start:%Y/%m/%d} before:{a.end + one:%Y/%m/%d}",
        "chat_filter": f"after:{back_start - one:%Y-%m-%d} before:{a.end + one:%Y-%m-%d}",
        "calendar_ahead": f"{(a.end + one).isoformat()}..{ahead_end.isoformat()}",
    }
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Progress/Problems window: {out['look_back'][0]} .. {out['look_back'][1]}")
        print(f"Plans window:             {out['look_ahead'][0]} .. {out['look_ahead'][1]}")
        print(f"Header label:             {out['header_label']}")
        print(f"Mail search filter:       {out['mail_filter']}")
        print(f"Chat search filter:       {out['chat_filter']}")
        print(f"Calendar (ahead):         {out['calendar_ahead']}")


if __name__ == "__main__":
    main()
