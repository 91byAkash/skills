Ad group structure:
- AG1 [{theme}]: {keyword} (phrase), [{keyword}] (exact) → RSA1, RSA2
- AG2 [{theme}]: …

Negative keywords:
  Campaign-level:
    - {kw} (≥ 4)
  Ad-group level:
    - AG1: {kw}, {kw}
    (total ≥ 8)

Sitelinks (≥ 4):
  - {title ≤ 25} | {line 1 ≤ 35} | {line 2 ≤ 35} | {URL}

Callouts (≥ 4, each ≤ 25 chars):
  - {callout}

Structured snippets (if relevant):
  - {header}: {value}, {value}, {value}

RSA1 — {ad group}
  Final URL: https://…
  Path1: {≤ 15}   Path2: {≤ 15}
  Headlines (15, each ≤ 30):
    1. {headline} (NN)
    …
    15. {headline} (NN)
  Descriptions (4, each ≤ 90):
    1. {description} (NN)
    …
  Pinning: none (or explicit)

Self-check: 15 headlines and 4 descriptions per RSA, limits respected with counts printed, ≥ 8 negatives, structure labeled, no regulated-claim words, `ads_tool.py limits` passes.
