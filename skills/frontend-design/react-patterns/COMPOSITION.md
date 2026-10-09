# Component Composition Patterns

## Boolean props are a smell

```tsx
// hard to use, hard to maintain: 2^5 combinations, many invalid
<Composer isThread isEditing showAttachments hideSend compact />
```
Each boolean doubles the states to test. Replace with one of the patterns below.

## Explicit variants

When options are mutually exclusive, make them one prop or separate components:
```tsx
<Button variant="primary" | "secondary" | "danger" size="sm" | "md" />
// or, when variants differ in structure, not just style:
<ThreadComposer /> <EditMessageComposer /> <ForwardComposer />
```
Separate components sharing internal pieces are often clearer than one component with modes.

## Compound components

Parts share state through a provider; callers arrange the layout:
```tsx
<Composer.Root onSubmit={send}>
  <Composer.Input placeholder="Reply…" />
  <Composer.Toolbar>
    <Composer.AttachButton />
    <Composer.Submit>Send</Composer.Submit>
  </Composer.Toolbar>
</Composer.Root>
```
```tsx
const Ctx = createContext<ComposerContext | null>(null);
function useComposer() { const c = use(Ctx); if (!c) throw new Error("Composer parts must be inside Composer.Root"); return c; }
function Root({ onSubmit, children }: Props) {
  const [text, setText] = useState("");
  const value = useMemo(() => ({ text, setText, submit: () => onSubmit(text) }), [text, onSubmit]);
  return <Ctx value={value}><form onSubmit={e => { e.preventDefault(); value.submit(); }}>{children}</form></Ctx>;
}
```

## Children over render props

Prefer `children` and slot components for content. Use a render prop only when the parent must pass data to what the caller renders (e.g. a virtual list's row renderer).

## Context interface, not implementation

Define what consumers need (`{ text, setText, submit, isSubmitting }`) and keep how it is stored (local state, reducer, external store, server sync) private to the provider. Swapping the implementation should not touch consumers.

## Lift state to the provider

When siblings outside the component need the state (a preview pane showing the composer's text), lift the state into a provider above both instead of syncing with effects or refs.

## Split by update frequency

Fast-changing values (cursor position, input text) in one context; slow ones (user, permissions, theme) in another, so most consumers do not re-render on each keystroke.

## React 19 changes

- `ref` is a regular prop on function components; `forwardRef` is no longer needed.
- `use(Context)` can replace `useContext(Context)` and works conditionally; `use(promise)` reads a promise inside Suspense.
- `<Context value={…}>` can replace `<Context.Provider value={…}>`.
- Actions: `<form action={fn}>`, `useActionState` (replaces the old `useFormState`), `useFormStatus`, and `useOptimistic` for form submission state and optimistic UI.
- Ref callbacks may return a cleanup function; `<title>`, `<meta>` and `<link>` rendered anywhere are hoisted to `<head>`.
- React 19.2: `useEffectEvent` and `<Activity>` are stable.
- React Compiler 1.0 (stable since Oct 2025) memoizes automatically; with it on, do not add `memo`/`useMemo`/`useCallback` by default.

## Checklist for a shared component API

- [ ] Fewer than ~3 booleans; mutually exclusive options are a single prop or separate components.
- [ ] Layout flexibility via composition (children/compound parts), not configuration props.
- [ ] Sensible defaults; required props are truly required.
- [ ] Accessible by default (labels, roles, keyboard) without caller effort.
- [ ] Usage examples written before implementation.
