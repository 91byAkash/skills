# React Native Rules

## Rendering (critical: violations crash or break UI)
- All text inside `<Text>`; a bare string in a `<View>` crashes.
- Avoid `cond && <X/>` when `cond` can be `0` or `""`; rendering `0` outside `<Text>` crashes. Use a ternary or `!!cond`.

## Lists (high)
- Use a virtualised list (FlatList, or a recycler list such as FlashList; FlashList v2 needs the New Architecture and drops size estimates) for anything beyond a screenful; never `ScrollView` + `map` for long data.
- Stable `keyExtractor` from data ids.
- Memoize row components; keep row props primitive and stable; no inline objects/functions created per row.
- Provide `getItemLayout` or estimated item size when rows are fixed or predictable.
- Different row types: declare item types so recycling reuses the right cells.
- Expensive work out of rows: precompute derived fields before passing data.
- Images in lists: a caching image component, sized thumbnails, not full-resolution assets.

## Animation (high)
- Run animations on the UI thread (Reanimated worklets or the native driver); never drive per-frame animation through React state.
- Animate `transform` and `opacity`; avoid layout properties.
- Derived animation values (`useDerivedValue`) instead of recomputing in JS each frame.
- Press feedback with gesture-handler-based pressables or `Pressable` with UI-thread animation.

## Scroll (high)
- Do not store scroll position in React state (re-render every frame). Use shared values or refs; throttle callbacks.

## Navigation (high)
- Use native stack and native tab navigators for platform transitions and memory behaviour.

## State (medium)
- Minimise state; derive the rest. Keep one source of truth (server cache vs local state, not both).
- Use a dispatcher/reducer for complex related updates; functional updates to avoid stale closures in callbacks.
- Provide fallbacks for state that may be undefined while loading.

## React Compiler (medium)
- Destructure functions from props/hooks before use so the compiler can track them.
- Shared animation values are mutable by design; access via `.value` (or `get`/`set`) inside worklets only.

## UI (medium)
- Images: a performant image component with caching, placeholders, and correct `contentFit`.
- Menus and modals: native components (native context menus, native modal presentation) over JS imitations.
- `Pressable` over legacy touchables; adequate hit slop (≥ 44 pt).
- Safe areas: apply insets to scroll content (`contentInset`/`contentContainerStyle`), not by wrapping everything in a padded view.
- Measure views with `onLayout` or layout APIs, not timers.
- Styling: `StyleSheet.create` or a compiled styling solution; avoid creating style objects in render.

## Design system and dependencies (medium/low)
- Compound components for flexible primitives; import from one design-system folder.
- Wrap and re-export third-party UI so swapping libraries touches one place.
- Monorepos: native dependencies installed in the app package; a single version of React/React Native across workspaces.
- Fonts: load via the build config plugin (embedded at build) instead of runtime loading where possible.
- Hoist `Intl` formatters and other expensive objects out of render.

## Measuring
- Profile on a real mid-range Android device in release mode; development builds are much slower.
- Use the performance monitor (JS and UI frame rates) and the React profiler; watch for JS thread stalls during scroll and gestures.
