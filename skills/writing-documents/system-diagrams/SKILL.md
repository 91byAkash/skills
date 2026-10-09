---
name: system-diagrams
description: "Create accurate, validated diagrams of systems and processes (architecture/C4, sequence, workflow, data flow, state, ER, deployment) as Mermaid, PNG/SVG or HTML. Use when asked to draw, diagram or map a system, request path, pipeline or schema, or to fix broken Mermaid. Not for numeric charts (use excel-spreadsheets) or the surrounding design doc (use cowrite-document)."
license: MIT
metadata:
  category: "writing-documents"
  version: "3.0.0"
---

# Architecture and process diagrams

Scope: architecture (C4 context and container views), workflows, sequence and API call flows, data flow and lineage, state and lifecycle, ER models, deployment topology. Sources: a description, pasted Mermaid, or a codebase traced with file:line evidence. Output: Mermaid plus PNG/SVG, or a checked standalone HTML/SVG page.

A diagram answers one question for one audience at one level of detail. The work is mostly deciding what to show and getting the facts right. Then lay it out so the main path reads at a glance, and prove it renders before it goes into a document.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `question` | yes | - | "what happens when an order is paid?" |
| `audience` | optional | engineers new to the system | execs, on-call, auditors |
| `source` | yes, one of | - | a description, pasted Mermaid, a repo path, IaC files |
| `type` | optional | chosen in step 2 | `architecture`, `sequence`, `state` |
| `destination` | optional | GitHub Markdown | Confluence, Word, slides, review screen |
| `format` | optional | Mermaid (`.mmd` + fence) | `png`, `svg`, `html` |
| `doc` | optional | none | `docs/orders-design.md` to embed into |
| `scope` | optional | the main flow at container level | "only the payment path" |

## Output

- The diagram source (`.mmd` or `diagram_html.py` `.json`) saved as `diagrams/<doc>_<NN>_<type>_<title>.*`.
- A rendered artifact for any destination that doesn't render Mermaid: PNG at 2× scale, SVG, or HTML.
- A one-line caption saying what to notice.
- A hand-off note listing the evidence used, the unknowns, and anything deliberately left out.

Every diagram has passed `lint_mermaid.py` and a real render (`render_mermaid.sh --check`), or `diagram_html.py` with 0 errors, before it is embedded.

## Supporting files

- [REFERENCE.md](REFERENCE.md): which format per destination, Mermaid syntax for every type, styling and contrast palette, layout rules with spacing numbers, `diagram_html.py` spec, repository tracing, troubleshooting table. Read section 2 before writing Mermaid and section 4 when a diagram reads badly.
- [templates/starters/](templates/starters/): working `.mmd` starters (context, containers, sequence, dataflow, state, er, deployment, workflow). Copy the closest one.
- [templates/diagram.json](templates/diagram.json): `diagram_html.py` spec for a styled architecture view.
- [templates/architecture-design.md](templates/architecture-design.md): design-doc skeleton with a slot for each diagram type.
- [examples/repo-to-diagram.md](examples/repo-to-diagram.md) with [examples/orders-service.json](examples/orders-service.json): a traced repository, evidence table, checker output, and Mermaid companion.
- [scripts/](scripts/):
  - `lint_mermaid.py file.mmd|doc.md`: fast static checks with file:line output (unknown type, unbalanced brackets, subgraph/end, `end` ids, inline comments, undefined classes, classDef without `color:`, unquoted special characters, node count, unlabeled edges, undeclared participants).
  - `render_mermaid.sh in.mmd [out.png|svg] [--check] [--theme] [--scale 2]`: mermaid-cli in headless Chrome; condensed parse errors.
  - `extract_mermaid.py doc.md --list|--extract|--validate|--replace -o out.md`: per-document batch work; `--replace` swaps fences for images and refuses to write if any block fails.
  - `diagram_html.py spec.json -o x.html [--svg x.svg] [--png x.png] [--repo-root R]`: grid layout with label-aware gaps, port spread, light/dark theme, legend; checks overlaps, edges through nodes, label gaps and collisions, crossings, fan-out; verifies `sources` against a checkout.

## Steps

1. **Pin the question.** Write it in one sentence plus the audience. If it isn't clear, ask one question. If several questions are bundled, plan one diagram each.
2. **Choose the type.**

   | The question is about | Type | Mermaid |
   |---|---|---|
   | what a system is made of, what it depends on | architecture: context or containers | `flowchart LR` + classes |
   | the order of calls between parties, returns, async, timeouts | sequence | `sequenceDiagram` |
   | steps, decisions, approvals, runbooks | workflow | `flowchart TD` |
   | where data originates, moves, is transformed and consumed | data flow / lineage | `flowchart LR` |
   | the statuses of one thing and what moves it | lifecycle / state | `stateDiagram-v2` |
   | entities, keys, cardinality | ER | `erDiagram` |
   | where things run: regions, clusters, networks, ports | deployment | `flowchart TB` + subgraphs |
   | code structure (classes, interfaces) | class | `classDiagram` |

   For pasted Mermaid, keep its topology and meaning but re-choose the type and rewrite the styling. `graph`/`flowchart` becomes architecture or workflow; `sequenceDiagram` stays sequence; `stateDiagram` stays lifecycle.
   For everyday subjects (a visa process, a house move), use the same types with plain-language labels. Ask for personal facts rather than inventing dates or amounts.
3. **Gather facts.**
   - From a description: list components, relationships with direction and protocol, and conditions. Mark anything you inferred.
   - From code: follow REFERENCE "Tracing a repository". Pin the commit, start at the entry points, and attribute each I/O to the code that does it. Record `path:lines` per node and edge, and write unknowns down instead of guessing. If a component isn't in the code, don't draw it as fact.
   - From IaC/manifests: deployment facts only (what runs where, ports, scaling). Runtime calls still need code evidence.
4. **Set the scope.** One level of abstraction, about 7-15 nodes and 20 at most. If it is bigger, split: context first, then a container view per area, and a sequence per important flow. Put the narrowed scope in the title.
5. **Pick the tool.**
   - If the destination renders Mermaid and the auto-layout reads well, use Mermaid and copy a starter.
   - If the layout tangles, the view is for a review screen, or a consistent house style is needed, use `diagram_html.py` with explicit rows/cols.
   - If a standard exists in the repo (PlantUML, Graphviz, Structurizr), follow it and apply the same checks by rendering.
6. **Draft and lay out.** Main path in reading order. Each branch or store sits directly above or below its owner, and returns go through an empty corridor. Every edge gets a label (action, protocol, condition, async) unless its endpoints fully imply it. Conditions go on the edge they qualify. Groups appear only for real boundaries. Give every `classDef` a `color:`. Details: REFERENCE sections 3-4.
7. **Validate.**
   - Mermaid: `lint_mermaid.py` and fix every ERROR. Then `render_mermaid.sh --check` (for a doc: `extract_mermaid.py doc.md --validate`). If it fails, look up the message in REFERENCE "Troubleshooting", fix it, and re-run. Never embed a diagram that hasn't rendered. If mermaid-cli cannot be installed (no npm or no Chrome; the script exits 2), use the destination's own preview (GitHub/GitLab, mermaid.live) as the render check, and say in the hand-off which check was used.
   - HTML: `diagram_html.py spec.json --repo-root <repo>` until it reports 0 errors. Treat crossings and fan-out warnings as layout work, not noise.
8. **Look at it.** Render to PNG and view it: main path obvious, labels readable at the intended size, nothing on top of a line, legend or caption explains the colours. Fix and re-render. Two focused correction rounds are usually enough. If it still fails, report the remaining defect rather than iterating blindly.
9. **Embed and deliver.** GitHub/GitLab get the fence. Confluence/Word/PDF/slides get `extract_mermaid.py doc.md --replace -o out.md --keep-source`, or the PNG from `render_mermaid.sh --scale 2`. Save sources under `diagrams/`. In the hand-off, state the evidence (commit), the unknowns, and the omissions.

## Checkpoints

- After step 2: one sentence names the question, the type and the audience.
- After step 3: every node and edge has a source (a description line, or `path:lines`); unknowns are listed.
- After step 7: lint 0 errors and render OK (or checker 0 errors).
- After step 8: you have looked at the rendered image yourself; don't only rely on the tools.

## Worked example

Brief: "Draw what happens when an order is created; it goes in Confluence and the README." Full transcript in [examples/repo-to-diagram.md](examples/repo-to-diagram.md).

1. Question: "what does `POST /orders` touch?" Audience: design reviewers. Types: container-level architecture plus a sequence for the paid/failed branch.
2. Trace at commit `871348a`: `rg` finds the route, DB connect, provider call, publish and consume. Six facts were recorded with lines. The storefront isn't in the repo, so it's shown as a generic "API client". The exchange→queue binding is an explicit unknown.
3. `diagram_html.py orders-service.json --repo-root ../sample-repo` first failed with `bad-source: app/main.py:6-18 is outside the file (1-17)`. After fixing the range: `0 error(s), 0 warning(s)`, no crossings. The PNG was inspected.
4. README sequence: `lint_mermaid.py` 0 errors, `extract_mermaid.py --validate` OK, and `--replace` produced `diagrams/readme_01_sequence_create_order.png` for Confluence.
5. Hand-off flagged a likely bug found while tracing (`result.ok` on an httpx response).

## Pitfalls

- **Inventing components.** A config key or package name isn't a running service. Draw what the evidence shows and note the rest.
- **Mixing levels.** Classes next to cloud regions confuses everyone. Split into separate views.
- **Unlabelled or vague edges.** "uses" and "calls" say nothing; "publishes OrderPaid (async)" says what flows and how.
- **Conditions in a footnote.** An unconditional-looking arrow with a note elsewhere misleads. Put "only if paid" on the edge.
- **Colour without meaning, or text without contrast.** Every colour maps to a legend entry; every `classDef` has `color:`.
- **Mermaid parse traps.** Lowercase `end` as an id; unquoted `()` in labels; `%%` after code; missing `end` for a subgraph or `alt` block; a message without `:` in a sequence.
- **Embedding unrendered diagrams.** A fence that fails to parse shows up as a code block in the published doc. Validate first.
- **Platform mismatch.** Confluence, Word and most wikis show the raw code. Ship an image and keep the source.
- **Too big.** Past ~20 nodes, nobody reads it. Split by level or by flow.
- **Stale diagrams.** Keep the source next to the doc, name the commit, and re-render when the code changes.

## Done when

- [ ] The diagram answers the stated question at one level, with a title and a one-line caption.
- [ ] Every node and edge is backed by the description or by `path:lines` at a named commit; unknowns and omissions are stated.
- [ ] Every edge carries a label or is marked implied; conditions sit on their edges.
- [ ] `lint_mermaid.py` and `render_mermaid.sh --check` pass (or `diagram_html.py` reports 0 errors), with no unexplained warnings.
- [ ] You looked at the rendered image: main path clear, labels readable, no overlaps or lines through boxes.
- [ ] Source saved as `diagrams/<doc>_<NN>_<type>_<title>.*`; the destination gets a fence or an image as it requires.

Related skills: cowrite-document (the design doc around the diagram), word-documents and pdf-files (embedding images), powerpoint-decks (diagram slides), long-form-writing (captions and surrounding prose), internal-communications (sharing architecture changes).
