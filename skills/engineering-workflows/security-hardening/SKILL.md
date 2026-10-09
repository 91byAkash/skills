---
name: security-hardening
description: "Harden code as you build it, or audit a codebase for exploitable vulnerabilities and report each proven finding with severity and the smallest fix. Use when code touches auth, user input, uploads, webhooks, payments, PII, secrets, SSRF or LLM output, or the user asks for a \"security review\" or \"audit\". Not for general code review (use review-diff) or pentesting systems you do not own."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Security Hardening

Two modes share one evidence bar:

- **harden**: you are building or changing a feature. Threat-model it, apply the controls, prove the abuse cases fail.
- **audit**: you are reviewing existing code. Map boundaries, hunt by attack class, validate every candidate locally, report only what you can demonstrate.

A finding is a *reachable boundary violation with a concrete result*, never a checklist deviation. Tag each with a CWE id; when the reader expects OWASP categories, use the current **OWASP Top 10:2025** (A01 Broken Access Control, A02 Security Misconfiguration, A03 Software Supply Chain Failures, A04 Cryptographic Failures, A05 Injection, A06 Insecure Design, A07 Authentication Failures, A08 Software or Data Integrity Failures, A09 Security Logging and Alerting Failures, A10 Mishandling of Exceptional Conditions), not the 2021 list.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `target` | required | — | `services/api/` or the PR diff `main...feature/upload` |
| `mode` | optional | `harden` if a change is in progress, else `audit` | `audit` |
| `scope` | optional | whole target | `src/auth/**, src/billing/**` |
| `profile` (audit) | optional | `standard` | `quick` (small target / re-run), `deep` (high stakes) |
| `stack` | optional | detected from manifests | `Node 20 + Express + Postgres` |
| `assets` | optional | inferred | "customer PII, card tokens, admin actions" |
| `prior_findings` | optional | none | `security/findings.json` from the last run |
| `out_dir` | optional | `security/` | `docs/security/2026-10/` |
| `execution` | optional | `local-only` (the only allowed value: local code, local fixtures, dummy data) | `local-only` |

## Output

- **harden**: the change with controls applied, plus at least one abuse-case test per trust boundary touched, and a short note listing boundaries, controls, and anything deferred.
- **audit**: `out_dir/findings.md` (human report, from [templates/report.md](templates/report.md)), `out_dir/findings.json` (one record per candidate, shape in [templates/finding.json](templates/finding.json)), and `out_dir/coverage.md` (what was and was not examined, from [templates/coverage.md](templates/coverage.md)). States: `confirmed`, `needs_validation`, `rejected`. Only `confirmed` gets a severity.

## Supporting files

- [REFERENCE.md](REFERENCE.md): concrete control patterns (injection, XSS, access control, sessions, headers/CORS, validation, uploads, SSRF, destructive paths, rate limiting, secrets, dependencies, privacy, LLM output). Read the section you need when you reach that code.
- [ATTACK-CLASSES.md](ATTACK-CLASSES.md): hunting catalogue by domain (web/auth, business logic, data isolation, client-side, AI/agents, supply chain, cloud, protocols, availability, memory safety). Read in audit mode when planning coverage.
- [templates/report.md](templates/report.md), [templates/finding.json](templates/finding.json), [templates/coverage.md](templates/coverage.md): audit deliverables (the coverage file holds the recon inventory and the step-3 ledger).
- [scripts/secret-scan.sh](scripts/secret-scan.sh) `[--path DIR]`: scans staged changes (or a directory) for likely secrets; exit 0 clean, 1 hits, 2 usage error. A regex net, not a replacement for a dedicated scanner (gitleaks, trufflehog) in CI. Run before every commit in harden mode and at the start of an audit.

## Steps: harden mode

1. **Map trust boundaries** the change touches: HTTP params/bodies/headers, forms, uploads, webhooks, queue messages, third-party API responses, files read from disk, env/CLI args, and LLM output. If you cannot list them, stop and list them first.
2. **Name the assets** (credentials, PII, money movement, admin actions) and run STRIDE over each boundary:

   - *Spoofing*: could a caller pretend to be a different user or service? Answer with authentication and verified signatures.
   - *Tampering*: could data be altered on the wire or in storage? Answer with TLS, integrity checks and parameterized queries.
   - *Repudiation*: could someone deny having done something? Answer with an audit trail of security-relevant events.
   - *Information disclosure*: could data reach someone who should not see it? Answer with response-field allowlists, error messages that reveal nothing, and encryption.
   - *Denial of service*: could the boundary be flooded or exhausted? Answer with request size limits, timeouts and rate limiting.
   - *Elevation of privilege*: could someone gain rights they were not given? Answer with authorization checked per object and least privilege.

3. **Write abuse cases next to use cases** ("upload a 2 GB file", "fetch `http://169.254.169.254/`", "read invoice 1043 as another tenant"). Each becomes a failing test before the control exists.
4. **Apply controls** from [REFERENCE.md](REFERENCE.md). Non-negotiables:
   - validate input at the boundary with a schema; downstream code uses only the parsed value
   - queries take parameters, always; input is never concatenated into SQL, shell commands or templates
   - output goes through the framework's automatic escaping; if raw HTML truly cannot be avoided, pass it through an allowlist sanitizer first
   - authorize every request against the specific object, not just "is logged in"
   - hash passwords with argon2id / scrypt / bcrypt (cost ≥ 12)
   - session cookies `HttpOnly; Secure; SameSite=Lax` (or `Strict`) with a bounded lifetime
   - secrets from env or a secret store; never in code, logs, client bundles, or error bodies
5. **Ask before** (needs human approval): new auth flows or auth logic changes, new categories of sensitive data, new third-party integrations, CORS changes, upload handlers, rate-limit changes, new roles/permissions.
6. **Never**: commit secrets, log tokens/passwords/full card numbers, trust client-side validation, disable security headers, `eval`/`innerHTML` with user data, store auth tokens in `localStorage`, return stack traces.
7. **Dependencies** you add: check name (typosquats), maintainer, age, install scripts, and lockfile diff; run the ecosystem audit (`npm audit --omit=dev`, `pnpm audit`, `pip-audit`, `cargo audit`, `govulncheck ./...`, `bundle audit`). Never run forced auto-fixes that jump major versions.
8. **Run** `scripts/secret-scan.sh` and the abuse-case tests. If any abuse case passes (the attack works) → the control is wrong; fix before moving on.

## Steps: audit mode

1. **Set up.** Record target, source ref (`git rev-parse HEAD`), profile, scope, and execution policy at the top of `coverage.md`. If `prior_findings` exist: carry a prior `confirmed` record only if its source is unchanged; changed source → revalidate; prior `rejected` suppresses only that exact claim, not the area.
2. **Reconnaissance.** Inventory entry points (routes, RPC handlers, CLI commands, consumers, cron jobs, file parsers, webhooks, admin tools), identity model (who are the principals, how is a tenant/owner determined), data stores, outbound calls, build/release path. Run `scripts/secret-scan.sh --path .`.
3. **Build the coverage ledger** in `coverage.md`: rows = surface × boundary × attack class (pick classes from [ATTACK-CLASSES.md](ATTACK-CLASSES.md) by what recon found). Profile sets granularity: `quick` = one row per surface; `standard` = per surface × class; `deep` = per subsystem × class × lifecycle (create/update/delete/export/restore).
4. **Hunt ledger rows in priority order** (unauthenticated surfaces → cross-tenant → money/privilege → everything else). For each row, trace from input to sink and write a candidate only if you can name: the lower-trust principal, the input they control, the intended control, the boundary crossed, and the concrete result. If parallel helpers are available, give each a disjoint set of rows and require structured candidates back.
5. **Candidate gate.** Drop anything that is: a missing best practice with no reachable violation, self-impact by the same principal, dependent on deployment/proxy behaviour not visible in source (→ `needs_validation`, not a guess), or a stronger effect than observed.
6. **Validate locally.** For each candidate, write the smallest proof: a unit test, a fixture fed to the parser, a dummy-tenant integration test. Never touch shared, staging, or production systems. If the proof works → `confirmed`. If it needs information the repo lacks → `needs_validation` with the exact missing fact. If it fails → `rejected` with why.
7. **Fresh-eyes check.** Re-read every confirmed record cold (or hand it to an independent reviewer): does the cited code still say that? Does the proof actually show the claimed result?
8. **Severity** (confirmed only), capped by the demonstrated impact:
   - **critical**: unauthenticated code execution, full data-store access, or arbitrary account takeover
   - **high**: an explicit control fully defeated with real consequences (auth bypass, cross-tenant read/write, stored XSS against others, authenticated RCE)
   - **medium**: real boundary violation with narrow blast radius or uncommon preconditions
   - **low**: non-secret internals disclosed, or high effort for minimal gain
   - **informational**: minimal impact; useful as a chain prerequisite
   Discriminator high vs medium: does it *fully defeat* the control, or only weaken it?
9. **Fix recommendation**: the invariant the code must enforce, the narrowest change at the last trusted decision point, and the regression test. If asked to fix, fix high/critical first, each with its test.
10. **Write outputs** from the templates. Prose and JSON must agree. End in one of two states: all outputs written, or `coverage.md` says `incomplete` with the exact reason. Never imply one run covered everything.

## Checkpoints

- After step 2 (harden) / step 3 (audit): show the boundary list or ledger before writing controls or hunting.
- Before any fix that changes auth, CORS, roles, or data retention: get approval.
- Before reporting: every `confirmed` record has a reproducible local proof.

## Worked example

Audit, `target=api/`, `profile=quick`. Recon finds `GET /invoices/:id` loads `Invoice.findById(id)` and checks only `req.user` exists.

- Candidate: lower-trust principal = user in tenant B; input = `id`; intended control = tenant ownership; boundary = tenant isolation; result = reads tenant A invoice.
- Proof: integration test seeds tenants A and B, logs in as B, requests A's invoice, gets 200 with A's data.
- Record: `confirmed`, **high** (cross-tenant read fully defeats the isolation control).
- Fix: `Invoice.findOne({ id, tenantId: req.user.tenantId })`, return 404 (not 403) on miss; regression test asserts 404.

A second candidate, "no CSP header", has no reachable injection sink → dropped at the candidate gate; noted in coverage as a hardening suggestion, not a finding.

## Pitfalls

- Scanner or audit output pasted as findings without reachability. Triage by whether the vulnerable code path runs in production.
- Checking authentication but not per-object authorization (IDOR is the most common real bug).
- Validating with a denylist of "bad characters" instead of a schema allowlist.
- SSRF filters that check the hostname string but not every resolved IP, or that follow redirects unchecked.
- In-memory rate limits behind multiple instances (limit × instances) or on serverless (never fires). Use a shared store.
- Deleting a path that came from input or another process without resolving it under an allowlisted root.
- Treating a leaked secret as fixed once removed from git. If it reached a remote, rotate it.
- Assigning severity to `needs_validation` records, or writing the report before validation.

## Done when

- [ ] Trust boundaries and assets are listed (harden) or the coverage ledger exists (audit).
- [ ] Every boundary touched has a passing abuse-case test (harden).
- [ ] `scripts/secret-scan.sh` is clean or every hit is explained.
- [ ] Dependency audit run; critical/high items triaged by reachability.
- [ ] Every confirmed finding has location, proof, severity, invariant, and fix; `needs_validation` items name the missing fact.
- [ ] `findings.md`, `findings.json`, and `coverage.md` agree, and coverage states what was not examined.
- [ ] No testing touched systems outside the local workspace.
