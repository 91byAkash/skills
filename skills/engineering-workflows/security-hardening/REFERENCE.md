# Security Hardening: Control Patterns

Open the section matching the code you are touching. Examples use Node/TypeScript and Python; the rule matters more than the syntax.

## Contents
- Injection
- Cross-site scripting
- Access control
- Authentication and sessions
- Headers, CORS, error responses
- Input validation
- File uploads
- Server-side request forgery
- Destructive operations on derived paths
- Rate limiting
- Secrets
- Dependency triage
- Personal data
- LLM output and agent tools

## Injection

Rule: data never becomes code. Use placeholders, argument arrays, and safe loaders.

```ts
// SQL
await db.query("SELECT * FROM users WHERE email = $1", [email]);      // yes
await db.query(`SELECT * FROM users WHERE email = '${email}'`);       // no
// Shell: pass an argv array, never a string through a shell
execFile("convert", [inputPath, "-resize", "200x200", outPath]);     // yes
exec(`convert ${inputPath} -resize 200x200 ${outPath}`);             // no
```

```python
cur.execute("SELECT * FROM users WHERE email = %s", (email,))
subprocess.run(["git", "log", "--", path], check=True)   # no shell=True
yaml.safe_load(text)                                       # never yaml.load on untrusted input
```

- Dynamic identifiers (sort column, table name): map from an allowlist, never interpolate.
- NoSQL: reject objects where scalars are expected (`{"$gt": ""}` as a password).
- Templates: never render user input as a template source (server-side template injection).
- Deserialization: no `pickle`, Java native serialization, or `unserialize` on untrusted bytes; use JSON plus schema validation.
- XML: disable external entities and DTDs.

## Cross-site scripting

- Let the framework escape. Every raw-HTML escape hatch (`dangerouslySetInnerHTML`, `v-html`, `|safe`, `innerHTML`) needs an allowlist sanitizer (e.g. DOMPurify) and a comment explaining why.
- Context matters: HTML body, attribute, URL, JS string, and CSS each need different encoding. Never put user data inside `<script>` blocks; pass it via `data-` attributes or a JSON script tag with `<` escaped.
- URLs from users: allow only `https:` (and `mailto:` if needed). `javascript:` links are XSS.
- CSP as a second layer: start with `default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'` and tighten. Avoid `'unsafe-inline'` for scripts; use nonces.

## Access control

Rule: authorize the specific object on every request, server-side, at the last trusted decision point.

```ts
const doc = await Docs.findOne({ id: req.params.id, ownerId: req.user.id });
if (!doc) return res.status(404).end();   // 404, not 403, to avoid confirming existence
```

- Scope queries by tenant/owner in the query itself, not by filtering afterwards.
- Check mutations too (update/delete/export), plus bulk and list endpoints, search, and GraphQL resolvers per field.
- Role checks belong in one middleware/policy layer, deny by default.
- Never take `userId`, `role`, `tenantId`, or `isAdmin` from the request body.

## Authentication and sessions

- Password hashing: argon2id (memory ≥ 19 MiB, t ≥ 2) or bcrypt cost ≥ 12, or scrypt. Never SHA-* alone.
- Login and reset: rate limit (about 10 attempts / 15 min per account and per IP), identical responses for "no such user" and "wrong password", reset tokens single-use, ≥ 128 bits random, expiry ≤ 1 hour, stored hashed.
- Sessions: regenerate the session ID at login and privilege change; invalidate on logout and password change.
- Cookie: `HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=<bounded>`. `SameSite=None` requires a CSRF token.
- JWT: pin the algorithm, verify `exp`, `aud`, `iss`; never accept `alg: none`; keep them short-lived and keep a revocation path.
- Secret for signing comes from the environment and is ≥ 32 random bytes.

## Headers, CORS, error responses

| Header | Value |
|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | see XSS above |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `X-Frame-Options` / `frame-ancestors` | `DENY` / `'none'` unless embedding is a feature |

- CORS: explicit origin list from config; never reflect `Origin` blindly; never `*` with credentials.
- Errors: generic body (`{"error":"internal"}` plus a request ID); details to server logs only. Debug mode off in production.
- Responses: serialize through an allowlist of fields so `passwordHash`, reset tokens, and internal flags never leak.

## Input validation

Validate shape, type, length, range, enum, and format at the boundary with a schema; reject with 400/422 and structured details; pass only the parsed value onward.

```ts
const Body = z.object({
  email: z.string().email().max(254),
  name: z.string().min(1).max(100),
  plan: z.enum(["free", "pro"]),
}).strict();                       // unknown keys rejected
const body = Body.parse(req.body);
```

```python
class Body(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    name: constr(min_length=1, max_length=100)
```

Also cap request body size at the server (e.g. 1 MB for JSON) and set timeouts.

## File uploads

- Allowlist MIME types and check magic bytes; the extension and `Content-Type` header prove nothing.
- Cap size at the proxy and the app.
- Store outside the web root under a generated name (UUID); never use the client filename as a path.
- Serve with `Content-Disposition: attachment` and the stored type, or from a separate origin.
- Archives: cap entry count and total uncompressed size (zip bombs); reject entries with `..` or absolute paths (zip slip).
- Images: re-encode to strip metadata and polyglot payloads.

## Server-side request forgery

Applies to webhooks, import-from-URL, link previews, image proxies, PDF renderers.

1. Allowlist scheme (`https`) and, where possible, host.
2. Resolve DNS yourself; reject if **any** resolved address is loopback, private (10/8, 172.16/12, 192.168/16), link-local (169.254/16, including cloud metadata), CGNAT (100.64/10), unique-local IPv6 (fc00::/7), or `::1`.
3. Connect to the address you validated (pin it) so DNS rebinding cannot swap it.
4. Disable redirects or re-validate each hop.
5. Cap response size and time; never return raw upstream bodies or errors to the caller.
6. Prefer an egress proxy with its own allowlist for anything high-risk.

## Destructive operations on derived paths

A delete/move/overwrite target is only as trustworthy as whoever *wrote* the value, not the channel it came through (a job payload or another process's arguments are as hostile as a form field). Before acting, require all three:

1. The **resolved** path (symlinks followed, `realpath`) is under an allowlisted root.
2. It is strictly below that root, never the root itself.
3. Ownership evidence comes from authenticated state (your DB row says this job owns this directory), not from a marker file inside the tree, which anything with write access could plant.

Then act on a handle, not a re-resolved string, to avoid check-then-use races (open the directory, verify, operate relative to the descriptor), or accept and document the race window.

```bash
target=$(realpath -e -- "$dir") || exit 1
case "$target" in "$ROOT"/?*) ;; *) echo "refusing: $target" >&2; exit 1;; esac
```

## Rate limiting

- General API: e.g. 100 requests/min per token. Auth endpoints: about 10 / 15 min per account and per IP. Expensive endpoints (export, search, AI calls): per-user quotas.
- With more than one instance, back limits with a shared store (Redis or the database). In-memory counters become `limit × instances` and never fire on serverless.
- Return 429 with `Retry-After`. Log limit hits as security events.

## Secrets

- Loaded from environment or a secret manager; `.env.example` committed with placeholders; `.env*` and key files gitignored.
- Scan staged changes before committing: `scripts/secret-scan.sh`.
- Never in logs, URLs (query strings end up in logs), client bundles (`NEXT_PUBLIC_`, `VITE_` prefixes ship to browsers), or error messages.
- A secret that reached any remote is compromised: rotate first, then clean history if you must.
- Separate secrets per environment; least-privilege scopes on API keys.

## Dependency triage

```
audit reports critical/high
├─ Is the vulnerable function reachable from runtime code?  no → schedule, note why
├─ Patched version within the same major?                   yes → upgrade now, run tests
├─ Only a major bump fixes it?                              → plan the upgrade; mitigate meanwhile (input guard, config)
└─ No fix exists?                                           → mitigate, pin, document, set a review date
```

- New dependency checklist: exact name (typosquats like `crossenv`), weekly downloads and age, maintainer change history, install scripts (`preinstall`/`postinstall`), what it pulls transitively.
- Disable lifecycle scripts by default where the package manager supports it and allowlist the few that need them.
- Commit the lockfile; review lockfile diffs in PRs; install with the frozen/CI mode (`npm ci`, `pnpm i --frozen-lockfile`, `pip install --require-hashes`).

## Personal data

- Classify each new field: non-personal, personal, sensitive (health, financial, government ID, precise location).
- Collect only for a stated purpose; keep PII out of analytics events and logs (hash or drop).
- Set retention at design time and implement deletion that reaches caches, search indexes, analytics copies, and backups (or document backup expiry).
- Support export / correction / deletion where your jurisdiction requires it; design schemas so one user's data is findable.
- Sending PII to any vendor (analytics, ads, LLM APIs) is sharing; it needs consent or a documented basis.
- Do not assume one regime: GDPR (EU/UK), India's DPDP Act 2023, and US state laws (e.g. CCPA/CPRA) differ on consent, breach notice and cross-border transfer. Name the ones that apply in the hand-off note.

## LLM output and agent tools

- Treat model output as untrusted input: validate against a schema before use, encode before rendering, never pass it to `eval`, SQL, or a shell.
- Retrieved documents, web pages, and tool results can contain instructions (prompt injection). Keep them in a data channel; never let them choose tool targets or widen permissions.
- Tools: least privilege, allowlisted targets, explicit confirmation for irreversible or external actions (send, pay, delete, share).
- Do not put secrets in prompts; assume the system prompt can be extracted.
- Cap tokens, tool calls, and spend per request and per user.
