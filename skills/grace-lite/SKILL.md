---
name: grace-lite
description: "GRACE semantic code markup. Use when the user asks about GRACE, asks to set up project, review. Triggers: GRACE init, GRACE review, or when code already contains #region MODULE_CONTRACT markers."
license: MIT
metadata:
  author: Sergei Korolev <knopki@duck.com>
  url: https://github.com/knopki/agent-skills
---

# Graph-RAG Anchored Code Engineering, lite variant

**GRACE** gives a project **semantic code markup** — region-based contracts and
anchors that make code machine-navigable, documentation inside the code.

Also, GRACE methodology offers Log Driven Development as observable contracts.

## When to Use

- The user asks to **initialize** a project with GRACE markup (activation
  trigger: **"GRACE init"**) - follow the `references/init.md`.
- The user asks to **continue / resume adding GRACE markup** to a project that
  was already started - follow the `references/init.md`.
- The user asks to **review** - follow the `references/review.md`.
- You are working with code with word PURPOSE in comments.

## Markup Reference

### Principles

- Mark up all **public and non-trivial** code.
- Expose public API explicitly via language features: `__all__` in Python,
  `export` in JS/TS, etc.
- Do not mark up trivial code: private one-liners, getters/setters, obvious
  operations.
- Markup must be **proportional** — don't annotate every tiny detail.
- Never include empty contract fields. If there's nothing meaningful to say,
  omit the field.
- Python exception: if an entity is annotated by markup, it must always be
  wrapped in a region (unlike C#, where short top-level entities may use `///
<purpose>` without `#region`).
- For exact comment syntax, refer to the template in
  `assets/_semantic_template_reference.<ext>`.

### Workflow

1. **MODULE_CONTRACT first** — always write the module contract before any code.
   It sets the boundary and purpose of the file.
2. **Public contracts next** — define contracts for all public classes,
   functions, and methods. Create stubs.
3. **Implement** — write code inside the contracted regions.

### Region Types

#### MODULE_CONTRACT

File-level contract. Exactly one per file, placed at the very top before all
code.

Defines **what** the module is for and **how** it relates to the rest of the
system.

**Fields:**

- `PURPOSE` — **required**. The goal of the module: what business/operational
  need it fulfills.
- `SCOPE` — recommended. Functional areas covered by the module and what is
  explicitly excluded (`NOT:`).
- `INVARIANTS` — recommended. Conditions or states that always hold.
- `USECASES` — optional. Scenarios in `[Entity]: [Actor] => [Action] => [Goal]`
  format.
- `DEPENDENCIES` — optional. Non-trivial dependencies: `USES API:`, `READS:`,
  `WRITES:`.
- `RATIONALE` — optional. Q/A format: why it was implemented this way.
- `KEYWORDS` — optional. Comma-separated keywords for grep search.

#### CLASS

Wraps a class definition. Groups related state and behavior into a single named
unit.

**Required field:** `PURPOSE` — what the class enables the user/agent to do.

**Optional fields:** `REQUIRES`, `ENSURES`, `RATIONALE`, `SCOPE`, `INVARIANTS`.

#### COMPONENT

Wraps a React component (JSX/TSX). A UI unit that renders markup and manages its
own state or effects.

Same field semantics as `CLASS`.

#### FUNC

Wraps a non-trivial public function outside a class. A standalone callable unit
with inputs and outputs.

**Required field:** `PURPOSE`.

**Optional fields:** `REQUIRES` (preconditions), `ENSURES` (postconditions),
`RATIONALE`, `SCOPE`, `INVARIANTS`.

#### METHOD

Wraps a non-trivial public method inside a class. A callable unit bound to class
state.

Same field semantics as `FUNC`.

#### BLOCK

Wraps a non-trivial logical block inside a function or method — a loop,
pipeline, or group of related operations. A descriptive one-line summary may
follow the block name.

No fields. Block has only a name and an optional summary.

#### Domain-Specific Types

These types cover common patterns in specific languages. They are **not a closed
set** — add your own types when the domain demands it.

- `LIBRARY` — function group / library (Bash)
- `SECTION` / `SUBSECTION` — document sections (Markdown)
- `VARIABLE`, `RESOURCE`, `LOCALS`, `OUTPUT` — (Terraform)
- `PLAY`, `VARS`, `TASK`, `HANDLER` — (Ansible)

All domain-specific types require a `PURPOSE` field.

### A Note on PURPOSE

`PURPOSE` is the most important field. Do not confuse it with a description — it
answers **why**, not **what**. A description says "this module handles user
authentication"; a purpose says "this module ensures only verified users access
protected resources." If you strip away the purpose, the code loses its reason
to exist.

### Comment Syntax

Exact syntax is in the templates at `assets/_semantic_template_reference.<ext>`.
Summary:

- **Python, Bash, Terraform, Ansible YAML**: `# region TYPE_name`,
  `# endregion TYPE_name`
- **JS, TS, JSX, TSX**: `// #region TYPE_name` / `// #endregion TYPE_name`;
  `MODULE_CONTRACT` — in a JSDoc block: `/** #region moduleContract ... **/`,
  other fields are JSDoc tags like `@purpose`.
- **C#**: `#region TYPE_name` / `#endregion TYPE_name`; `MODULE_CONTRACT` — via
  `/// <contract>...</contract>`; short top-level entities may use
  `/// <purpose>` without `#region`, other fields are XML-tags.
- **Markdown**: `<!-- #region TYPE_name -->` / `<!-- #endregion TYPE_name -->`

### Region Naming

- Type prefix is always UPPERCASE: `CLASS_`, `FUNC_`, `BLOCK_`, `METHOD_`,
  `SECTION_`, etc.
- After the prefix, use the name in the language's native style:
  - Python: `snake_case` (`FUNC_example_function`, `METHOD_calculate_total`)
  - JS/TS/JSX/TSX: `camelCase` (`FUNC_exampleFunction`, `METHOD_calculateTotal`)
  - C#: `PascalCase` (`CLASS_ExampleController`, `METHOD_ExampleMethodAsync`)
  - Bash, Terraform, Ansible: `snake_case`
- For `CLASS`, `METHOD`, `FUNC` — use the literal class/method/function name.
- For `BLOCK` — any descriptive name (`BLOCK_calculate_regression`,
  `BLOCK_handlers`).

### Log-Driven Development

Use debug-level logging with structured data throughout the code. Every log
message should be a short, obvious statement of intent, paired with key-value
data:

```python
logger.debug("Pre calculation", extra={"event": "start", "param1":
param1})
logger.debug("Business result", extra={"result": result})
```

```javascript
console.debug("Pre calculation", { event: "start", param1 });
console.debug("Business result", { result });
```

These logs serve as **observable contracts** — they make internal behavior
testable and debuggable without changing production logic. Structured data
enables filtering, assertion, and tracing. This is especially critical in async
applications where stack traces are insufficient.
