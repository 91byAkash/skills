# Review request

You are reviewing completed work. Read-only: do not modify the working tree, index, or branches; inspect with `git diff`, `git show`, `git log`.

## What was built
<1-3 sentences>

## Requirements
<path to spec/plan/ticket, or pasted acceptance criteria>

## Range
- Base: <BASE_SHA>
- Head: <HEAD_SHA>
```
git diff --stat <BASE_SHA>..<HEAD_SHA>
git diff <BASE_SHA>..<HEAD_SHA>
```

## Review focus (check each deliberately)
- <input or failure mode the tests do not cover>

## Rulings the implementer made
- <copied from the ledger, if any>

## How to judge
- The spec says what must happen; where it is silent, judge by what a reasonable user would expect.
- Grade each finding by its effect on a user if shipped.
- Check: plan alignment, code quality, architecture, tests (real behaviour, edge cases), production readiness (migrations, backward compatibility, docs).

## Report format
Strengths: <brief>
Issues:
- Critical: <file:line> <problem> <fix>
- Important: ...
- Minor: ...
Declined to judge: <behaviour set aside and why, one per line; "none" if empty>
Assessment: Ready to merge | Ready after fixes | Not ready
