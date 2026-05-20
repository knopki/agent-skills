---
name: grace-lite
description: >
  Mandatory load when you encounter START_MODULE_CONTRACT, START_CONTRACT, or START_BLOCK markers in any source file, when the user mentions GRACE, when working with source files, updating docs/knowledge-graph.xml, or adding modules or public interfaces.
license: MIT
compatibility: Requires Python 3.10+
metadata:
  author: Sergei Korolev <knopki@duck.com>
  url: https://github.com/knopki/agent-skills
---

# GRACE: Graph-RAG Anchored Code Engineering

GRACE-lite provides structured comment markup for source files and a
navigational XML knowledge graph (`docs/knowledge-graph.xml`) that maps module
boundaries, public interfaces, dependencies, and execution flows.

## Core Principles

- **Contract-first**: create/update MODULE_CONTRACT before code; never jump to
  code when requirements, architecture, or verification are unclear. Contract
  locks in intent so every subsequent agent works from the same understanding.
- **Markup is navigation**: `START_*/END_*` markers are semantic coordinates for
  1–2 hop navigation, not docs. Unique, paired.
- **Graph is always current**: update `docs/knowledge-graph.xml` in same change
  for structural, API, or dependency changes. Graph compresses structure for
  fragment-based reading.
- **Governed autonomy**: contracts, plans, and graph define WHAT; agents choose
  HOW within those boundaries.
- **Proportional markup**: core logic gets full contracts; trivial helpers get
  none. Unnecessary anchors are noise.

Paired anchors set expectations before implementation. Contract-first: decide
intent, then generate.

Markup is self-similar: MODULE_CONTRACT → function contract → block anchors.
Each level restricts ambiguity below. Covers code markup only.

## Navigation Order (mandatory)

Navigate: 1) `docs/knowledge-graph.xml` (shared truth) → 2) file-local markers
(`MODULE_CONTRACT`, `MODULE_MAP`, `CHANGE_SUMMARY`, function contracts, semantic
blocks) → 3) full file reads only after narrowing to a specific module, file, or
block. Anchors: `START_*/END_*`, `LINKS:`, `M-` prefix, `CrossLink`.

Same markup serves generation (top-down template) and navigation (bottom-up
index for fragment-based reading).

## Semantic Markup Reference

### Module Level (required)

```python
# FILE: path/to/file.ext
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: [What this module does - one sentence]
#   SCOPE: [What operations are included]
#   DEPENDS: [List of module dependencies; M-<NAME>, etc]
#   LINKS: [Knowledge graph references]
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   exportedSymbol - one-line description
# END_MODULE_MAP
```

### Function or Component Level

Required for: core business logic, exported functions, public methods,
graph-relevant callables. Optional for: private helpers, trivial accessors.
Place above function signature. Do not add contracts to every function blindly:
over-markup creates noise that degrades, not improves, agent navigation.

```python
# START_CONTRACT: functionName
#   PURPOSE: [What it does]
#   INPUTS: { paramName: Type - description } | { None }
#   OUTPUTS: { ReturnType - description } | { None - no return value }
#   SIDE_EFFECTS: None | description of external state changes
#   LINKS: [Related modules/functions; M-*, fn-*, type-*, class-*, etc]
# END_CONTRACT: functionName
```

### Code Block Level (required)

```python
# START_BLOCK_VALIDATE_INPUT
# ... code ...
# END_BLOCK_VALIDATE_INPUT
```

Block names describe **logical purpose** (`VALIDATE_INPUT`, `COLLECT_RESULTS`),
not transient implementation details.

### Change Tracking (required)

```python
# START_CHANGE_SUMMARY
#   LAST_CHANGE: [v1.2.0 - What changed and why]
#   PREVIOUS_CHANGE: [v1.1.1 - What changed and why]
# END_CHANGE_SUMMARY
```

### Anti-patterns

- Do NOT mix JSON or Markdown structure with GRACE anchors in the same file.
- Do NOT add contracts to trivial one-liners or private helpers.
- Do NOT write empty or boilerplate contracts (e.g. `SIDE_EFFECTS: none` when
  the function obviously mutates state). A bad contract is noise.
- Do NOT use line numbers for patching; use block/contract anchors.

## Knowledge Graph

File: `docs/knowledge-graph.xml`.
Root: `<KnowledgeGraph>`.
Child: `<Project NAME="..." VERSION="...">`.

### Project Element

`<Project>` required children: `<keywords>`, `<annotation>`. Optional: `M-*`,
`DF-*`, `CrossLink`.

### M-{NAME} Module Element

Each governed module uses its unique `M-{DOMAIN}` ID as the XML tag:

```xml
<M-DOMAIN NAME="Human name" TYPE="TYPE" STATUS="STATUS">
  <purpose>One-line purpose</purpose>
  <path>src/relative/path.py</path>
  <depends>M-OTHER, M-THIRD or none</depends>
  <annotations>
    <fn-name PURPOSE="Function purpose" />
    <class-Name PURPOSE="Class purpose" />
  </annotations>
</M-DOMAIN>
```

TYPE: `ENTRY_POINT` | `CORE_LOGIC` | `DATA_LAYER` | `UI_COMPONENT` | `UTILITY` |
`INTEGRATION`.

STATUS: `planned` → `partial` → `implemented`.

Required: `<purpose>`, `<path>`, `<depends>`. Optional: `<annotations>`
(prefix: `fn-`, `class-`, `type-`, `export-`, `const-`).

Knowledge graph holds only the public boundary (exports, types, entry points).
Internal helpers, private state, and implementation details stay in
file-local markup. This keeps the graph compact and prevents semantic noise
in shared context.

### DF-{NAME} Data Flow Element

Element name is unique.

```xml
<DF-PUBLISH NAME="Publish dweet">M-API -> M-CONTENT -> M-STORAGE</DF-PUBLISH>
<DF-STREAM NAME="Parallel paths">M-API -> M-STREAMING; M-DWEETS -> M-STREAMING</DF-STREAM>
```

Separators: `->` sequential, `;` parallel/independent, `/` alternatives.
Tag name = `DF-<NAME>`, `NAME` attribute required.

### CrossLink: Cross-module Link Element

```xml
<CrossLink from="M-API" to="M-CONTENT" relation="delegates parsing" />
```

All `from`/`to` values must reference existing M-IDs. `relation` is free-form prose.

### When to update the graph

Update `docs/knowledge-graph.xml` in the same change when:

- Module created/removed: add/remove M-entry (`STATUS`: `planned` → `partial` →
  `implemented`).
- Public API changes (callables, classes, exports, types): update
  `<annotations>`.
- Dependencies change: update `<depends>` and `<CrossLink>`.
- Private-only changes: no graph update needed.

## Markup Rollout

- **New files**: include MODULE_CONTRACT + MODULE_MAP + CHANGE_SUMMARY on
  creation.
- **Existing files**: bring to standard when substantively edited; internal
  markup progressively.

## Logging & Verification

Structured logs are the primary observability mechanism: each log entry at a
block boundary declares what the code assumes is happening at that point,
making runtime behavior traceable back to the contract and enabling
post-hoc verification.

Governed functions emit `logging.debug("[Module][function][BLOCK] msg", extra={...})`
at block boundaries. Prefer structured fields; redact secrets.
Missing anchors on critical branches = verification defect.

```python
# Good: block boundary log declares intent and context
logger.debug("[Storage][save_dweet][VALIDATE_INPUT] input=%s", dweet_key)
# ...
logger.debug("[Storage][save_dweet][WRITE_DB] rows_affected=%d", n)
```

Tests: deterministic assertions first; trace/log assertions when trajectory
matters. Test files may carry MODULE_CONTRACT, MODULE_MAP, semantic blocks, and
CHANGE_SUMMARY when substantial. Module-local tests stay close to their module.
Update tests when log markers change intentionally.

## Size Limits

Source file: 500 lines soft (evaluate splitting into focused modules), 1000 hard
(must refactor before change is complete). Function + its contract: 60 lines
(decompose into smaller helpers). Semantic block: 50 lines (warning: consider
splitting or extracting).

## Validation

Always run validation and fix problems before submitting.

```bash
python3 scripts/grace_check.py              # All checks (XML + source)
python3 scripts/grace_check.py --init       # Create graph from template
# Flags: --check-xml, --check-source, --root DIR, --json
```

Exit: 0=ok, 1=errors, 2=usage.

## References

- [Bootstrap guide](references/bootstrap.md) — initializing GRACE-lite on a new
  project
- [Graph template](assets/knowledge-graph.xml.template) — used by `--init`
