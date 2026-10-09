# Example: turning the Q3 review deck into the Q4 version

A real session run with the scripts in this skill. The source deck was built from `templates/outline.json` with `build_deck.py` (10 slides).

**Brief:** "Make the Q4 version of the retention review. Drop the customer-quote slides, keep the Q3 churn chart and add a Q4 one right after it, update the title slide and the stats headline. Keep the speaker notes in sync."

## 1. Look before touching

```text
$ python scripts/pptx_slides.py list q3-review.pptx
  1  ppt/slides/slide1.xml      slideLayout7.xml   notes=y  Churn fell 18% after the onboarding changes
  2  ppt/slides/slide2.xml      slideLayout7.xml   notes=n  Three numbers that moved this quarter
  3  ppt/slides/slide3.xml      slideLayout7.xml   notes=y  Churn dropped the month the new checklist shipped
  ...
  7  ppt/slides/slide7.xml      slideLayout7.xml   notes=n  Customers noticed
  8  ppt/slides/slide8.xml      slideLayout7.xml   notes=n  "We had our first dashboard before the kickoff call ended."
  9  ppt/slides/slide9.xml      slideLayout7.xml   notes=n  Risks we are watching
 10  ppt/slides/slide10.xml     slideLayout7.xml   notes=n  Decisions needed today
```

Decision: slides 7 and 8 are the customer-voice slides, so delete them. Slide 3 is the chart to duplicate.

## 2. Structure first

```text
$ python scripts/pptx_slides.py delete q3-review.pptx 7 8 -o step1.pptx
deleted slides [7, 8]
clean: removed 5 unreferenced part(s): ppt/media/image1.jpg, ppt/slides/_rels/slide7.xml.rels,
       ppt/slides/_rels/slide8.xml.rels, ppt/slides/slide7.xml, ppt/slides/slide8.xml
$ python scripts/pptx_slides.py duplicate step1.pptx 3 --after 3 -o step2.pptx
duplicated slide 3 -> new slide 4 (ppt/slides/slide7.xml)
```

The photo was used only by the deleted slide, so `clean` removed it too. The duplicate got its own notes slide and its own `chart2.xml`, so new data on slide 4 won't touch slide 3.

## 3. Fill text, scoped by slide

`pairs.json` (slides 1-2):

```json
{"Q3 retention review · October 2026": "Q4 retention review · January 2027",
 "Three numbers that moved this quarter": "Three numbers that held in Q4"}
```

`s4.json` (slide 4, including notes):

```json
{"Churn dropped the month the new checklist shipped": "Churn stayed down through the holiday quarter",
 "The step change lines up with the July 3 release.": "December was the lowest month since the launch.",
 "Point at July.": "Point at December."}
```

```text
$ python scripts/pptx_replace.py step2.pptx -o step3.pptx --pairs pairs.json --slides 1-2
   1 x 'Q3 retention review · October 2026'
   1 x 'Three numbers that moved this quarter'
$ python scripts/pptx_replace.py step3.pptx -o step4.pptx --pairs s4.json --slides 4 --notes
   1 x 'Churn dropped the month the new checklist shipped'
   1 x 'The step change lines up with the July 3 release.'
   1 x 'Point at July.'
```

The first attempt ran the chart-title pair with `--slides 1-3`. It renamed slide 3 (the Q3 chart) instead of the new slide 4, and the grid made that obvious. Scoping each map to the slides it belongs to fixed it.

## 4. New chart data

```python
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor

p = Presentation("step4.pptx")
chart = next(sh.chart for sh in p.slides[3].shapes if sh.has_chart)
cd = CategoryChartData(number_format="0.0%")
cd.categories = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
cd.add_series("Monthly churn", [0.046, 0.043, 0.042, 0.041, 0.043, 0.040])
chart.replace_data(cd)
chart.value_axis.minimum_scale = 0                     # replace_data re-enables auto scaling
for i, pt in enumerate(chart.plots[0].series[0].points):
    pt.format.fill.solid()
    pt.format.fill.fore_color.rgb = RGBColor.from_string("E04E58" if i == 5 else "D6E2FB")
p.save("q4-review.pptx")
```

Without the `minimum_scale` line, the render showed the axis starting at 3.7%. That made a flat quarter look like a sawtooth.

## 5. Validate and QA

```text
$ python scripts/pptx_validate.py q4-review.pptx --original q3-review.pptx
0 error(s), 0 warning(s), 0 inherited
$ python scripts/pptx_qa.py q4-review.pptx
9 slides, 0 error(s), 0 warning(s)
$ python scripts/pptx_outline.py q4-review.pptx --text-only --slides 4
## Slide 4 — layout 'Blank'
Churn stayed down through the holiday quarter
categories: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
series 'Monthly churn': [0.046, 0.043, 0.042, 0.041, 0.043, 0.04]
December was the lowest month since the launch.
  notes: Point at December. Mention that seasonality last year went the other way.
$ python scripts/thumbnail_grid.py q4-review.pptx --cols 3
q4-review-grid.png  slides 1-9
```

Visual pass on the grid: title and stats updated, slides 3 and 4 side by side with independent data and highlights, no overflow, and the photo slide gone with nothing orphaned.

## 6. What still needed a human call

- The stats on slide 2 (18%, 2.4×, $310k) are still Q3 figures. The brief didn't give Q4 numbers, so the hand-off says so instead of guessing.
- The title slide headline ("Churn fell 18%…") is a Q3 claim. Flag it for the presenter to restate with Q4 data.
