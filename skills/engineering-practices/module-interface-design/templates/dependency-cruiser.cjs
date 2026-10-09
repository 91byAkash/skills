// @ts-check
/*
 * Deep-module boundary check for dependency-cruiser.
 *
 * Model: every directory directly below MODULES_DIR is one module. Files sitting
 * at a module's top level form its public face; anything one folder deeper
 * (lib/, tests/, helpers/ ...) is private to that module.
 *
 * Set MODULES_DIR and nothing else. Run the check on the whole source tree
 * (`depcruise src`), otherwise imports made by code outside MODULES_DIR are never
 * examined. If the run reports "0 modules" for a TypeScript project, the installed
 * `typescript` is one dependency-cruiser cannot load: check `npx depcruise --info`.
 */
const { existsSync } = require("node:fs");

const MODULES_DIR = "src/packages";

// Regex helpers (derived; no need to touch).
const quote = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const under = (rest) => `^${quote(MODULES_DIR)}/${rest}`;
const PRIVATE = under("[^/]+/[^/]+/"); // a file nested inside some module's subfolder

/** Every rule here is a hard failure; this keeps each entry to its intent. */
const deny = (name, why, from, to) => ({ name, comment: why, severity: "error", from, to });

const forbidden = [
  deny("outside-reaches-into-module",
    "Code that lives outside MODULES_DIR may only import a module's top-level files.",
    { pathNot: under("") },
    { path: PRIVATE }),

  // $1 is the importing module's own name, captured by the `from` pattern.
  deny("module-reaches-into-sibling",
    "Inside its own folder a module is free; another module is reached only via its top-level files.",
    { path: under("([^/]+)/") },
    { path: PRIVATE, pathNot: under("$1/") }),

  deny("test-reaches-into-internals",
    "A module's tests use top-level files (of any module) plus their own tests/ helpers, never lib code.",
    { path: under("([^/]+)/tests/") },
    { path: PRIVATE, pathNot: under("$1/tests/") }),

  deny("circular-import", "Import cycles are not allowed anywhere.", {}, { circular: true }),

  // Which modules may depend on which (layering) is a separate decision; add rules like:
  // deny("billing-must-not-use-ui", "...", { path: under("billing/") }, { path: under("ui/") }),
];

/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden,
  options: {
    doNotFollow: { path: "node_modules" },
    tsPreCompilationDeps: true,
    enhancedResolveOptions: {
      exportsFields: ["exports"],
      conditionNames: ["import", "require", "node", "default"],
    },
    ...(existsSync("tsconfig.json") ? { tsConfig: { fileName: "tsconfig.json" } } : {}),
  },
};
