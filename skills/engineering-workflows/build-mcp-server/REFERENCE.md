# MCP Server Reference

## Contents
- Naming
- Tool design rules
- Descriptions
- Response format
- Pagination and truncation
- Errors
- Annotations
- Resources and prompts
- Transports
- Security
- Testing and evaluation
- Review checklist

## Naming

| Thing | Convention | Example |
|---|---|---|
| TS package | `<service>-mcp-server` | `acme-tickets-mcp-server` |
| Python module | `<service>_mcp` | `acme_tickets_mcp` |
| Tool | `<service>_<verb>_<resource>`, snake_case | `acme_list_projects` |
| Verbs | `search` (fuzzy), `list` (enumerate), `get` (one by ID), `create`, `update`, `delete`, domain verbs (`assign`, `merge`) | |

The service prefix matters because agents load several servers at once; `create_issue` collides, `acme_create_issue` does not. No version numbers in names.

## Tool design rules

1. Start from workflows. Write the sequence of calls an agent would make for each; if two calls always go together, consider one tool.
2. Cover the common operations broadly enough that agents can compose novel tasks; add workflow tools where they save several round trips.
3. Make outputs carry the IDs and handles needed for the next call.
4. Accept what agents know: names, emails, URLs. Resolve to IDs inside the tool when it is cheap and unambiguous; when ambiguous, return candidates.
5. Bound everything: string lengths, list sizes, date ranges.
6. Prefer enums to free strings for modes and statuses.
7. Avoid boolean soup; if a tool has many flags that change behaviour, split it.
8. Keep the count manageable (roughly 5 to 30 tools). Group rarely used admin operations behind a separate server if needed.

## Descriptions

A good tool description has:
- one sentence on what it does
- when to use it instead of its siblings ("Use acme_get_ticket when you already have an ID")
- what it returns (key fields)
- constraints (rate limits, max range)
- one example call

Every field description says the format and gives an example (`"ISO date, e.g. 2026-03-01"`). Descriptions must match behaviour exactly; agents trust them.

## Response format

- Offer `response_format: "markdown" | "json"`, default markdown.
- Markdown: headings per item, key fields only, human-readable dates, IDs in parentheses. Good for reading and summarising.
- JSON: full, stable field names, machine-friendly timestamps. Good for chaining and filtering.
- Where the SDK supports it, declare an output schema and return structured content alongside text.
- Omit noise: internal URLs, null fields, deeply nested metadata the agent never needs.

## Pagination and truncation

```json
{ "items": [...], "count": 20, "total": 413, "has_more": true, "next_cursor": "eyJvZmZzZXQiOjIwfQ" }
```
- Default `limit` 20, max 100. Never load all records into memory to slice.
- Pass through the service's cursor if it has one; otherwise encode offset.
- Cap any single response at about 25,000 characters. When truncating, keep whole items, set `truncated: true`, and add a hint: "Narrow with `status` or `updated_after`, or lower `limit`."

## Errors

Return errors as tool results with `isError: true` and text that tells the agent what to do next:

| Upstream | Message pattern |
|---|---|
| 400 validation | "Invalid `due_date` '31/02'. Use ISO format YYYY-MM-DD." |
| 401/403 | "Not authorised for project P-9. The configured key can access: P-1, P-4." |
| 404 | "No ticket T-123. Use acme_search_tickets to find IDs." |
| 409 | "Ticket T-12 was modified since you read it. Fetch it again, then retry." |
| 429 | "Rate limited; retry after 30 s or reduce `limit`." |
| 5xx / timeout | "Acme API unavailable (503). Try again shortly." |

Never leak stack traces, tokens, or internal hostnames.

## Annotations

| Hint | Meaning | Example |
|---|---|---|
| `readOnlyHint` | does not modify anything | search, get |
| `destructiveHint` | may delete or overwrite data | delete, bulk update |
| `idempotentHint` | repeating with the same args has no extra effect | set status, upsert |
| `openWorldHint` | talks to an external system | any API call (false for a local pure computation) |

Clients use these to decide when to ask for confirmation. Set them honestly.

## Resources and prompts

- Resources: read-only data addressed by URI (`acme://tickets/T-1043`, `file:///reports/weekly.md`). Use for documents or records the client may attach as context; templates allow parameterised URIs.
- Prompts: named, parameterised message templates a user can invoke ("triage-ticket" with `ticket_id`). Optional; tools are what agents use most.

## Transports

Spec revision: **2026-07-28** (current; previous 2025-11-25). It made the core stateless: no `initialize` handshake and no `Mcp-Session-Id`; each request carries its protocol version and client capabilities in `_meta`, and servers must answer `server/discover`. Current SDKs (TypeScript v2 `@modelcontextprotocol/server`, Python `mcp` 2.x) serve both the 2026 and the older handshake clients from one server, so you rarely touch this directly. Check the spec changelog for anything newer before relying on a detail.

| Transport | Use for | Notes |
|---|---|---|
| stdio | local, single user, CLI-launched | stdout is the protocol stream; log to stderr only. TS v2: `serveStdio(buildServer)`; Python: `mcp.run()` |
| Streamable HTTP | remote, multi-client, web-hosted | single POST endpoint; no protocol sessions in 2026-07-28, so keep cross-call state in explicit handles passed as tool arguments. Scales behind a plain load balancer |
| HTTP+SSE | never for new servers | deprecated since 2025-03-26, formally scheduled for removal; migrate to Streamable HTTP |

Also deprecated in 2026-07-28 (do not build on them): Roots, Sampling and the Logging capability (pass paths as tool arguments, call an LLM API directly, log to stderr or OpenTelemetry). Server-initiated requests (elicitation, sampling) became multi round-trip results (`input_required`); let the SDK handle this.

Client config for a stdio server (shape varies slightly by client):
```json
{ "mcpServers": { "acme-tickets": { "command": "node", "args": ["/abs/path/dist/index.js"], "env": { "ACME_API_KEY": "..." } } } }
```

## Security

- Secrets from environment variables; fail at startup with a clear message if missing.
- Validate all inputs with the schema; treat everything the agent sends as untrusted (it may be steered by injected content).
- Enforce scope server-side (allowed projects, read-only mode flag). Do not rely on the agent to behave.
- For HTTP: require auth, validate `Origin`/`Host` (DNS rebinding), bind to `127.0.0.1` for local use, use TLS remotely.
- Remote auth follows the spec's OAuth 2.1 profile: the MCP server is a *resource server*. Publish Protected Resource Metadata (RFC 9728) pointing at your authorization server, return `401` with `WWW-Authenticate` when the token is missing, and accept only tokens issued for this server (audience bound via RFC 8707 resource indicators). Never pass the client's token through to upstream APIs; get a separate upstream token. Clients register with Client ID Metadata Documents; Dynamic Client Registration is deprecated but still supported. Use the SDK's auth helpers rather than hand-rolling this.
- Static API keys or bearer tokens are fine for single-tenant internal servers; per-user access needs OAuth.
- Confirm-worthy operations (delete, send, pay) get `destructiveHint: true`, and consider a `dry_run` parameter.
- Log tool calls (name, args without secrets, latency, outcome) to stderr or a file for debugging.

## Testing and evaluation

- Unit-test helpers (pagination, formatting, error mapping) with a mocked HTTP client.
- Smoke test the protocol: `python3 scripts/mcp-smoke.py --list -- <server command>` (options before `--`; `--protocol legacy` forces the old handshake to check older clients still work).
- Evaluation questions must be: independent; answerable with read-only calls; multi-step (needing several tools or pages); realistic; single verifiable answer (name, number, date, ID); stable over time.
- Good: "Among tickets closed in Q1 2026 tagged 'sso', which customer had the most? Give the domain." Poor: "How many tickets are open?" (changes), "Create a ticket" (write), "What does acme_get_ticket do?" (not a task).
- For each failed question, label the cause: wrong tool chosen (naming/description), missing data in output, pagination misunderstood, error unhelpful, tool missing. Fix the server, not the question.

## Review checklist

- [ ] Names follow `<service>_<verb>_<resource>`; no collisions with generic names.
- [ ] Each description states purpose, when to use, returns, example.
- [ ] Every input typed and bounded; enums where possible.
- [ ] Lists paginate with `has_more`/`next_cursor`; responses truncate with guidance.
- [ ] Markdown and JSON formats both work.
- [ ] Errors are actionable and never leak internals.
- [ ] Annotations set on every tool.
- [ ] Shared client/auth/error code; no duplicated request logic.
- [ ] No stdout logging in stdio mode.
- [ ] Secrets only from env; startup fails clearly without them.
