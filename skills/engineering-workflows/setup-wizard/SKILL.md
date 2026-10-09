---
name: setup-wizard
description: "Generate an interactive bash wizard that walks a person through manual setup steps only they can do: creating accounts and API keys, setting CI secrets, one-off cutovers. Use when the user says \"walk me through setting up X\" or setup needs tedious human-only dashboard steps. Not for steps an agent can do itself, or repo hooks (use git-guardrails)."
license: MIT
metadata:
  category: "engineering-workflows"
  version: "3.0.0"
---

# Setup Wizard

Scope: account and API-key creation in third-party dashboards, CI secrets, infrastructure provisioning, one-off cutovers. The wizard opens each URL, gives exact click paths, captures values (secrets hidden), writes `.env` and CI secrets, and confirms before irreversible actions. Runs on bash 3.2+ (macOS default) and Linux.

Turn a manual procedure into a script a stranger could follow: one stage per step, the right URL opened, values captured once and written where they belong.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `procedure` | yes | – | "set up payments + email provider for local dev and CI" |
| `script_path` | optional | `scripts/setup-<slug>.sh` (or a scratch path for one-off use) | `scripts/setup-payments.sh` |
| `env_file` | optional | `.env` | `.env.local` |
| `ci_secret_cmd` | optional | detected CI CLI if installed, else skip with a note | `gh secret set`, `glab variable set` |
| `keep_in_repo` | optional | `no` (ephemeral) | `yes` = commit + link from README |
| `irreversible_steps` | optional | discovered | "delete old DNS record", "rotate production key" |

## Output

- An executable wizard at `script_path` built from [scripts/wizard-template.sh](scripts/wizard-template.sh): banner, numbered stages with progress, opened URLs, precise click paths, hidden entry for secrets, idempotent `.env` upserts, CI secret writes, confirm gates before irreversible actions, and a closing summary of what was written and what was skipped.
- A short note telling the user how to run it, and (if `keep_in_repo`) a README link.

## Supporting files

- [scripts/wizard-template.sh](scripts/wizard-template.sh): wizard library (stage, say, step, open_url, ask, ask_secret, write_env, set_ci_secret, confirm, pause, summary) plus two example stages. Values round-trip safely through `.env` (quotes, backslashes, `$`), closed input stops instead of looping, CI failures show the CLI's error, and the summary warns if `.env` is not git-ignored. Copy it and replace the stages.

## Steps

1. **Scope from the repo, not from questions.** Read `.env.example`/`.env.*`, README setup sections, `docker-compose*`, framework config, and CI workflow files (every secret/variable reference there is a value the wizard must produce). For a cutover: current state, target state, irreversible steps between them.
2. **List stages and values** and confirm with the user. For every captured value record: where the human finds it, where it is written (`.env`, CI secret, both, nowhere), and whether it is secret (hidden input) or public. The list is done when every value has all three.
3. **Map each stage's click path** precisely: URL, menu path, what to copy ("Dashboard → Developers → API keys → Create restricted key → copy"). If you do not know the current UI, say so and ask rather than invent.
4. **Author the script**: copy the template to `script_path`, set the defaults `ENV_FILE="${ENV_FILE:-<env_file>}"` and `CI_SECRET_CMD="${CI_SECRET_CMD:-<ci_secret_cmd>}"` at the top, set `TOTAL_STAGES`, write one `stage` per step in dependency order. Rules: open the URL before asking for its value; `ask_secret` for anything secret; `write_env` for every persisted value; `set_ci_secret` only for names CI actually references; `confirm` before anything irreversible; validate formats where cheap (e.g. key prefix `sk_test_`), re-asking on mismatch.
5. **Make it re-runnable**: existing `.env` values are offered as defaults (Enter keeps them), so Ctrl-C and re-run is safe.
6. **Verify**: `bash -n script` and `shellcheck` if available; `chmod +x`. Do not run it for real yourself (it opens browsers and waits for a person), but smoke-test the plumbing with dummy answers: `printf '\n<dummy value>\ny\n' | WIZARD_NO_OPEN=1 ENV_FILE=/tmp/wiz.env CI_SECRET_CMD=dry-run ./script` must exit 0, write every planned key to `/tmp/wiz.env`, and list nothing unexpected under "skipped"; delete `/tmp/wiz.env` afterwards. Trace: every value from step 2 is captured and lands where planned; every CI secret name matches the workflow reference exactly.
7. **Hand off**: tell the user the command to run. If `keep_in_repo`, commit it and link it from the README setup section; otherwise note it can be deleted after use.

## Checkpoints

- Stage list confirmed by the user before writing.
- No secret is echoed, logged, or passed on a command line visible in `ps` (use stdin for CI CLIs).
- Every irreversible action is behind `confirm`.
- `bash -n` passes and the dummy-answer smoke run writes every planned key.

## Worked example

Procedure: local + CI setup for a payments sandbox and a transactional email provider.
Stages (confirmed): 1 Payments sandbox account → `PAYMENTS_SECRET_KEY` (secret, .env + CI), `PAYMENTS_PUBLISHABLE_KEY` (public, .env); 2 Webhook signing secret via the provider CLI → `PAYMENTS_WEBHOOK_SECRET` (secret, .env); 3 Email provider API key → `EMAIL_API_KEY` (secret, .env + CI); 4 Verify sender domain (pure action, confirm when DNS records are added).
Stage 1 in the script:
```bash
stage "Payments sandbox keys"
open_url "https://dashboard.payments.example/test/apikeys"
step "Sign in, make sure 'Test mode' is on (top right)."
step "Developers → API keys → Reveal secret key → copy."
ask_secret PAYMENTS_SECRET_KEY "Paste the secret key (starts with sk_test_)" '^sk_test_'
write_env PAYMENTS_SECRET_KEY "$PAYMENTS_SECRET_KEY"
set_ci_secret PAYMENTS_SECRET_KEY "$PAYMENTS_SECRET_KEY"
```
Static check: CI workflow references `secrets.PAYMENTS_SECRET_KEY` and `secrets.EMAIL_API_KEY`; both are set; webhook secret is local-only by design.

## Pitfalls

- Asking the user questions the repo already answers.
- Vague instructions ("get your API key") instead of click paths.
- Echoing secrets, or passing them as CLI arguments.
- Non-idempotent `.env` writes that append duplicates on re-run.
- Assuming every loader reads `.env` like the wizard does: `write_env` double-quotes values, and some loaders (docker compose, dotenv-expand) expand `$VAR` inside double quotes. If a secret can contain `$`, check the app reads it back intact.
- Setting CI secrets the pipeline never reads, or misspelling the name.
- Running the wizard yourself, or skipping confirm gates on destructive steps.

## Done when

- [ ] Every value from the confirmed list is captured and written to its destination(s).
- [ ] Irreversible steps gated by `confirm`; secrets hidden end to end.
- [ ] Script passes `bash -n` (and shellcheck if available) and is executable.
- [ ] User told how to run it; committed and linked from README if it should persist.
