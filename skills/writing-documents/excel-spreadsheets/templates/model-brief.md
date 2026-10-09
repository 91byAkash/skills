# Model brief

Fill this in (with the user, or from their request) before building. Anything
left blank is an assumption you must state in the reply.

| Item | Answer |
|---|---|
| Question the model answers | <e.g. "Can we fund 3 hires in 2027 from operating cash?"> |
| Primary output(s) | <cells/charts the reader looks at first> |
| Periods | <monthly / quarterly / yearly>, <start> to <end> |
| Currency and unit | <$k, ₹ lakh, units> |
| Scenarios | <Base / Downside / Upside, or none> |
| Tabs (exact names if specified) | <Assumptions, Model, Summary> |
| Required headers or formulas the user spelled out | <copy literally> |
| Inputs (label → value → source) | <Starting revenue → 1,200 → FY2025 actuals> |
| Inputs the user must still provide | <list; mark yellow in the file> |
| Existing file conventions to follow | <font, colours, input cells, number formats> |
| Checks to reconcile against | <source totals, last year's actuals> |
| Deliverable | <filename.xlsx, values cached for preview? yes/no> |

## Layout sketch

```
Assumptions   A: label | B: value (blue) | C: source note
Model         A: line item | B..: one column per period, one formula pattern per row
Summary       KPIs pulling from Model (green), chart
```
