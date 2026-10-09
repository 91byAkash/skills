---
name: word-documents
description: "Create, read and edit Word documents (.docx, .dotx, .doc) with real styles, keeping existing formatting. Use when a task names a .docx file, asks for a \"Word doc\", memo, letter or contract, or asks for find-and-replace, tracked-change redlines or review comments. Not for PDFs (use pdf-files), spreadsheets (use excel-spreadsheets) or decks (use powerpoint-decks)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# Word documents (.docx)

Scope: styles, tables, images, headers/footers, page numbers and TOC; surgical edits; tracked changes; comments; accept/reject revisions; conversion to PDF or from .doc. Not for Google Docs edited through their own API.

A `.docx` is a ZIP of XML parts: `word/document.xml` (body), `styles.xml`, `numbering.xml`, `comments.xml`, headers/footers, `media/`, relationships (`_rels/*.rels`) and `[Content_Types].xml`. Pick the lightest tool that keeps what you don't touch.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `task` | yes | - | `create`, `read`, `edit`, `redline`, `comment`, `convert` |
| `source` | for read/edit | - | `contract.docx`, `legacy.doc`, `brand.dotx` |
| `content` | for create | - | Markdown outline, notes, data |
| `output` | optional | `<source-stem>-edited.docx` or `<slug>.docx` | `report.docx` |
| `author` | for redline/comment | the user's name | `Akash Jha` |
| `page` | optional | template's setup, else Letter | `a4`, `letter`, `--landscape` |
| `style_source` | optional | built-in styles | a `.docx`/`.dotx` whose styles to inherit |
| `extras` | optional | none | `--toc`, `--header "Confidential"`, `--page-numbers` |

## Output

One `.docx` file (plus a rendered PDF/PNGs for QA, not delivered unless asked) that opens in Word without a repair prompt, uses named styles for headings/lists/tables, and passes `scripts/validate_docx.py`. For redlines, every change is a revision by `author`; for reads, Markdown text.

## Supporting files

- [REFERENCE.md](REFERENCE.md): OOXML anatomy and units, XML recipes (runs, revisions, comments, fields, tables, images, sections, content controls), python-docx and docx (JavaScript npm package) gotchas, conversions. Read before any XML edit or when a script does not cover the case.
- [scripts/](scripts/): all Python 3, need `lxml` and `python-docx`; LibreOffice for conversion/rendering.
  - `md_to_docx.py`: Markdown → styled .docx (TOC, header, page X of Y, tables, images with alt text, `--template`).
  - `docx_to_markdown.py`: read a .docx with headings, lists, tables, `{+ins+}`/`{-del-}` and comments.
  - `ooxml.py`: safe `unpack` / `pack` / `list` (refuses symlinks and path traversal).
  - `merge_runs.py`: coalesce fragmented runs so phrases are findable.
  - `docx_replace.py`: find/replace across runs, keeping formatting; `--track --author` for redlines; `--delete-paragraph`.
  - `docx_comment.py`: anchored comments (single or `--batch` JSON).
  - `track_changes.py`: `list`, `accept`, `reject` (optionally per `--author`).
  - `validate_docx.py`: structure, rels, content types, revision/comment integrity; `--original` catches untracked edits.
  - `office_convert.py`, `render_pages.py`: headless LibreOffice conversion and page PNGs.
- [templates/report.md](templates/report.md), [templates/memo.md](templates/memo.md), [templates/letter.md](templates/letter.md): Markdown skeletons for `md_to_docx.py`.
- [examples/redline-walkthrough.md](examples/redline-walkthrough.md): full contract redline session with commands and outputs.

## Steps

1. **Classify the task.**
   - Create from content → step 2.
   - Read/summarize → `python scripts/docx_to_markdown.py in.docx` (add `--changes accept` for the clean text). Stop.
   - Edit, redline or comment an existing file → step 3.
   - Legacy `.doc` → `python scripts/office_convert.py file.doc --to docx`, then treat the result as the source.
   - `.dotx` template → see REFERENCE "Templates": copy, switch the main content type, then edit.
2. **Create.**
   - If the user has a house template, pass it with `--template brand.docx` so its styles, page setup and headers carry over.
   - Write the content as Markdown from a template in `templates/`, then:
     `python scripts/md_to_docx.py doc.md -o doc.docx --page a4 --toc --page-numbers --header "…" --title-from-h1`
   - If you need layout Markdown can't express (multi-column sections, text boxes, letterhead art, complex numbering), build with python-docx or the JavaScript `docx` npm package using REFERENCE recipes; still use named styles.
   - Go to step 5.
3. **Prepare an edit.** Work on a copy; never overwrite the source.
   ```bash
   python scripts/ooxml.py unpack in.docx work/
   python scripts/merge_runs.py work/
   ```
   Read `work/word/document.xml` around the target text. If a phrase still isn't contiguous after merging, it spans formatting changes; the scripts below handle that.
4. **Make the change with the narrowest tool.**
   - Text change, no redline → `docx_replace.py work/ --find … --replace …` (`--all` for every hit, `--pairs edits.json` for many).
   - Redline requested ("track changes", "show my edits", legal/contract review) → same with `--track --author "<name>"`. Whole paragraph removal → `--delete-paragraph "unique text" --track`.
   - Review notes → `docx_comment.py work/ --anchor "phrase" --text "note" --author "<name>"`.
   - Clean copy of a redlined file → `track_changes.py accept in.docx -o clean.docx`.
   - Anything else (styles, table cells, images, section setup) → hand-edit the XML with an lxml script per REFERENCE; keep element order and never pretty-print.
   Then pack: `python scripts/ooxml.py pack work/ out.docx --force`.
5. **Validate.** `python scripts/validate_docx.py out.docx` (edits: add `--original in.docx`; redlines: also `--author "<name>"`). Fix every FAIL and rerun.
6. **Render and look.** `python scripts/render_pages.py out.docx --outdir qa --dpi 80` and open each PNG. Check headings, list numbering, table widths, images, header/footer, page breaks, and (for redlines) that strikethrough/insertions appear where intended.
7. **Deliver** the path, what changed (counts from the script output), and anything you could not do.

## Checkpoints

- After step 1: you know whether the deliverable must preserve an existing file. If yes, no step may regenerate the document from scratch.
- After step 4: every script printed a non-zero count per pattern; exit code 2 means a find string was not found, so fix the string rather than moving on.
- After step 5: `OK` with zero FAIL lines. With `--original`, no "untracked edits" message.
- After step 6: you looked at every page image, not just the first.

## Worked example

Request: "In `msa.docx`, change the payment term from 30 to 45 days and the party name Acme Ltd → Acme Inc as tracked changes under my name, and flag the late-fee sentence."

```bash
python scripts/ooxml.py unpack msa.docx work/
python scripts/merge_runs.py work/                         # merged 2 runs
cat > edits.json <<'J'
[{"find": "30 days", "replace": "45 days"},
 {"find": "Acme Ltd", "replace": "Acme Inc"}]
J
python scripts/docx_replace.py work/ --pairs edits.json --all --track --author "Akash Jha"
#    1  '30 days' -> '45 days'
#    4  'Acme Ltd' -> 'Acme Inc'
python scripts/docx_comment.py work/ --anchor "Late fees" --text "Which rate applies? Suggest 1.5%/month." --author "Akash Jha"
python scripts/ooxml.py pack work/ msa-redline.docx
python scripts/validate_docx.py msa-redline.docx --original msa.docx --author "Akash Jha"   # OK
python scripts/render_pages.py msa-redline.docx --outdir qa
```
Report: "msa-redline.docx: 5 tracked replacements (1 payment term, 4 party names) and 1 comment, all by Akash Jha; validation clean; rendered page checked." Full session: [examples/redline-walkthrough.md](examples/redline-walkthrough.md).

## Pitfalls

- **Regenerating to edit.** Rebuilding an existing document from extracted text drops styles, numbering, comments, fields and section setup. Edit the XML in place.
- **Run fragmentation.** "30 days" may be stored as `3` + `0 days`. Run `merge_runs.py` first; the replace script also splits runs at exact offsets.
- **Untracked edits inside a redline.** One plain replace among tracked ones is invisible in the "final" view. `validate_docx.py --original` catches it.
- **`<w:t>` inside `<w:del>`.** Deleted text must be `<w:delText>`; otherwise Word shows it as live text or reports corruption.
- **Deleting a paragraph only by its runs** leaves an empty paragraph (an empty bullet if numbered). Also mark the paragraph mark deleted (`--delete-paragraph` does both).
- **Manual formatting instead of styles.** Bold 16pt Normal text is not a heading; it won't appear in the TOC or navigation pane.
- **Literal bullets and `\n`.** Use list styles/numbering, and one paragraph per line.
- **TOC and page fields are computed by Word on open** (fields are marked dirty). `md_to_docx.py` pre-fills the TOC with the heading list, so LibreOffice renders and PDFs show contents without page numbers; Word adds the numbers. Say so instead of "fixing" it.
- **python-docx `paragraph.text = …`** collapses the paragraph's runs into one, losing mixed formatting. Assign to specific runs.
- **Pretty-printing XML** adds whitespace inside text nodes and can break `xml:space="preserve"` content.
- **Untrusted files:** use `ooxml.py unpack`, which skips symlink entries and paths that escape the folder.

## Done when

- [ ] Output `.docx` exists at the agreed path; the source file is unchanged.
- [ ] `validate_docx.py` prints `OK` (with `--original`/`--author` for edits and redlines).
- [ ] Every page was rendered and inspected; no overflow, missing images, broken numbering or stray empty bullets.
- [ ] Headings, lists and tables use named styles; images have alt text.
- [ ] For redlines: every change is a revision by the named author, and comments are anchored to the right text.
- [ ] The reply lists what changed (with counts), the output path, and any limits (e.g. TOC fills on open).

Related skills: `pdf-files` (export or fill forms), `excel-spreadsheets` (tables that need formulas), `powerpoint-decks`, `cowrite-document` (writing the content), `system-diagrams` (figures to embed).
