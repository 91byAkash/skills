# Packages

Each folder here is a **deep module**: a lot of behaviour behind a small interface.

```
<name>/
  index.ts      entry point (public): import this from outside
  client.ts     another entry point, if the package has distinct audiences
  lib/          implementation (private)
  tests/        tests and fixtures (private); import only entry points
```

Rules (checked by `npm run lint:boundaries`, part of `check`):

1. Outside code imports only a package's root files.
2. A package uses its own `lib/` freely and other packages only via their root files.
3. Tests go through entry points, the same way callers do.
4. No dependency cycles.

Guidance:

- Prefer several small entry points over one barrel `index.ts` that re-exports everything.
- Before adding a new package, apply the deletion test: would inlining it into callers spread complexity? If not, it does not need to be a package.
- Packages are flat: no package inside another. Internals may nest as deep as needed.
- Copy `example/` to start a new package; delete it once real packages exist.
