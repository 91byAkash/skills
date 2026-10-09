# Hook configurations

## Node: hook manager + staged-file runner

Install (use the detected package manager): `npm i -D husky lint-staged prettier`, then `npx husky init` (adds `"prepare": "husky"` so hooks install on every `npm install`).

`.husky/pre-commit` (no shebang needed on recent versions):
```
npx lint-staged
npm run typecheck
```
`.husky/pre-push` (optional, for slower checks):
```
npm test
```
`.lintstagedrc`:
```json
{
  "*.{js,jsx,ts,tsx,mjs,cjs}": ["eslint --fix", "prettier --write"],
  "*.{json,md,css,scss,yml,yaml,html}": "prettier --write"
}
```
Simplest catch-all: `{ "*": "prettier --ignore-unknown --write" }` (skips files Prettier cannot parse).

## Python / polyglot: the pre-commit framework

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff check
        entry: ruff check --fix
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: ruff format
        language: system
        types: [python]
      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        pass_filenames: false
```
Install: `pip install pre-commit && pre-commit install` (add to the setup docs). Run on all files once: `pre-commit run --all-files`.

## Plain hooks (no manager)

`scripts/install-hooks.sh` writes `.githooks/pre-commit` and runs `git config core.hooksPath .githooks`. Add that config command to the project's setup script so new clones get the hooks.

## Formatter defaults (create only if no config exists)

`.prettierrc`:
```json
{ "printWidth": 100, "singleQuote": false, "trailingComma": "all", "semi": true, "tabWidth": 2, "useTabs": false, "arrowParens": "always" }
```
`pyproject.toml`:
```toml
[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

## Agent command guard registration (generic)

Most agent tools with pre-execution hooks accept a command to run before each shell call, pass the call as JSON on stdin, and treat exit code 2 as "block, show stderr to the agent". Register `scripts/guard-git-command.sh` there with a matcher for shell/terminal tool calls, at project scope (inside the repo's agent settings folder) or user scope (home directory settings). Merge into existing hook arrays; never replace the whole settings file.
