# Beats menu (show this before writing each beat)

```
Grounded so far: deploy pipeline, CI check, gate   (ledger.py show)
Article so far:  1 beat, 2 sentences (re-read from disk just now)

Next beat: pick one
A) The number. "Fourteen minutes. A year ago, six."
   requires: deploy pipeline  ·  grounds: slow deploys
   unlocks: the timing table, the "nobody chose this" beat
B) Coin it. "We started calling it gate debt."
   requires: gate  ·  grounds: gate debt
   unlocks: the cleanup rule, the title
C) The overheard line. "We can't remove it, we don't know who owns it."
   requires: gate  ·  grounds: orphaned check
   unlocks: the ownership-tag fix
(blocked for now: "the 3 a.m. alarm" needs *orphaned check*; pick C first, or make it a prerequisite)
```

Rules:
- Every option must be reachable from the grounded set. Use `ledger.py offer ledger.json cand.json` to check.
- Say what each option grounds and what it unlocks, so the user sees a little way down each path.
- Once the user picks, write only that beat, then stop.
