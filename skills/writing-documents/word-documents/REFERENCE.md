# docx reference

Read the section you need. All XML below uses the `w:` prefix for
`http://schemas.openxmlformats.org/wordprocessingml/2006/main` and `r:` for the
officeDocument relationships namespace.

## Contents
1. Package anatomy
2. Units
3. Paragraphs, runs and styles
4. Tracked changes (revisions)
5. Comments
6. Fields: page numbers, TOC, dates
7. Tables
8. Images
9. Sections: page size, orientation, margins, headers/footers
10. Lists and numbering
11. Templates (.dotx) and content controls
12. python-docx: what it does and doesn't
13. JavaScript `docx` package gotchas
14. Conversions
15. Editing XML safely with lxml
16. Troubleshooting

## 1. Package anatomy

| Part | Holds |
|---|---|
| `[Content_Types].xml` | MIME type for every part (`Default` by extension, `Override` by part name) |
| `_rels/.rels` | points at `word/document.xml`, core/app properties |
| `word/document.xml` | body: `<w:body>` → `<w:p>` paragraphs, `<w:tbl>` tables, final `<w:sectPr>` |
| `word/_rels/document.xml.rels` | ids (`rId5`) used by images, hyperlinks, headers, comments |
| `word/styles.xml` | paragraph/character/table styles (`w:styleId` ≠ display name: "Heading 1" is usually `Heading1`) |
| `word/numbering.xml` | list definitions (`w:abstractNum`) and instances (`w:num`) |
| `word/comments.xml` | comment bodies |
| `word/header1.xml`, `footer1.xml` | header/footer stories |
| `word/footnotes.xml`, `endnotes.xml` | notes |
| `word/media/*` | images |
| `docProps/core.xml` | title, author, dates |

## 2. Units

| Unit | Where | Conversion |
|---|---|---|
| DXA (twentieths of a point) | page size, margins, indents, table widths | 1440 = 1 inch, 567 ≈ 1 cm |
| Half-points | font size `w:sz` | `w:val="22"` = 11 pt |
| Eighths of a point | border width `w:sz` | 4 = 0.5 pt |
| EMU | drawings/images | 914400 = 1 inch, 360000 = 1 cm |
| Fiftieths of a percent | `pct` table widths | 5000 = 100% |

Page sizes in DXA: Letter 12240 × 15840, A4 11906 × 16838, Legal 12240 × 20160.

## 3. Paragraphs, runs and styles

```xml
<w:p>
  <w:pPr><w:pStyle w:val="Heading2"/><w:jc w:val="left"/></w:pPr>
  <w:r><w:rPr><w:b/></w:rPr><w:t>Bold start </w:t></w:r>
  <w:r><w:t xml:space="preserve"> then normal text</w:t></w:r>
</w:p>
```
- A run (`w:r`) is a stretch with one formatting (`w:rPr`). Word splits runs for revision ids and spell-check, so visible phrases are often fragmented. Merge identical neighbours first (`merge_runs.py`).
- Leading/trailing spaces need `xml:space="preserve"` on `w:t`.
- `w:pPr` child order is schema-enforced; the common ones in order: `pStyle, keepNext, keepLines, pageBreakBefore, numPr, pBdr, shd, tabs, spacing, ind, jc, outlineLvl, rPr, sectPr, pPrChange`.
- `w:rPr` order: `rStyle, rFonts, b, i, caps, strike, color, sz, szCs, highlight, u, vertAlign, lang, ...`. Validators and Word complain when order is wrong.
- Prefer a style (`pStyle`/`rStyle`) over direct formatting. Headings must use the built-in Heading N styles (or set `w:outlineLvl`) to appear in the TOC and navigation pane.
- Page break: `<w:r><w:br w:type="page"/></w:r>` inside a paragraph. Line break: `<w:br/>`. Tab: `<w:tab/>`.
- Horizontal rule: a paragraph bottom border (`<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="auto"/></w:pBdr>`), not an empty table.
- Right-aligned text on the same line (e.g. "Total ........ 42"): a right tab stop with a dot leader in `w:tabs` (`<w:tab w:val="right" w:leader="dot" w:pos="9360"/>`) and a `<w:tab/>` in the run, never padding with dots or spaces.

## 4. Tracked changes (revisions)

Every revision element needs `w:id` (unique across the document), `w:author`, `w:date` (ISO 8601, `2026-10-08T09:00:00Z`).

| Change | XML |
|---|---|
| Insert text | `<w:ins w:id="7" w:author="A" w:date="…"><w:r><w:t>new</w:t></w:r></w:ins>` |
| Delete text | `<w:del w:id="8" w:author="A" w:date="…"><w:r><w:delText>old</w:delText></w:r></w:del>` |
| Replace | a `w:del` immediately followed by a `w:ins`, copying the old run's `w:rPr` into the new run |
| Delete a whole paragraph | wrap every run in `w:del` **and** mark the paragraph mark: `<w:pPr><w:rPr><w:del w:id="9" w:author="A" w:date="…"/></w:rPr></w:pPr>` (the revision mark is the first child of that `w:rPr`) |
| Insert a new paragraph | new `w:p` with its runs in `w:ins` and `<w:pPr><w:rPr><w:ins …/></w:rPr></w:pPr>` |
| Formatting change | inside `w:rPr`: `<w:rPrChange w:id=… w:author=… w:date=…><w:rPr>…old props…</w:rPr></w:rPrChange>` (last child) |
| Move | `w:moveFrom` / `w:moveTo` with matching `w:moveFromRangeStart`/`End` names; simpler to model as delete + insert |
| Table row inserted/deleted | `<w:trPr><w:ins …/></w:trPr>` or `<w:del …/>` |

A deleted paragraph mark means "join this paragraph with the next one". Accepting it moves the remaining content into the following paragraph; if nothing remains, the paragraph vanishes. `track_changes.py accept` implements this; some converters only strip text and leave an empty (possibly bulleted) paragraph, which is a converter artifact, not a document defect.

Minimal-diff rule for redlines: replace only the words that change. "within 30 days" → delete `30`, insert `45`, not the whole sentence. Reviewers read the redline, so smaller hunks are kinder.

## 5. Comments

Three things must agree:
1. `word/comments.xml` with `<w:comment w:id="0" w:author="…" w:date="…" w:initials="…"><w:p>…</w:p></w:comment>`;
2. a relationship of type `…/relationships/comments` targeting `comments.xml`, plus an `Override` content type `application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml`;
3. in the body: `<w:commentRangeStart w:id="0"/>` … anchored runs … `<w:commentRangeEnd w:id="0"/><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>`.

A comment with no `commentReference` exists but is invisible. Range markers may sit between runs of one paragraph or span paragraphs (start in one `w:p`, end in a later one). Newer Word versions add `commentsExtended.xml` (threading, resolved state) and `commentsIds.xml`; they are optional, and a reply written as a second comment on the same range displays fine.

## 6. Fields

Complex field pattern (works for `PAGE`, `NUMPAGES`, `DATE \@ "d MMMM yyyy"`, `TOC \o "1-3" \h \z \u`, `REF bookmark \h`):
```xml
<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>
<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
<w:r><w:fldChar w:fldCharType="separate"/></w:r>
<w:r><w:t>1</w:t></w:r>           <!-- cached result shown until updated -->
<w:r><w:fldChar w:fldCharType="end"/></w:r>
```
`w:dirty="true"` (or `<w:updateFields w:val="true"/>` in `settings.xml`) asks Word to refresh on open. LibreOffice renders the cached result; `md_to_docx.py` caches the heading list as the TOC result so renders are readable (no page numbers until Word updates).

## 7. Tables

- Give the table a style (`Table Grid` or the template's), a `w:tblW`, a `w:tblGrid` with one `w:gridCol` per column, and a `w:tcW` on every cell, all in DXA. Grid columns must sum to the table width. Percent widths render inconsistently across apps (Google Docs in particular).
- Content width = page width − left − right margin (Letter with 1" margins: 9360 DXA).
- Header row: `<w:trPr><w:tblHeader/></w:trPr>` repeats it on each page; bold its text.
- Shading: `<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>`. `w:val="solid"` paints the cell with the pattern colour (black).
- Merges: horizontal `w:gridSpan`, vertical `w:vMerge w:val="restart"` then `w:vMerge` on cells below. Avoid merges in data tables people will copy into spreadsheets.
- Don't let rows split across pages for short rows: `<w:cantSplit/>` in `w:trPr`.

## 8. Images

- python-docx: `doc.add_picture(path, width=Inches(4))` (keeps aspect ratio when only width is given). Alt text: set `descr` on the `wp:docPr` element (see `md_to_docx.py`).
- Raw XML: an inline `w:drawing` → `wp:inline` with `wp:extent cx/cy` in EMU, `wp:docPr id/name/descr`, and `a:blip r:embed="rIdN"` pointing at a relationship of type `…/relationships/image` targeting `media/imageN.png`. Add a `Default Extension="png" ContentType="image/png"` if missing.
- Replacing an image in place: overwrite `word/media/imageN.ext` with a same-format file and, if the aspect ratio changes, update `wp:extent` and `a:ext`.
- Insert at a reasonable resolution (150-200 dpi at printed size); 4000-px screenshots bloat the file.

## 9. Sections

The body's last `w:sectPr` describes the final section; earlier sections end with a `w:sectPr` inside a paragraph's `w:pPr`.
```xml
<w:sectPr>
  <w:headerReference w:type="default" r:id="rId8"/>
  <w:footerReference w:type="default" r:id="rId9"/>
  <w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>
  <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
  <w:titlePg/>   <!-- different first-page header/footer -->
</w:sectPr>
```
Landscape = swap `w:w`/`w:h` and set `w:orient`. One landscape page inside a portrait document = a section break before and after it. Header types: `default`, `first` (needs `w:titlePg`), `even` (needs `w:evenAndOddHeaders` in settings).

## 10. Lists and numbering

- Bullets and numbers come from `numbering.xml`: a paragraph with `<w:numPr><w:ilvl w:val="0"/><w:numId w:val="3"/></w:numPr>` (or a list style that carries it). Never type `•` or `1.` into the text.
- Restart numbering for a new list: add a new `w:num` that points at the same `w:abstractNumId` with `<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride>`, and use its `numId`. python-docx's "List Number" style continues one global sequence, which is the usual "my second list starts at 4" bug.
- Nested levels: `w:ilvl` 0-8; or styles `List Bullet 2`, `List Bullet 3`.

## 11. Templates and content controls

- `.dotx` → `.docx`: unpack, change the `Override` for `/word/document.xml` from `application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml` to `application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml`, pack with a `.docx` name. Keep `.dotx` when the user wants a template back.
- Placeholders like `{{client_name}}`: merge runs, then `docx_replace.py --pairs values.json --all`. Check for leftovers: `docx_to_markdown.py out.docx | grep -n '{{'`.
- Content controls (`w:sdt`): fill `w:sdtContent`'s runs; keep `w:sdtPr` (tag/alias identify the field). Find them with `//w:sdt[w:sdtPr/w:tag/@w:val="ClientName"]`. Remove `<w:showingPlcHdr/>` once real text is in.
- Using a house template with python-docx: `Document("brand.dotx_or_docx")`, delete the body content but keep the final `w:sectPr` (that's what `md_to_docx.py --template` does), then add content with the template's style names.

## 12. python-docx

Does well: new documents, paragraphs/runs with styles, headings, tables, pictures, sections, headers/footers, core properties, reading text.

Does not do (use XML): tracked changes, comments (older versions), fields (TOC/PAGE), footnotes, content controls, numbering restarts, text boxes, charts, reading the text of `w:ins`/`w:del` correctly (`paragraph.text` ignores revisions inconsistently).

Gotchas:
- `paragraph.text = "x"` and `cell.text = "x"` replace all runs with one plain run; set `run.text` on the run you mean.
- Style names are display names (`"List Bullet"`), and the style must exist in the document's `styles.xml` (the default template has the common ones; a custom template might not).
- East-Asian text needs `rFonts w:eastAsia` set, or it falls back to another font.
- `doc.add_heading(text, 0)` uses the Title style, not Heading 1.

## 13. JavaScript `docx` package gotchas

When building with the npm `docx` package (`new Document({sections:[…]})`, `Packer.toBuffer`):
- Default page is A4; for Letter set `page: { size: { width: 12240, height: 15840 } }` (DXA).
- Landscape: pass portrait width/height plus `orientation: PageOrientation.LANDSCAPE`; the library swaps them.
- Tables: set `columnWidths` on the table and `width: { size, type: WidthType.DXA }` on every cell; widths must sum to the table width. Percent widths break in Google Docs.
- Shading: `ShadingType.CLEAR` with `fill`; `SOLID` renders black.
- Lists: a `numbering` config with `LevelFormat.BULLET`/`DECIMAL` and `numbering: { reference, level }` on paragraphs; no literal bullet characters.
- `ImageRun` needs `type: "png"|"jpg"|…` and `transformation: { width, height }` in pixels.
- `PageBreak` goes inside a `Paragraph`'s children. No `\n` in text: one `Paragraph` per line (or `break: 1` on a `TextRun`).
- TOC: `new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-3" })`, and headings must use `HeadingLevel.*` (custom heading styles need `outlineLevel`).
- Right-aligned text with dot leaders: `PositionalTab` with `PositionalTabAlignment.RIGHT` and `PositionalTabLeader.DOT`.
- It cannot open existing files; for edits use the XML route.

## 14. Conversions

| From → To | Command |
|---|---|
| .docx → .pdf | `python scripts/office_convert.py in.docx --to pdf` |
| .doc/.rtf/.odt → .docx | `python scripts/office_convert.py in.doc --to docx` |
| .docx → page PNGs | `python scripts/render_pages.py in.docx --outdir qa --dpi 100` |
| .docx → Markdown | `python scripts/docx_to_markdown.py in.docx` (or `pandoc -t gfm --track-changes=all` when pandoc is installed) |
| Markdown → .docx | `python scripts/md_to_docx.py in.md -o out.docx` (or `pandoc in.md -o out.docx --reference-doc=brand.docx`) |
| .docx → plain text | `markitdown in.docx` when installed; loses revisions |

LibreOffice conversion uses a throwaway profile per run (concurrent runs and a stale lock otherwise hang `soffice`). Rendering differences vs Word: font substitution (install or embed the fonts named in styles), cached field results, slightly different line breaking.

## 15. Editing XML safely with lxml

```python
from lxml import etree
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
tree = etree.parse("work/word/document.xml")
for p in tree.iterfind(".//w:p", NS):
    text = "".join(p.itertext())        # quick filter, includes deleted text
    ...
tree.write("work/word/document.xml", xml_declaration=True, encoding="UTF-8", standalone=True)
```
- lxml keeps namespace prefixes and unknown extension elements (`w14:`, `mc:Ignorable`); `xml.etree.ElementTree` rewrites prefixes (`ns0:`) and can make the file unreadable.
- Never pretty-print or strip whitespace. Never regex-edit across tags.
- Keep `mc:Ignorable` namespaces declared on the root even if you don't use them.
- Use a fresh `w:id` above the current maximum for revisions, bookmarks and comments.
- Parse untrusted XML with entity resolution off (`resolve_entities=False, no_network=True`), as `wordxml.py` does.

## 16. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Word: "unreadable content" | element order in `pPr`/`rPr`, `w:t` inside `w:del`, missing content type, rel to missing part | `validate_docx.py`, then fix the named part |
| Find string "not found" though visible | split across runs, smart quotes (`'` vs `’`), non-breaking space, field result | merge runs; search with `--regex` allowing `[’']` and `\s` |
| Deleted text reappears after accept | it was in `w:t` not `w:delText`, or outside the `w:del` | wrap runs properly |
| Empty bullet after accepting | paragraph mark not deleted | add the paragraph-mark `w:del` |
| Second numbered list continues at 4 | shared `numId` | new `w:num` with `startOverride` |
| TOC says "No table of contents entries" | headings use custom styles without outline level | use Heading N styles or set `w:outlineLvl` |
| Black table cells | `w:shd w:val="solid"` | `w:val="clear"` with `w:fill` |
| Fonts look wrong in render | font not installed in the render environment | install it or accept substitution, verify in Word if critical |
