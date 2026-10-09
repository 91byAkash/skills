# Filling PDF forms

Two kinds of forms need different methods. Find out which you have first:

```bash
python scripts/pdf_forms.py fields form.pdf
```
- Lists fields → **fillable (AcroForm)**: fill by field name (section A).
- "no fillable fields" → **flat form** (boxes and lines drawn on the page): place text at coordinates (section B).
- A form built with XFA (some government forms) shows few or no AcroForm fields but displays fields in Acrobat. pypdf cannot fill XFA. Options: ask for a non-XFA version, or treat it as a flat form on the rendered page.

## A. Fillable forms

1. **List fields and make a template.**
   `python scripts/pdf_forms.py fields form.pdf --template values.json`
   Each line: page, type, fully qualified name, current value, allowed states/options, rectangle.
2. **Map the user's data to field names.** Names are often cryptic (`topmostSubform[0].Page1[0].f1_01[0]`). Match by page position: render `pdf_forms.py grid form.pdf --page 1 -o grid.png` and compare the `rect` of each field with the label beside it. Write down the mapping before filling.
3. **Write values.json.**

| Field type | JSON value | Notes |
|---|---|---|
| text | `"Akash Jha"` | respect `max_len`; dates in the format the label asks for |
| checkbox | `true` / `false` | mapped to that box's own on-state (`/Yes`, `/On`, `/1`, ...) |
| radio | one of `states` (`"pro"` or `"/pro"`) | the group shares one name; each button has its own export value |
| choice (dropdown/list) | one of `options` | exact text match |
| signature | not fillable | leave for a real signature tool; never paste an image as a "signature" unless asked |
| button | skip | push buttons hold no value |

4. **Fill:** `python scripts/pdf_forms.py fill form.pdf values.json -o filled.pdf`. The script refuses unknown names (with suggestions), invalid options and over-long text; fix the JSON and rerun.
5. **Read back:** `pdf_forms.py fields filled.pdf` must show every value; then render and look.
6. **Flatten if requested** (recipient must not edit, or viewers show blank fields): `fill … --flatten`. Flattening paints each widget's current appearance into the page and removes the form; keep the unflattened copy too.

Hierarchical names: a field named `applicant.name` is a child `name` under parent `applicant`; use the full dotted name the `fields` command prints.

## B. Flat (non-fillable) forms

1. **Find label positions** in PDF points (origin bottom-left):
   `python scripts/pdf_forms.py words form.pdf --page 1 --grep "Name|Date|Signature"`
2. **If labels aren't text** (scanned form): render a grid, `pdf_forms.py grid form.pdf --page 1 -o grid.png --step 25`, read approximate x/y off the grid lines (red = x, blue = y).
3. **Write entries.json.** Prefer label anchors so placement survives small layout shifts:
```json
[
  {"page": 1, "label": "Name:", "text": "Akash Jha"},
  {"page": 1, "label": "Date of birth", "below": true, "dy": 16, "text": "1990-04-12"},
  {"page": 1, "label": "Signature", "occurrence": 2, "dx": 10, "text": "Akash Jha"},
  {"page": 2, "x": 72, "y": 512, "text": "X", "size": 12}
]
```
   - Default placement is right of the label (`dx` 6 pt), on the label's baseline. `below: true` puts it under the label (`dy` default 14 pt).
   - Checkboxes on flat forms: an `"X"` at the box's coordinates.
   - Long answers: split across lines yourself (one entry per line, `y` decreasing by ~1.2 × font size).
4. **Overlay:** `python scripts/pdf_forms.py overlay form.pdf entries.json -o filled.pdf --size 10`.
5. **Render and adjust:** text should sit inside the box, not on the line or the label. Nudge `dx`/`dy` and rerun; two rounds is normal.

## Field-name discovery tricks

- Tooltips (`/TU`) often hold the human label: `python -c "from pypdf import PdfReader; [print(k, v.get('/TU')) for k, v in PdfReader('form.pdf').get_fields().items()]"`.
- Fill every text field with its own name to see where each one lands, render, and use that as a map (then fill for real from the original file).

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Values present in `fields` but blank on screen | viewer ignores NeedAppearances | `--flatten`, or open in a different viewer to confirm |
| Checkbox shows unchecked after `true` | widget lacks appearance for its on-state | check `states` from `fields`; flatten; or overlay an "X" |
| Text too long, cut off | field box size fixed | shorten, use the field's multi-line option, or smaller font via overlay |
| `fields` lists nothing but Acrobat shows fields | XFA form | see top of this page |
| Characters missing (accents, ₹) | field font lacks glyphs | overlay with a TTF registered in ReportLab, or flatten after fill in a full viewer |
