---
name: build-mcp-server
description: "Design, build, smoke-test and evaluate an MCP (Model Context Protocol) server that exposes an API, database or local tool to agents. Use when asked to \"build an MCP server\", wrap a service for agent use, fix an MCP server whose tools confuse agents or flood context, or pick transport and auth. Not for writing an agent skill (use write-agent-skill)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Build an MCP Server

Targets spec revision 2026-07-28 with the v2 SDKs (TypeScript `@modelcontextprotocol/server`, Python `mcp` 2.x), which also serve older-protocol clients.

An MCP server exposes **tools** (actions the agent calls), **resources** (data the client can read by URI), and optionally **prompts** (reusable templates). Its quality is measured by one thing: can an agent complete real tasks with it, quickly and without wasting context.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `service` | required | — | "Acme Tickets REST API v2" or "local SQLite analytics DB" |
| `workflows` | required | — | "find open tickets for a customer; summarise a ticket thread; reassign and comment" |
| `language` | optional | TypeScript | `python` |
| `transport` | optional | `stdio` for local tools, Streamable HTTP for remote/multi-user (never the deprecated HTTP+SSE) | `http` |
| `auth` | optional | API key from env var | OAuth 2.1 (spec authorization profile) for per-user remote access |
| `write_access` | optional | read-only first | "allow create/update; no delete" |
| `server_name` | optional | `<service>-mcp-server` (TS) / `<service>_mcp` (Python) | `acme-tickets-mcp-server` |
| `eval_count` | optional | 10 | 20 for a large API |

## Output

- A runnable server project (source, package/dependency file, README with install, env vars, and client config snippet).
- A tool list with names, one-line purposes, annotations, and input schemas.
- Smoke-test output from [scripts/mcp-smoke.py](scripts/mcp-smoke.py) showing `server/discover` (or `initialize` for older SDKs), `tools/list`, and at least one successful `tools/call`.
- An evaluation file (`evaluation.xml`) with `eval_count` verified question/answer pairs, and the results of running them.

## Supporting files

- [REFERENCE.md](REFERENCE.md): tool design rules, naming, response format, pagination and truncation, errors, annotations, transports, security, testing. Read during design (step 2) and review (step 6).
- [templates/server.ts](templates/server.ts) and [templates/server.py](templates/server.py): skeletons with one read tool, one write tool, shared client, pagination, truncation, and actionable `isError` results. The Python one runs on SDK 2.x (`MCPServer`) and falls back to 1.x (`FastMCP`); the TS one uses SDK v2 (`@modelcontextprotocol/server`, `serveStdio`, `z.object` input schemas) and its header lists the package/tsconfig settings and the v1 differences. Copy the one matching `language` at step 4, renaming the server to `server_name`.
- [templates/evaluation.xml](templates/evaluation.xml): evaluation format with example pairs. Use at step 8.
- [scripts/mcp-smoke.py](scripts/mcp-smoke.py): stdlib-only stdio client: probes `server/discover` (2026-07-28) and falls back to the `initialize` handshake, lists tools, calls a tool; exits 1 on protocol errors, unknown tools, or `isError` results. Run `python3 scripts/mcp-smoke.py --help`.

## Steps

1. **Understand the service.** Read its API docs: auth method, rate limits, pagination style, key objects and IDs, error format. Note which endpoints the `workflows` need. If the service has a sandbox or test account, use it.
2. **Design tools around workflows, not endpoints.** For each workflow, sketch the calls an agent would make. Then:
   - one tool per distinct intent (`acme_search_tickets`, `acme_get_ticket`, `acme_add_comment`)
   - merge steps the agent would always chain (fetch ticket + its last 20 messages in `acme_get_ticket`)
   - keep broad coverage for common operations so agents can compose; add workflow tools only where they save several calls
   - name as `<service>_<verb>_<resource>`, snake_case, verbs `search/list/get/create/update/delete`
   - IDs the agent needs next must appear in outputs; accept human-friendly inputs (names, emails) where lookup is cheap
3. **Write the tool table** (name, purpose, inputs with types/limits, output fields, annotations) and **checkpoint with the user** before coding. Default to read-only tools; add writes only as allowed by `write_access`.
4. **Scaffold** from the template for `language`. Put the API client, auth, error mapping, pagination, and formatting in shared helpers; tools stay thin.
5. **Implement each tool:**
   - input schema with types, bounds, enums, and a described example per field (Zod / Pydantic)
   - description: what it does, when to use it versus siblings, what it returns, one example
   - `limit` (default 20, max 100) and `cursor`/`offset` on every list/search; return `has_more` and `next_cursor`
   - `response_format`: `markdown` (default, concise, for reading) or `json` (full fields, for chaining); return structured content too where the SDK supports an output schema
   - truncate responses over ~25,000 characters with a note on how to narrow the query
   - errors as tool results (`isError`; in Python raise `ToolError`, since other exceptions reach the model only as a bare "Error executing tool") that say what went wrong and what to try next ("No ticket 123. Use acme_search_tickets to find IDs."), never raw stack traces
   - annotations: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`
6. **Review** against the checklist in [REFERENCE.md](REFERENCE.md#review-checklist): no duplicated logic, consistent errors, full typing, descriptions match behaviour, secrets only from env.
7. **Build and smoke test.**
   - TS: `npx tsc` (package/tsconfig settings in the template header) then `python3 scripts/mcp-smoke.py --call acme_search_tickets '{"query":"refund","limit":3}' -- node dist/index.js`
   - Python: `python3 -m py_compile server.py` then `python3 scripts/mcp-smoke.py --call acme_search_tickets '{"query":"refund","limit":3}' -- python3 server.py`
   - Options go before `--`; everything after it is the server command. Point the server at a sandbox or a local stub API (`ACME_API_URL=http://127.0.0.1:8765`) for the call.
   - Also call one tool with a bad ID: the output must say `ERROR` (an `isError` result) with a next-step hint, not `ok`.
   - Optionally inspect interactively with an MCP inspector UI.
   Run once more with `--protocol legacy` if older clients must keep working.
   If `server/discover` or `initialize` fails → the process writes to stdout outside the protocol (log to stderr instead) or crashes on missing env vars.
8. **Evaluate.** Using only read-only calls, explore real data and write `eval_count` questions that each need several tool calls, have one short verifiable answer, and will not change over time (closed tickets, past dates). Solve each yourself to confirm the answer. Save as `evaluation.xml`. Run an agent with only this server against the questions; for each miss, decide whether the tool name, description, output, or missing tool caused it, fix, rerun.
9. **Document**: README with purpose, tool list, env vars, client config JSON, transport, and known limits.

## Checkpoints

- After step 3: tool table approved (names, write scope).
- After step 7: smoke test passes before writing evaluations.
- After step 8: accuracy reported; misses traced to a cause.

## Worked example

`service`: Acme Tickets API; `workflows`: "find a customer's open tickets and summarise the latest one".

| Tool | Purpose | Key inputs | Annotations |
|---|---|---|---|
| `acme_search_tickets` | find tickets by text, customer email, status | `query?`, `customer_email?`, `status` enum, `limit` 1–100 (20), `cursor?`, `response_format` | read-only, idempotent, open-world |
| `acme_get_ticket` | ticket + last N messages | `ticket_id`, `messages` 1–50 (20) | read-only, idempotent |
| `acme_add_comment` | add an internal or public comment | `ticket_id`, `body` ≤ 5000, `public` bool (false) | not read-only, not destructive, not idempotent |

Agent run: `acme_search_tickets(customer_email="li@corp.test", status="open")` → markdown list with IDs → `acme_get_ticket(ticket_id="T-1043")` → summary. Two calls, no guessing.

Evaluation pair: "Which agent closed the oldest ticket tagged 'billing-migration' in March 2026? Answer with their email." → `ops-7@acme.test`.

## Pitfalls

- One tool per endpoint (60 tools) so the agent cannot choose; or one mega-tool with a `mode` string that hides what it does.
- Returning entire API payloads; agents drown. Default to the fields that matter, offer `json` for detail.
- Lists without `limit`/pagination, or pagination that does not tell the agent there is more.
- Printing logs to stdout in a stdio server; it corrupts the protocol stream.
- Throwing exceptions instead of returning actionable error text.
- Descriptions that promise behaviour the tool does not have.
- HTTP transport bound to `0.0.0.0` without auth or Origin checks (DNS rebinding); bind to `127.0.0.1` locally.
- Passing the client's OAuth token straight to the upstream API (token passthrough is forbidden by the spec), or keeping per-session state that a stateless 2026 server cannot rely on.
- Following a v1-era tutorial: `@modelcontextprotocol/sdk` imports, `from mcp.server.fastmcp import FastMCP`, or an SSE transport.
- Evaluation questions whose answers change (counts of open items) or that need write operations.

## Done when

- [ ] Tool table matches the workflows and was approved; writes limited to `write_access`.
- [ ] Every tool has typed, bounded inputs, a precise description, annotations, and actionable errors.
- [ ] Lists paginate and responses truncate with guidance.
- [ ] Build/compile passes and the smoke test shows discover/initialize, tools/list, and a successful call.
- [ ] `evaluation.xml` has `eval_count` verified, stable, read-only questions; accuracy and fixes reported.
- [ ] README covers install, env vars, client config, and limits; no secrets in code.
