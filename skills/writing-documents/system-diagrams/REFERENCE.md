# Diagram reference

Read the section you need: syntax when writing Mermaid, layout when a diagram reads badly, troubleshooting when it won't render.

## Contents

1. Which format where (platform matrix)
2. Mermaid syntax by diagram type
3. Styling and contrast
4. Layout rules (any tool)
5. `diagram_html.py` spec reference
6. Tracing a repository
7. Troubleshooting

## 1. Which format where

| Destination | Ship | Notes |
|---|---|---|
| GitHub / GitLab Markdown, wikis built on them | a ```` ```mermaid ```` fence | flowchart, sequence, class, state, ER, gantt, pie and mindmap render. Newer types (`architecture-beta`, `block-beta`, C4) depend on the host's Mermaid version, so check the preview and fall back to `flowchart`. |
| Confluence, Notion, Jira, Google Docs, Word, slides, PDF, email | PNG (or SVG where accepted) **plus** the `.mmd` source in the repo | `extract_mermaid.py doc.md --replace -o out.md`. PNG at 2× scale for crisp screens. |
| Docs site (MkDocs, Docusaurus, Sphinx) | fence if the Mermaid plugin is enabled, else SVG | check the site's build config |
| Standalone review / design-review screen | `diagram_html.py` HTML (theme toggle, tooltips with sources) | single file, no network needed |
| Printed / archived | SVG or PDF | vector stays sharp |

Always keep the editable source (`.mmd` or `.json`) next to the doc that uses it. A diagram that can only be edited as a PNG goes stale.

File naming: `diagrams/<doc-stem>_<NN>_<type>_<title>.{mmd,png,svg}`, e.g. `diagrams/orders_design_02_sequence_checkout.png`. The number keeps the order of appearance, and stable names let a re-render overwrite files instead of adding copies.

## 2. Mermaid syntax by diagram type

### Flowchart (architecture, workflow, data flow, deployment)

```
flowchart LR
  %% direction: LR, RL, TD/TB, BT
  a[Rectangle] --> b(Rounded) --> c([Stadium / actor])
  d[(Database)] --- e[[Subroutine / queue]] -.-> f{Decision}
  g{{Hexagon}} ==> h>Flag] --o i((Circle))
  %% or: a -- label --> b
  a -->|label| b
  %% dotted = async / optional
  a -.->|async| e
  %% thick = main path
  a ==>|critical| b
  subgraph vpc["Private network"]
    direction TB
    x --> y
  end
  click a "https://example.com/runbook" "Runbook"
```

- Quote any label containing `( ) [ ] { } # ; :` or starting with a keyword: `a["Retry (3x)"]`.
- Line breaks inside labels: `<br/>`.
- Node ids are plain words without spaces. Never use lowercase `end` as an id (it closes subgraphs); `End`, `done` work.
- `%%` starts a comment and must be on its own line; a trailing `%%` after code is a parse error. `%% title: ...` is read by `extract_mermaid.py` for file names.
- Subgraphs can be edge endpoints (`vpc --> z`), and each can set its own `direction`.

### Sequence

```
sequenceDiagram
  autonumber
  actor U as User
  participant A as API
  participant D as DB
  participant Q as Queue
  participant P as Payments
  participant W as Worker
  participant M as Mailer
  participant S as SMS
  %% ->> sync request, -->> response
  U->>A: POST /orders
  %% or A->>+D / D-->>-A shorthand
  activate A
  %% -) async (open arrow)
  A-)Q: publish OrderPaid
  %% -x lost / failed
  A-xP: call dropped
  alt approved
    A-->>U: 201
  else declined
    A-->>U: 402
  end
  opt cache miss
    A->>D: select
  end
  loop every 30s
    W->>A: poll
  end
  par notify email
    A->>M: send
  and notify sms
    A->>S: send
  end
  Note over A,D: same transaction
  deactivate A
```

Declare participants in the order you want columns. Keep message text short (verb + object + key parameter). Show only the parameters that matter.

### State

```
stateDiagram-v2
  [*] --> Pending
  Pending --> Paid: charge approved
  Pending --> Failed: declined
  Failed --> Pending: retry
  state Shipping {
    [*] --> Packed
    Packed --> InTransit
  }
  Paid --> Shipping
  Shipping --> [*]
  note right of Failed: kept 30 days
```

Every non-terminal state needs a way out; every failure that is recoverable needs a transition back.

### Entity relationship

```
erDiagram
  %% exactly one -- zero or more
  CUSTOMER ||--o{ ORDER : places
  %% one -- one or more
  ORDER ||--|{ ORDER_LINE : contains
  %% zero or one each side
  ORDER |o--o| PAYMENT : "paid by"
  ORDER {
    uuid id PK
    uuid customer_id FK
    string status "pending|paid"
  }
```

Cardinality: `|o` zero or one, `||` exactly one, `}o` zero or more, `}|` one or more. `--` identifying, `..` non-identifying.

### Class

```
classDiagram
  class Order {
    +UUID id
    +Status status
    +pay(token) Result
  }
  Order "1" --> "*" OrderLine : contains
  PaymentGateway <|.. StripeGateway : implements
  Order ..> PaymentGateway : uses
```

### C4 and other types

- C4 (`C4Context`, `C4Container`) works but lays out poorly and isn't rendered everywhere. A flowchart with consistent classes (person, system, external) plus a legend usually reads better and renders everywhere. `templates/starters/context.mmd` and `containers.mmd` follow that pattern.
- C4 in Mermaid is still marked experimental: syntax is PlantUML-style (`Person(id, "Label", "desc")`, `System_Ext(...)`, `Rel(from, to, "label", "tech")`, boundaries with `{ }`), and layout is driven only by statement order and `UpdateLayoutConfig($c4ShapeInRow="3")`.
- `architecture-beta` (icons, groups, port-side edges) looks like this; the `-beta` keyword is the spelling most hosts know:

```
architecture-beta
  group api(cloud)[API]
  service db(database)[Database] in api
  service server(server)[Server] in api
  db:L -- R:server
```

- Since Mermaid 11, `block`, `packet`, `sankey` and `xychart` also work without `-beta` (the `-beta` spelling is still accepted). Hosts pin older Mermaid versions, so use the `-beta` spelling, check the destination's preview, and fall back to `flowchart` if it shows raw code. `lint_mermaid.py` accepts both spellings.
- Gantt, timeline, journey, mindmap, quadrant: fine for plans and overviews, not architecture.

## 3. Styling and contrast

- Every `classDef` that sets `fill` also sets `color:` (text) and `stroke`. Light fill means dark text; dark fill means white text. `lint_mermaid.py` warns on a missing `color:`.
- Use colour for a meaning (type, ownership, trust zone) and say what it means in a legend or caption. Use 3-5 classes at most.
- Palette used by the starters (fill / stroke / text):

| Meaning | fill | stroke | color |
|---|---|---|---|
| person / client | `#FFF4E5` | `#B4590A` | `#5A2D05` |
| internal service | `#E8EEFB` | `#2B4C9B` | `#14275A` |
| store / queue | `#E6F4EC` | `#24784A` | `#0E3B22` |
| external system | `#F3F4F6` | `#6B7280` | `#1F2933` |
| gate / decision | `#FFF7D6` | `#9A6B00` | `#3D2A00` |
| failure path | `#FDECEC` | `#B42318` | `#5C0F0A` |
| the system in focus | `#1F2A5C` | `#1F2A5C` | `#FFFFFF` |

- Icons and emoji in labels (🔐 💾 📨) can help a non-technical audience. Use them sparingly and consistently; they don't replace a type label, and some renderers draw them as boxes.
- Render with `--theme neutral` (the default in `render_mermaid.sh`) on a white background for docs. Use `--bg transparent` only when you know the page colour.

## 4. Layout rules (any tool)

**Abstraction.** One diagram, one level: context, then containers, then components, then code. Name a narrower scope in the title ("…: checkout path only"). About 7-15 nodes is comfortable and 20 is the ceiling. Past that, split by level or by flow.

**Main path first.** Identify the reader's main journey (the request path, the happy path) and lay it out in reading order: left→right for systems, top→bottom for workflows. Neighbours on the main path sit next to each other.

**Branches and stores.** Put each store, cache or side call directly above or below the node that owns, reads or writes it, so its edge is one straight segment. Keep a row's branches on the same side.

**Returns.** Put an edge going back to an earlier node in an empty corridor, on the side with no branches, so it doesn't cross them. In sequence diagrams, use the dashed response arrow.

**Second entrance.** When a node already has an incoming edge, bring a new source in from another side (usually above or below).

**Fan-out.** A side carrying k edges needs at least `32 + 14 × (k − 1)` px (4 edges ≈ 74 px). Spread a hub's edges over two or three sides, or make the hub larger. Centre a parent over its children, and line a child up with its only parent.

**Label space.** Labels carry meaning (protocol, action, async, condition), so leave room for them rather than dropping them. The clear gap between two boxes for a horizontal label is about `6.5 px × characters + 21 px`, with CJK characters counting as two. Clear gap means box edge to box edge, not centre to centre. Label every edge unless both endpoints fully imply it.

**Boundaries.** Draw a group only for a real boundary: network or trust zone, deployment unit, ownership, persistence. Keep outside actors outside the frame. A frame doesn't replace the edges.

**Conditions belong on the edge.** "only if paid", "on 5xx, ×3", "nightly". A note elsewhere doesn't make an unconditional-looking arrow conditional.

**Crossings.** Fix them by moving the endpoint that is off the main path, not by adding detours. Don't trade meaning or readable text size for zero crossings.

**Text size.** On screen, node labels ≥ 12 px and edge labels ≥ 10 px at the intended display width. In slides, export at 2× and check readability at the slide's size.

## 5. `diagram_html.py` spec reference

| Field | Required | Meaning |
|---|---|---|
| `title` | yes | top line; state scope and, for code, the commit |
| `caption` | optional | one sentence: what to notice |
| `nodes[].id/label/row/col` | yes | grid placement; rows top→bottom, cols left→right; gaps auto-size |
| `nodes[].type` | optional (`service`) | actor, client, service, gateway, store, cache, queue, job, external |
| `nodes[].sub` | optional | second line: technology, path |
| `nodes[].w` | optional | fixed width in px |
| `nodes[].sources` | optional | `["path:line", "path:a-b"]`, checked with `--repo-root` |
| `edges[].from/to` | yes | node ids |
| `edges[].label` | recommended | what flows or happens |
| `edges[].style` | optional (`sync`) | sync (solid), async (dashed), data (thick), return (dotted grey) |
| `edges[].route` | optional (`auto`) | auto (straight if aligned, else h-v-h through the column gap), `hv`, `vh` |
| `edges[].from_side/to_side` | optional | left, right, top, bottom; pin only when needed |
| `edges[].implied` | optional | true to allow no label |
| `groups[].label/members/kind` | optional | boundary frame around members; `kind: trust` draws it red |
| `notes[]` | optional | sourced facts, unknowns, caveats under the diagram |
| `lang` | optional (`en`) | `<html lang>` |

Exit 1 on any ERROR. Fix in the order the checker suggests: unknown ids → overlaps → edges through nodes → label gaps and collisions → crossings and fan-out → unlabelled edges.

## 6. Tracing a repository

1. **Pin the snapshot.** `git rev-parse --short HEAD`, `git status --short`. Put the commit in the title or caption. If the tree is dirty, say so, or trace a clean checkout.
2. **Find the slice.** Start from entry points (route registrations, `main`, CLI commands, queue consumers, cron/scheduler config, deployment manifests), then follow imports and call sites until each requested responsibility reaches its real input, output or side effect.
3. **Attribute I/O to the code that does it.** The function that opens the connection or writes the file owns that edge. A comment or a "manages X" docstring is not evidence.
4. **Record evidence while reading**: `path:start-end` for each node and each meaningful edge. Follow branches, retries, fallbacks and error handling, because they become edge conditions.
5. **Separate kinds of claim.** Configured vs. called, local stub vs. real service, optional feature vs. normal path. Label the one the code supports.
6. **Name unknowns** in the notes ("binding from exchange to queue not in this repo"). Never turn a config value or package name into a service you haven't seen used.
7. Stop when every requested responsibility and relationship has evidence. Extra reads should answer an open question that could change the diagram.

Useful searches: `rg -n "@(app|api|router)\.(get|post|put|delete)|add_url_rule|createServer|listen\("`, `rg -n "connect\(|create_engine|psycopg|redis|boto3|S3Client|publish|basic_publish|send_message|KafkaProducer"`, `rg -n "httpx|requests\.|fetch\(|axios"`, plus `docker-compose*.yml`, `k8s/`, `*.tf`, `Procfile`, `serverless.yml`.

## 7. Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| `Parse error ... got 'end'` | node id `end` | rename to `End` / `done` |
| `got '%'` or `got 'NODE_STRING'` on a line with `%%` | comment after code on the same line | move the comment to its own line |
| `Expecting 'SQE' ... got 'PS'` | unquoted `(` `)` in a `[ ]` label | quote the label |
| `got 'PIPE'` | unclosed `[` before an edge label | close the bracket |
| Sequence: `Expecting 'TXT', got 'NEWLINE'` | message without `:` text | add `: text` |
| Diagram renders but text invisible in dark mode | fill without `color:` | add `color:` to every classDef |
| Subgraph swallows everything after it | missing `end` | close it; `lint_mermaid.py` points at the opener |
| `class X foo` has no effect | classDef `foo` missing or misspelt | define it; lint reports `class-undefined` |
| GitHub shows the code, not a diagram | fence isn't exactly ```` ```mermaid ```` or the type isn't supported there | fix the fence; fall back to flowchart |
| Confluence shows code | Confluence doesn't render Mermaid natively | ship the PNG/SVG via `--replace` |
| `mmdc` hangs or "Failed to launch the browser" | no Chrome, or sandbox | `render_mermaid.sh` passes `--no-sandbox`; set `PUPPETEER_EXECUTABLE_PATH` |
| Long lines everywhere, tangled | too many nodes or mixed levels | split; choose LR vs TD by the main path |
| Labels overlapping lines | dense graph | fewer nodes, shorter labels, or `diagram_html.py` with explicit grid |
| Emoji show as boxes | renderer font lacks them | drop them or install an emoji font |
