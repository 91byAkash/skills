# Example: from a rant to a short post, through all three modes

**Request.** "I want to write a post about why our deploys got slow. I keep ranting about it in standups."

## Fragments mode

The file path wasn't given, so ask once and get `drafts/gate-debt-notes.md`. Capture the request itself as the first fragment, then interview:
- "How slow, compared to when?" gives the number: 14 minutes now, 6 a year ago.
- "What does each team say when you ask?" gives the overheard line about ownership.
- "What would you call this, if it had a name?" Several names get tried ("check creep", "pipeline sediment", "gate debt"), and the user picks *gate debt*. That's the leading word.

```
$ python3 scripts/fragments.py init drafts/gate-debt-notes.md "Why deploys got slow"
$ python3 scripts/fragments.py add drafts/gate-debt-notes.md --text "Every team added one check. Nobody removed one."
added fragment 1 (8 words)
... (the user edits fragment 1 by hand between turns; the next add appends after their edit)
$ python3 scripts/fragments.py check drafts/gate-debt-notes.md
5 fragments, 101 words; 0 problem(s)
```
The finished pile looks like templates/fragments-file.md.

## Shape mode

1. Read the whole pile. It is read-only from here on; the article goes in `drafts/gate-debt.md`.
2. Prerequisites, agreed with the user: readers are engineers who know what a *deploy pipeline* and a *CI check* are.
   `python3 scripts/ledger.py init art.json --prereq "deploy pipeline,CI check" --article drafts/gate-debt.md`
3. Three candidate openings, A/B/C, each with its thesis. They're in templates/shape-session.md §3. The user picks A, the number, because it's the most concrete.
4. Block by block:

```
$ python3 scripts/ledger.py land art.json "Opening: 14 minutes vs six" --requires "deploy pipeline" --grounds "slow deploys"
landed block 1
$ python3 scripts/ledger.py land art.json "Every team added one check" --requires "CI check" --grounds gate
landed block 2
$ python3 scripts/ledger.py check art.json --requires "gate debt"
BLOCKED: not grounded yet: gate debt  -> add a grounding block first, or promote to prerequisite
```
The user wanted the cleanup rule next, but it leans on *gate debt*, which nothing has grounded yet. So block 3 coins the term first ("We call the result gate debt: checks that outlived the reason they were added").

The pile has no example of a gate that caught a real bug. Name the gap: "Give me one, or we drop the 'some gates earn their keep' paragraph." The user supplies one.

## Edit pass

A first draft of the opening, written before the session tightened it:

```
# Gate debt

In this post, we'll delve into why our deploys got slow. It's not just about speed — it's about trust.

Every team added one check, and the checks were never removed. Many people say gates are free. We made a decision to measure. See [here](https://example.com/gates).
```

```
$ python3 scripts/prose_lint.py draft1.md
draft1.md:3:1: style throat-clear: warm-up opener: start with the point
draft1.md:3:1: style not-x-but-y: 'not X, but Y' framing: state Y directly
draft1.md:3:21: style ai-phrase: stock phrase 'delve'  [look at / dig into]
draft1.md:3:67: style filler: 'just' adds nothing  [(cut)]
draft1.md:5:1: note passive: passive 'were never removed': who does it?
draft1.md:5:64: style weasel: unsourced appeal 'many people say': cite it or own the claim
draft1.md:5:99: style nominal: 'made a decision' hides the verb  [decide]
draft1.md:5:131: fix click-here: link text should say where it goes  [[descriptive text](url)]
46 words; fix=1 style=6 note=1
```

After the fixes (same length, every finding resolved, the author's short sentences kept):

```
# Gate debt

Our deploys take 14 minutes. A year ago they took six.

Every team added one check, and no team removed one. Gates feel free, so we measured them: the [timing data](https://example.com/gates) shows two gates that caught nothing in a year and cost four minutes per deploy.
```
```
$ python3 scripts/prose_lint.py draft2.md
46 words; fix=0 style=0 note=0
```
The edit report (templates/edit-report.md) lists the click-here link as must-fix and the rest as style. Under "Kept on purpose" it records one item: the passive was removed by naming the actor ("no team removed one") rather than by restructuring the sentence.
