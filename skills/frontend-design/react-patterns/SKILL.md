---
name: react-patterns
description: "Write and review React and React Native code for performance and clean component APIs, fixing the costliest problems first. Use when writing or refactoring components, hooks or server components, reviewing a React PR, \"slow renders\" or a large bundle, or designing a reusable component API. Not for visual design (use frontend-visual-direction)."
license: MIT
metadata:
  category: "frontend-design"
  version: "3.0.0"
---

# React Patterns

Scope, by impact: async waterfalls, bundle size, server work, client fetching, re-renders, rendering, JS hot paths, effects; plus composition (compound components, variants) and React Native rules. Non-React frameworks are out of scope.

Fix the expensive things first. A single request waterfall costs more than every `useMemo` in the file.

## Inputs

| Parameter | Required | Default | Example |
|---|---|---|---|
| `target` | required | — | `app/dashboard/`, a PR diff, or `components/DataTable.tsx` |
| `mode` | optional | `review` | `write` (new code), `perf` (measure and fix), `api` (design a component API) |
| `platform` | optional | detected | `web` (with or without server components), `native` |
| `framework` | optional | detected | a server-component framework, Vite SPA, Expo |
| `react_version` | optional | from package.json | `19` (enables `use()`, ref-as-prop, actions); `19.2` adds `useEffectEvent`, `<Activity>` |
| `compiler` | optional | detected (React Compiler on/off) | `on`: skip manual memo unless measured |
| `symptom` | optional (perf) | — | "typing in the filter input lags", "JS bundle 1.2 MB" |

## Output

- **review**: findings ordered by impact category (below), each with location, problem, fix (code), and expected effect.
- **write / api**: the code, plus a note on data-loading strategy and component API choices.
- **perf**: before/after measurements (profiler commit times, bundle sizes, request timeline) and the changes that produced them.

## Supporting files

- [REFERENCE.md](REFERENCE.md): rules with bad/good code per category: waterfalls, bundle, server, client fetching, re-renders, rendering, JS hot paths, advanced effects. Read for the category you are working on.
- [COMPOSITION.md](COMPOSITION.md): component API patterns: compound components, explicit variants instead of booleans, children over render props, lifting state into providers, context interfaces, React 19 changes. Read in `api` mode or when props pile up.
- [REACT-NATIVE.md](REACT-NATIVE.md): native rendering rules, list performance, animation on the UI thread, scroll, navigation, images, modals, monorepos. Read when `platform=native`.

## Impact order

| # | Category | Impact | Typical fix |
|---|---|---|---|
| 1 | Async waterfalls | critical | start independent work together; move fetching up; stream with Suspense |
| 2 | Bundle size | critical | direct imports, dynamic import for heavy/rare UI, defer third-party scripts |
| 3 | Server work | high | parallel server fetches, per-request caching, pass minimal props to client |
| 4 | Client fetching | medium-high | a dedup/cache library; no fetch-in-effect chains |
| 5 | Re-renders | medium | derive in render, colocate state, split contexts, functional updates, transitions |
| 6 | Rendering | medium | virtualise, `content-visibility`, hoist static JSX, avoid hydration flicker |
| 7 | JS hot paths | low-medium | Map/Set lookups, single pass, hoist regex/Intl |
| 8 | Advanced | low | effect events, refs for handlers, init-once |

## Steps

1. **Read the setup**: React version, framework, server components or not, data library, compiler, bundler, existing conventions. `react_version` ≥ 19: use the React 19 rules in COMPOSITION.md (ref as a prop, `use()`, actions) and do not add `forwardRef`. `platform=native`: apply REACT-NATIVE.md in place of REFERENCE.md sections 2, 3 and 6. `compiler=on`: drop manual `useMemo`/`useCallback`/`memo` findings unless a profile shows the compiler missed a case.
2. **Branch by mode.**

**review / write**
3. Walk the impact order. For each category, check the target against REFERENCE.md rules. Stop to fix any critical item before polishing lower ones.
4. Check effects specifically: every `useEffect` should synchronise with an external system. Effect + `setState` from props/state → derive during render. Effect reacting to a user action → move into the event handler.
5. Check component APIs: more than ~3 boolean props, or props that only make sense together → see COMPOSITION.md.
6. Check correctness basics: stable keys from data (not index for dynamic lists), cleanup of subscriptions/timers, stale-response handling (abort or ignore), accessible custom controls.

**perf**
3. Measure first, starting from the `symptom`: input lag or slow updates → React Profiler (commit durations, why each component rendered) and the performance panel; slow first load → network waterfall and a bundle analyser. With no symptom, take all four. Write the baseline numbers down.
4. Fix the top cost only, re-measure, repeat. Do not add memoization without a measured re-render problem (and not at all when the compiler handles it).

**api**
3. List the variations callers need. Choose: explicit variant components or a `variant` prop for mutually exclusive styles; compound components with a shared provider for flexible layouts; `children` for content slots.
4. Write the usage examples first, then the implementation.

## Checkpoints

- perf: baseline numbers recorded before any change.
- review: critical findings (waterfalls, bundle) reported before lower-impact ones.
- api: usage examples agreed before implementation of a shared component.

## Worked example

Review of `app/dashboard/page.tsx` (server component) and `Filters.tsx`:

1. **Critical, waterfall**:
   ```tsx
   const user = await getUser(); const projects = await getProjects(); const stats = await getStats();
   ```
   The three calls are independent. Fix: `const [user, projects, stats] = await Promise.all([getUser(), getProjects(), getStats()]);` and wrap the slow `stats` panel in its own Suspense boundary so the page streams. Expected: ~3 round trips → 1.
2. **Critical, bundle**: `import { format } from "date-fns"` fine; `import _ from "lodash"` pulls the whole library into a client component. Fix: `import debounce from "lodash/debounce"` or a native implementation.
3. **Medium, re-render**: `Filters` stores `filteredRows` in state and syncs it in an effect on `[rows, query]`. Fix: compute `const filteredRows = useMemo(() => filter(rows, query), [rows, query])` (or plain computation if cheap) and wrap the query update in `startTransition` so typing stays responsive.
4. **Medium, API**: `<Card compact bordered withHeader withFooter danger>` → compound `<Card variant="danger"><Card.Header/>…</Card>`.

## Pitfalls

- Memoizing everything "just in case" while a request waterfall dominates load time.
- `useEffect` for derived data or for responding to clicks.
- Defining components inside other components (remounts every render, loses state).
- Context providers whose value object is recreated every render, re-rendering all consumers.
- Barrel-file imports of large libraries in client code.
- Passing whole database objects from server to client components (large serialized payloads, leaked fields).
- Index keys on lists that reorder or filter.
- Module-level mutable state on the server shared across requests.

## Done when

- [ ] No independent awaits run sequentially; slow sections stream behind their own boundaries.
- [ ] Heavy or rarely used client code is dynamically imported; no full-library barrel imports.
- [ ] Effects only synchronise with external systems; derived state is computed in render.
- [ ] Component APIs avoid boolean-prop explosions; mutually exclusive styles are explicit variants.
- [ ] (perf) Before/after measurements show the improvement.
- [ ] Keys, cleanups, and stale-response handling are correct.
