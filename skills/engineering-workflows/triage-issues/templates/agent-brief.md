<!--
The brief may sit in the queue for weeks while the code moves, so write it to survive that:
state behaviour and contracts (type names, signatures, config keys, commands) rather than
steps, and leave out file paths, line numbers and guesses about current structure. Every
"done" item must be checkable on its own. For a PR, brief only the work still missing from
the existing diff.
-->
{disclosure_line}

### Brief for the implementing agent ({bug | enhancement})

**Goal in one line:** <what must be true when this is finished>

**Done means**
- [ ] <observable check, phrased so a test can prove it>
- [ ] <observable check>
- [ ] A regression test reproduces the case from this issue

| Today | After this work |
|---|---|
| <what the system does now (for an enhancement: the baseline it extends)> | <what it should do, including edge cases and failure handling> |

**Contracts touched**
- `<TypeOrSchema>`: <the change and the reason>
- `<function(args)>`: <current result → expected result>
- `<config.key>` / `<command --flag>`: <new option, default value>

**Leave alone:** <nearby behaviour or code that must not change, so the agent does not over-reach>

**Needs a person because** (only for `ready-for-human`): <judgement call | access the agent lacks | design choice | hands-on testing>
