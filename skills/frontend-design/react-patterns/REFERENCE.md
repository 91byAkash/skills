# React Performance Rules

Ordered by impact. Each rule: what to look for, then the fix.

## Contents
1. Async waterfalls
2. Bundle size
3. Server work
4. Client data fetching
5. Re-renders
6. Rendering
7. JavaScript hot paths
8. Advanced effects and refs

## 1. Async waterfalls (critical)

**Parallelise independent work.**
```ts
// slow: three round trips
const a = await getA(); const b = await getB(); const c = await getC();
// fast
const [a, b, c] = await Promise.all([getA(), getB(), getC()]);
```

**Start early, await late.** Kick off a promise as soon as its inputs exist; await only where the value is needed.
```ts
const settingsP = getSettings(userId);        // start now
if (!(await canView(userId, docId))) return notFound();
const settings = await settingsP;            // already in flight
```

**Cheap checks before expensive awaits.** Validate input, check flags or auth from the session before hitting the database or network.

**Partial dependencies.** When B needs A but C does not, start C with A: `const aP = getA(); const cP = getC(); const b = await getB(await aP);`.

**API routes and server actions**: same rules; a handler that awaits five things in sequence is a waterfall too.

**Stream with Suspense.** Put slow, non-critical sections behind their own `<Suspense fallback={…}>` so the shell renders immediately. One boundary per independently slow region, not one around the whole page.

**Do not fetch in child effects after parent renders** (fetch → render → child fetch → render). Fetch at the route/loader/server-component level and pass data down, or preload in parallel.

## 2. Bundle size (critical)

- **Import directly, not from barrels** for large libraries and internal index files: `import Button from "@/ui/button"` rather than `import { Button } from "@/ui"` when the barrel re-exports heavy modules. Some frameworks/bundlers can optimise named imports from known packages; verify with the analyser.
- **Dynamic import** heavy or rarely shown UI (editors, charts, maps, admin panels, modals): `const Chart = lazy(() => import("./Chart"))` or the framework's dynamic helper, with a sized fallback.
- **Conditional loading**: load a module only when the feature is enabled or the user interacts (`onMouseEnter` / `onFocus` preload for likely next actions).
- **Defer third-party scripts** (analytics, chat, A/B tools) until after load or interaction; never block hydration on them.
- **Keep paths analysable**: dynamic imports with template strings over whole folders pull in everything; use explicit maps of `() => import("./x")`.
- **Server-only code stays on the server**: mark modules server-only so secrets and heavy deps cannot slip into client bundles.
- Measure with a bundle analyser; set a budget per route (e.g. ≤ 170 KB JS gzipped for the initial route on mobile).

## 3. Server work (high)

- **Parallel fetching** in server components: start sibling data requests together; nested components that each await create hidden waterfalls; lift and pass promises or data.
- **Per-request dedup**: wrap data functions with `React.cache` (server components only) so several components asking for the same user hit the DB once.
- **Cross-request cache**: an LRU or the framework's data cache for expensive, shareable reads; key by inputs; set TTLs. Next.js 16+: opt-in Cache Components with the `"use cache"` directive and `cacheLife`; earlier versions cache `fetch` differently by major (15 stopped caching `fetch` by default), so check the installed version before relying on either.
- **Minimal serialization**: pass only the fields the client component needs, not whole records (smaller payload, no leaked fields). Dedupe repeated objects passed to many client components.
- **Hoist static I/O**: read config files, templates, or fonts once at module scope (immutable data only), not per request.
- **No shared mutable module state** on the server: it leaks between users.
- **Authenticate inside server actions** every time; they are public endpoints.
- **Non-blocking side effects** (logging, analytics, cache warming): run after the response with the framework's after-response hook (e.g. Next.js `after()`) instead of awaiting them.

## 4. Client data fetching (medium-high)

- Use a data library with caching and request dedup (query/SWR-style) or framework loaders; avoid hand-written fetch-in-effect.
- If you must fetch in an effect: abort on cleanup and ignore stale responses.
```ts
useEffect(() => {
  const ac = new AbortController();
  fetch(`/api/items?q=${q}`, { signal: ac.signal }).then(r => r.json()).then(setItems).catch(() => {});
  return () => ac.abort();
}, [q]);
```
- Global listeners (resize, scroll, online): one shared subscription (e.g. `useSyncExternalStore`) rather than one listener per component; passive listeners for scroll/touch.
- `localStorage`: wrap with a versioned schema and validation; read once; handle missing/corrupt data; never store tokens there.

## 5. Re-renders (medium)

- **Derive, do not sync**: compute from props/state during render.
```tsx
// bad
const [fullName, setFullName] = useState(""); useEffect(() => setFullName(`${first} ${last}`), [first, last]);
// good
const fullName = `${first} ${last}`;
```
- **Events, not effects**: logic caused by a click goes in the click handler.
- **Colocate state** in the lowest component that needs it; lift only when siblings share it.
- **Split contexts** by update frequency (theme vs live cursor position); memoize provider values.
- **Functional updates** when the next state depends on the previous: `setCount(c => c + 1)`; keeps callbacks stable and avoids stale closures.
- **Lazy initial state** for expensive initialisers: `useState(() => parse(big))`.
- **Primitive dependencies**: depend on `user.id`, not `user`, when only the id matters.
- **Defer reads** of frequently changing values until needed (read a ref or store inside the handler instead of subscribing at render).
- **Transitions** for non-urgent updates (`startTransition(() => setFilter(v))`) and `useDeferredValue` for expensive derived views of fast-changing input.
- **Refs for transient values** that should not re-render (latest scroll position, timers).
- **Never define components inside components**; hoist them.
- **Memo only when measured** (and usually not at all with the compiler): `memo` on expensive children receiving stable props; `useMemo` for expensive computations, not for simple expressions; give memoized components stable default props (`const EMPTY: Item[] = []` outside the component rather than `items = []`).
- **Split combined hooks** that return many values when consumers need only one.

## 6. Rendering (medium)

- Long lists: virtualise (windowing) beyond a few hundred rows; stable keys from data.
- Off-screen sections: `content-visibility: auto` with `contain-intrinsic-size` to skip their rendering work.
- Hoist static JSX (icons, constant elements) outside the component.
- Conditional rendering: prefer `cond ? <X/> : null` over `cond && <X/>` when `cond` can be `0` or `""`.
- Hydration: avoid server/client mismatch flicker for theme or locale by setting attributes in an inline head script; use `suppressHydrationWarning` only on the specific element with an intentional mismatch (e.g. timestamps).
- Resource hints: preload critical fonts/images, preconnect to required origins; `fetchpriority="high"` on the LCP image.
- Scripts: `defer`/`async` or the framework's script component with a loading strategy.
- `useTransition` to show pending UI for slow navigations/updates instead of freezing.
- SVG: reduce path precision; animate a wrapper element rather than many SVG nodes.
- Hidden-but-kept-alive UI (tabs, back navigation): `<Activity mode="hidden">` (React 19.2+) keeps state and DOM while deprioritising updates, instead of unmounting and refetching.

## 7. JavaScript hot paths (low-medium)

Only where profiling shows a hot loop:
- `Map`/`Set` for repeated lookups instead of `array.find`/`includes` in loops; build an index once.
- One pass instead of chained `filter().map().reduce()` on large arrays; `flatMap` to filter+map.
- Early exits; check `length` before expensive comparisons.
- Hoist `RegExp` and `Intl.*Format` construction out of loops and render.
- Cache repeated property access and pure function results by input.
- `toSorted()`/`toReversed()` to avoid mutating props or state.
- Batch DOM reads and writes (read all, then write all) to avoid layout thrash.
- `requestIdleCallback` for low-priority work (prefetching, analytics flush).

## 8. Advanced effects and refs (low)

- **Effect events**: when an effect needs the latest value of something without re-running when it changes, use `useEffectEvent` (stable since React 19.2; keep it out of dependency arrays and call it only from effects) or, on older React, a "latest ref" pattern:
```ts
// React 19.2+
const onTickEvent = useEffectEvent(() => onTick());
useEffect(() => { const id = setInterval(onTickEvent, 1000); return () => clearInterval(id); }, []);
// older React
const onTickRef = useRef(onTick); useLayoutEffect(() => { onTickRef.current = onTick; });
useEffect(() => { const id = setInterval(() => onTickRef.current(), 1000); return () => clearInterval(id); }, []);
```
- **Stable handler refs** for subscriptions that should not resubscribe on every render.
- **Init once** for app-wide setup (SDK init) at module scope or guarded by a ref, not in an effect that runs twice in development strict mode.
