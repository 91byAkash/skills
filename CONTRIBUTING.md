# Contributing

Thanks for improving the pack. Keep changes small and focused, one skill per pull request where possible.

## Adding or changing a skill

1. Put the skill at `skills/<category>/<skill-name>/SKILL.md`. The folder name must equal the frontmatter `name` and be unique across the pack (lowercase letters, digits, single hyphens, at most 64 characters).
2. Start from this skeleton:

   ```markdown
   ---
   name: my-skill
   description: "What it is for, in one clause. Use when <distinct situations, user phrases, file types>. Not for <nearest neighbour> (use <other-skill>)."
   license: MIT
   metadata:
     category: "<category folder>"
     version: "3.0.0"
   ---

   # My Skill

   One or two sentences on the purpose and the key idea.

   ## Inputs

   | Parameter | Required | Default | Example |
   |---|---|---|---|
   | `param` | required | — | realistic value |

   ## Output

   - What exists when the skill is done.

   ## Supporting files

   - [REFERENCE.md](REFERENCE.md): what it holds. Read when <condition>.

   ## Steps

   1. **Verb phrase.** Action and command. Done when <checkable condition>.

   ## Worked example

   ## Pitfalls

   ## Done when

   - [ ] Observable completion item.
   ```

   `agent-operations/write-agent-skill` has the full guidance, a template, and `scripts/validate-skill.py`.
3. Rules:
   - Quote the description (it usually contains `: `, which is invalid YAML unquoted). Aim for 200-420 characters (the spec allows 1024, but agents cut long skill listings): the main job first, then `Use when` with 3-6 real trigger phrases, then `Not for` with the nearest neighbour skill. Put "Covers ..." lists in the body, not the description.
   - Names: verb-object or a plain noun phrase a user would say (`diagnose-bug`, `excel-spreadsheets`), unique and specific enough not to clash with other packs (avoid bare `pdf`, `tdd`, `review`).
   - Keep `SKILL.md` under about 400 lines; move long reference material into sibling files linked from `SKILL.md` with a note on when to read them.
   - Links stay inside the skill folder (skills are installed one at a time). Refer to other skills by name in prose.
   - Scripts: executable, `--help` or a usage header, non-zero exit on failure, standard library where practical. Add any new third-party Python package to `requirements.txt`.
   - Test every script you add on a real input.
   - No secrets, personal data, or binaries over 100 KB.
4. Update `INDEX.md` and the catalog in `README.md` if you add, rename, or remove a skill, and add a line to `CHANGELOG.md`.
5. Adding a category: list its folder in the `skills` array of the plugin's `plugin.json` and add an `akash-skills-<category>` entry to `marketplace.json`. For a release, raise `version` in `plugin.json` and in every `marketplace.json` entry that sets one; installed plugins only update when it changes.

## Check before you open a pull request

```bash
pip install pyyaml          # strict frontmatter parsing
bash scripts/check-pack.sh --expect 64
```

It checks frontmatter, required sections, links, script syntax, file hygiene, and the plugin manifests. CI runs the same command.
