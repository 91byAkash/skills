# Security Review: <target>

- Source ref: <commit sha>
- Date: <YYYY-MM-DD>
- Profile / scope: <quick|standard|deep> / <paths or "whole target">
- Execution: local code, local fixtures, dummy data only
- Status: <complete | incomplete: reason>

## Summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Informational | 0 |
| Needs validation | 0 |

One paragraph: the most important risk and the first fix to ship.

## Confirmed findings

### F-001 [High] <short title>

- **Where:** `path/to/file.ts:42` (`GET /invoices/:id`)
- **Class:** <CWE id; OWASP Top 10:2025 category if the reader expects one>
- **Principal → boundary:** <who> crosses <which control>
- **Result:** <what they gain, as demonstrated>
- **Proof:** `<test file or command>`; <one-line description of what it shows>
- **Invariant:** <the rule the code must enforce>
- **Fix:** <narrowest change at the last trusted decision point>
- **Regression test:** <name / path>

## Needs validation

### N-001 <title>
- **Where:** …
- **Why it might be real:** …
- **Missing fact:** <exact information needed, e.g. "does the edge proxy strip X-Forwarded-Host?">

## Hardening suggestions (not findings)

- …

## Coverage

See `coverage.md`. Not examined: <list>. No prior run / prior run <ref> reconciled.
