# GRACE Init Workflow

## 1. Detect languages and frameworks

Inspect the project root and source tree. Produce the set of
languages/frameworks in use.

## 2. Select matching templates

Select matching templates from `assets/` directory.

If a language has no template, note the gap and either fall back to the closest
convention or ask the user how to proceed.

## 3. Ask before copying — checkpoint

Present to the user the proposed template files.

**Ask whether the user wants these sample templates copied into the project's
`docs/`.** Copy only what the user confirms. If matching files already exist in
`docs/`, confirm before overwriting.

## 4. Copy confirmed templates

Copy each confirmed `_semantic_template_reference*` file into the project's
`docs/` directory. These copies are the working per-language markup reference
for the project.

## 5. Survey and propose a markup plan — checkpoint

- Read the selected templates to understand the markup.
- If resuming: detect files that already contain GRACE regions (e.g. `region
MODULE_CONTRACT`, etc) and treat them as done; continue the rest.
- Build an ordered plan of which modules/files to mark up. Suggested order:
  entry points and core business logic first, then outward.
- Decide markup depth per file using the proportional principle (full contract
  vs. partial vs. skip for trivial files).
- **Present the plan to the user and get approval before marking up.**

## 6. Apply markup interactively

For each file/module in the approved plan:

1. Apply module markup first.
2. Apply region-based markup per the matching template (`CLASS_*`, `METHOD_*`,
   `FUNC_*`, `BLOCK_*`, etc) and the relevant annotations.
3. Keep markup proportional — skip trivial helpers and accessors.
4. **When required intent is missing or ambiguous** — e.g. a module's `PURPOSE`,
   `INVARIANTS`, or `SCOPE` cannot be inferred confidently from the code —
   **stop and ask the user.** Do not invent business intent.
5. Prefer contract-first: settle the contract, then align the code.

Continue until the plan is complete or the user pauses. The session is
resumable: re-running "GRACE init" continues from unfinished files.

## Output

- `docs/_semantic_template_reference*` copies (only the confirmed ones)
- A markup plan (presented to the user; carried across the session)
- Source files annotated with GRACE-lite semantic markup (regions + annotations)
