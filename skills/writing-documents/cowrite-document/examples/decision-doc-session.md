# Example session: a decision doc from a context dump to reader-tested

The conversation is a condensed illustration. Every command output is from an actual run of the scripts. Reader replies are summarised, and their scores were entered by hand into `results.json`. The finished document is [invoicing-decision.md](invoicing-decision.md).

## Stage 1: Context

**Opening questions (answered in shorthand):**

```
1 type? -> decision doc
2 readers? -> finance lead + head of platform decide; payments squad reads
3 impact? -> approve 2 eng for Q4
4 template? -> none
5 constraints? -> roadmap locks 20 Oct, keep it short
```

**Dump (excerpt):** "nightly recon between legacy billing db and ledger failed 6x last qtr, 4 were the timeout... ERP migration is Q2... three old customers have custom rounding... LRS owns the ledger".

**Clarifying questions** (numbered, 7 asked). The answers that changed the doc:

- "3: patch-only fixes the timeout, so 4 of 6": this became Option 3, a real alternative to "do nothing".
- "5: finance OK to honour rounding by credit note, 12 months": this removed the biggest objection, so it went into the Recommendation.
- "7: LRS hasn't said yes to reviewing": this became a risk.

Exit test met: the next questions were about edge cases (December close, rollback), not basics.

## Stage 2: Structure and sections

```text
$ python scripts/scaffold_doc.py decision-doc "Move invoicing to the new ledger" --owner "Priya Rao" -o inv.md
wrote inv.md: 6 sections (Recommendation, The decision to make, Options, Comparison, Risks of the recommendation, What we need from you)
$ python scripts/doc_status.py inv.md | head -3
inv.md: 18 words, ~0.1 min read, 0/6 sections done
```

The order followed REFERENCE section 3: Options and Comparison first, Recommendation last.

**Options section.** 9 items were brainstormed, and the curation reply was "keep 1,2,5; 5 is the patch option; drop 3 (nobody would pick a vendor now), drop 7,8 (audience knows); merge 4 into 1". The draft replaced only that section's placeholder. One user edit was "say 'two engineers, six weeks', not '12 eng-weeks', in the options". That preference was then applied in the other sections too, with plain units in the prose and the table keeping the total.

**Comparison** stalled after three rounds of small edits, so the cut question was asked. "Rework when ERP lands" stayed, because it is the argument against Patch, and a "team morale" row went.

**Whole-document review at 5/6 sections** found one inconsistency. The decide-by date was "end of October" in the table and "20 October" in the text; it was fixed to 20 October everywhere.

```text
$ python scripts/doc_status.py inv.md
inv.md: 324 words, ~1.4 min read, 6/6 sections done
...
note  undefined    acronym LRS is never expanded
```

## Stage 3: Reader test

```text
$ cat q.txt     # 7 questions, "question || intended answer"
What is being decided? || Whether invoicing moves to the new ledger in Q4 or waits for the ERP migration
...
Who is LRS and what do we need from them? || Ledger owners; review capacity, not yet committed
$ python scripts/reader_test.py prepare inv.md --questions q.txt -o rt
wrote 7 question prompts and 6 checks to rt/ (fill results.json with replies and scores)
```

Each `rt/q*.txt` went to a reader with no other context. Two replies fell short:

- **q05** (how to back out): "turn the flag off… presumably data must be migrated back?" Scored *partial*, because the doc didn't say rollback needs no data migration.
- **q06** (who is LRS): "an internal team, unclear what is needed or by when". Scored *fail*.
- **check-assumptions** listed "shadow-run" as undefined.

```text
$ python scripts/reader_test.py report rt/results.json
5 pass, 1 partial, 1 fail, 0 unscored
- check-assumptions: fix Risks of the recommendation (define 'shadow-run')
NOT READY: revise the sections listed, then re-test with a fresh reader
```

**Fixes (surgical, both in Risks):**

- Spelled out the shadow run, and said that turning a flag off sends the next run through legacy billing with no data migration.
- Expanded LRS and stated the ask: one reviewer for about 4 h/week in weeks 43-48, confirmed by 20 October.

```text
$ python scripts/doc_status.py inv-v2.md --final && echo ok
ok
$ python scripts/reader_test.py report rt2/results.json      # new fresh reader, all 7 questions
7 pass, 0 partial, 0 fail, 0 unscored
READY: the document answers its readers' questions
```

## Final hand-off

- The user was asked to do their own read-through and to verify the 6 failures, the 12-month credit-note agreement, and the week numbers.
- Tip given: the full option analysis could go in an appendix if the deciders want it, without lengthening the main doc.
