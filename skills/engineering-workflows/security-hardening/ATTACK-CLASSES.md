# Attack Classes for Audits

Pick classes based on what reconnaissance found. Each class lists what to look for and the question that decides whether it is a finding. Apply the validation rules at the bottom before promoting anything.

## Web protocol and authentication
- **Request parsing disagreements**: proxy and app parse headers, paths, or bodies differently (smuggling, path normalisation `..;/`, double encoding). Does a lower-trust request reach a route the proxy meant to block?
- **Cache poisoning / deception**: unkeyed headers change the response; private pages cached under public keys. Can one user's response be served to another?
- **Auth flow flaws**: OAuth `state`/PKCE missing, redirect URI prefix matching, token in URL, account linking by unverified email, MFA skippable by calling the next step directly.
- **Session handling**: fixation, no rotation at login, logout not revoking, long-lived tokens without revocation.
- **CSRF**: state change via GET, `SameSite=None` without token, JSON endpoints accepting `text/plain`.

## Business logic
- **State machine violations**: skipping or repeating steps (pay → refund → refund).
- **Races with business impact**: double spend, coupon reuse, limit bypass via parallel requests. Is there a transaction/lock/unique constraint?
- **Numeric manipulation**: negative quantities, overflow, rounding, currency mismatch.
- **Time logic**: trial reset, expiry evaluated on client clock, timezone edges.
- **Defaults and fallbacks**: missing config → permissive mode; unknown role → admin.
- **Multi-step boundary failures**: check in step 1, use in step 3 with a swapped ID.

## Data isolation and lifecycle
- **Object-level authorization (IDOR)** across reads, writes, lists, search, exports, attachments, and websockets.
- **Derived data leaks**: search indexes, caches, thumbnails, analytics, logs, and error messages containing other tenants' data.
- **Search/filter/sort as oracle**: filtering on a field you cannot read reveals it.
- **Export/backup as exfiltration; import/restore as injection**: does restore trust IDs or owner fields in the file?
- **Deletion and revocation**: removed members keep access via tokens, share links, cached permissions, or background jobs.
- **Preview/draft/staging leakage**: unpublished content reachable by guessable URL.

## Client-side and browser
- **DOM XSS**: sources (`location`, `postMessage`, storage) reaching sinks (`innerHTML`, `eval`, `href`).
- **postMessage**: missing origin check on receive; `*` target on send with secrets.
- **Prototype pollution** via merge/clone of user JSON.
- **Service worker / storage**: tokens in `localStorage`; cache serving authenticated responses after logout.
- **Cross-site leaks and UI redress**: framing without `frame-ancestors`; open redirects used in phishing or OAuth.

## AI, LLM, and agents
- **Indirect prompt injection** through retrieved documents, emails, web pages, tool output, file names.
- **Tool misuse**: model-chosen arguments reach privileged tools without allowlists or confirmation.
- **Cross-user memory/context bleed**: shared caches, vector stores without tenant filters.
- **Output handling**: model output rendered as HTML, executed, or used in queries.
- **Disclosure**: secrets in system prompts, tool schemas, or logs.
Decisive question: can content controlled by one principal make the agent act with another principal's authority?

## Supply chain and release
- Unpinned or typosquatted dependencies; install scripts running in CI with secrets.
- CI triggered by untrusted forks with access to secrets; untrusted input interpolated into CI shell steps.
- Release artifacts unsigned or built from mutable inputs; update channels without signature checks.

## Cloud and deployment
- Over-broad workload identities; metadata endpoint reachable from user-influenced fetches.
- Public buckets or signed URLs with long expiry; debug or admin ports exposed.
- Secrets in images, env dumps, or build logs; containers running as root with host mounts.
Only report what the repository's config shows. Unseen infra is `needs_validation`, not assumed.

## Protocols, RPC, and messaging
- Schema confusion between producer and consumer; unknown fields trusted.
- RPC methods missing per-call authorization because "internal".
- Queue topics shared across tenants; consumers trusting `tenantId` in the message.
- Replay of signed messages without nonce/timestamp; out-of-order processing breaking invariants.

## Resource exhaustion
- Algorithmic amplification: regex backtracking (ReDoS), quadratic parsing, unbounded pagination, GraphQL depth/complexity.
- Accumulation: unbounded uploads, queues, retries, log growth.
- Quotas: per-user limits missing on expensive operations (exports, AI calls, emails).
- Failure handling: retry storms, missing timeouts, crash loops on a poison message.

## Memory safety and native code
- Bounds and integer errors in parsers; length fields trusted.
- Use-after-free, double free, data races in unsafe/FFI code.
- FFI boundaries passing unchecked lengths or lifetimes.
- Privileged helpers and local IPC reachable by unprivileged processes; deep links and webview bridges exposing native functions.

## Validation rules (apply to every candidate)

1. Name the lower-trust principal, the input they control, the intended control, the boundary crossed, and the concrete result. Missing any → not a finding.
2. Same principal affecting only themselves is not a boundary violation.
3. Report the effect you observed, not a stronger one you imagine.
4. A required control that lives outside the repository (proxy rule, cloud policy, header set at the edge) makes the item `needs_validation` with that fact named.
5. Proof is local only: unit test, fixture, dummy-tenant integration test. Never shared or production systems.
6. Defence-in-depth suggestions without a reachable violation go in a separate "hardening suggestions" list, not in findings.
