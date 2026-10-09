# Review Task <N>: <name>

Model: <tier, required>

Read, in order:
1. Requirements: <workspace>/task-<N>-brief.md
2. Implementer report: <workspace>/task-<N>-report.md (test evidence is here; do not rerun unless it is missing)
3. Diff package: <workspace>/review-<N>.txt (commits, stat, full diff)

Binding constraints (verbatim from plan/spec):
- <exact value / format / relationship>

Check:
- Spec compliance: every requirement met; nothing extra built; exact values match.
- Quality: correctness and edge cases, tests that would fail if the code broke, naming, structure, dead code, error handling at boundaries.
- Requirements you cannot verify from the diff: list them as "cannot verify from diff" rather than guessing.

Return:
```
spec: ✅ | ❌ (<missing/extra items>)
quality: approved | changes
path:line: <Critical|Important|Minor>: <problem>. <fix>.
cannot verify from diff: <items or none>
totals: C=<n> I=<n> M=<n>
```
