# Walkthrough: redline a contract with comments

Request: "In msa.docx change the payment term to 45 days and Acme Ltd → Acme Inc
as tracked changes under my name, and flag the late-fee sentence." Commands run
from the skill folder; outputs are real.

## 1. Look before touching

```bash
python scripts/docx_to_markdown.py msa.docx
```
```
# Master Services Agreement

This agreement is between Acme Ltd ("Supplier") and Northwind LLC ("Customer").

Invoices are payable within 30 days. Late fees apply at the statutory rate.

- Acme Ltd warrants the services for 90 days.
- Acme Ltd may subcontract with consent.

Notices to Acme Ltd go to legal@acme.example.
```
Four "Acme Ltd" occurrences, one payment term. In the XML the term is stored as
two runs (`…within 3` + `0 days. `), so a naive string replace would miss it.

## 2. Unpack and merge runs

```bash
python scripts/ooxml.py unpack msa.docx work/
python scripts/merge_runs.py work/          # merged 2 runs
```

## 3. Tracked replacements

```bash
cat > edits.json <<'J'
[{"find": "30 days", "replace": "45 days"},
 {"find": "Acme Ltd", "replace": "Acme Inc"}]
J
python scripts/docx_replace.py work/ --pairs edits.json --all --track --author "Akash Jha"
```
```
   1  '30 days' -> '45 days'
   4  'Acme Ltd' -> 'Acme Inc'
```
Each count matches what step 1 showed. A `0` (exit code 2) would mean the
search string doesn't match the XML text (quotes, spacing): fix it before going on.

## 4. Comment

```bash
python scripts/docx_comment.py work/ --anchor "Late fees" \
  --text "Which rate applies? Suggest 1.5%/month." --author "Akash Jha"
```

## 5. Pack, validate, view

```bash
python scripts/ooxml.py pack work/ msa-redline.docx
python scripts/validate_docx.py msa-redline.docx --original msa.docx --author "Akash Jha"   # OK
python scripts/docx_to_markdown.py msa-redline.docx
```
```
This agreement is between {-Acme Ltd-}{+Acme Inc+} ("Supplier") and Northwind LLC ("Customer").

Invoices are payable within {-30 days-}{+45 days+}. Late fees[^c0] apply at the statutory rate.
...
[^c0]: Akash Jha: Which rate applies? Suggest 1.5%/month.
```
Then `python scripts/render_pages.py msa-redline.docx --outdir qa` and open
`qa/page-1.png`: deletions are struck through, insertions underlined.

## 6. Optional clean copy

```bash
python scripts/track_changes.py accept msa-redline.docx -o msa-clean.docx
```

## What the validator would have caught

If one replacement had been made without `--track`:
```
FAIL: untracked edits found (text differs after rejecting all revisions):
  -Final clause stays.
  +Last clause stays.
```
