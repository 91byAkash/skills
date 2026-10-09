<!-- Save to plan_path. Whoever executes this works one task at a time and ticks boxes as steps finish. -->
# Plan: <feature>

| | |
|---|---|
| Implements | <spec path or link; read it alongside this plan> |
| Outcome | <one sentence: what exists when every task is done> |
| Approach | <two or three sentences on the shape of the solution> |
| Stack | <languages, frameworks, libraries that matter here> |

## Rules for every task
<!-- Copied with exact values from the spec, one per line: minimum versions, dependency limits, naming and copy rules, platform targets. -->
- <rule>

## Gaps the spec leaves open
<!-- At most five inputs or failure modes a real user will hit that the spec does not mention and no test would catch, likeliest first.
     Each one is pinned by a test inside the task that owns the code. Write "Checked: none found" if there are none. -->
1. <input or condition> should <expected behaviour>; pinned in task <N>

## Files touched
| Path | New or changed | What it is responsible for |
|---|---|---|
| | | |

---

### <N>. <task name>

Touches: new `<path>` · changed `<path>` (<function or lines>) · test `<path>`
Relies on: `<exact signature produced by an earlier task>`
Provides: `<exact name(params) -> return type>` for later tasks

- [ ] Red: add `<test name>` using the spec's exact values
  ```<lang>
  <test code>
  ```
- [ ] Confirm red: `<command>` fails with `<expected message>`
- [ ] Green: implement `<signature>` in `<file>` (<one line on the approach, only if the test leaves a real choice>)
- [ ] Confirm green: `<command>` passes
- [ ] Commit: `git add <files> && git commit -m "<type(scope): summary>"`
