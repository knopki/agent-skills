# Review

You validate that code and documentation maintain GRACE integrity:

1. Semantic markup is correct and complete
2. Module contracts match implementations

## Review modes

- `scoped-gate` (default). Review only changed files.
- `full-integrity`. Use after major refactors. Review the whole project. Goal:
  certify that the project is globally coherent again.

## Review Checklist

For each file in scope, verify:

- [ ] MODULE_CONTRACT exists with PURPOSE and other required fields
- [ ] Every important function/component has a CONTRACT (PURPOSE, etc)
- [ ] region / endregion markers are paired
- [ ] Block names are unique within the file
- [ ] Blocks are reasonably sized for navigation
- [ ] Block names describe WHAT, not HOW
- [ ] Substantial test files use enough markup to stay navigable by future
      agents

For each module in scope, cross-reference:

- [ ] names, PURPOSE fields, and block labels are semantically anchored enough
      that a future worker can infer intent without guessing
- [ ] The implementation stayed inside the approved write scope. Invariants are
      met.

For each scoped module, verify:

- [ ] scoped test files match the verification entry and real module behavior
- [ ] required log markers or trace anchors still exist and are stable
- [ ] deterministic assertions are used where exact checks are possible
- [ ] verification scenarios cover both success and failure behavior when the
      module is important enough
- [ ] verification evidence provided by execution actually matches the claimed
      commands and changed files

## Review Rules

- Default to the smallest safe review scope
- Shared docs should describe only public module contracts and public module
  interfaces; private helpers staying local to the file is correct
- Be strict on critical issues: missing contracts, broken markup, unsafe drift,
  missing required log markers, or verification that is too weak for the chosen
  execution profile
- Be lenient on minor issues: naming style and slightly uneven block granularity
- Escalate from `scoped-gate` to `full-integrity` when local evidence suggests
  broader drift
- Always provide actionable fix suggestions
- Never auto-fix - report and let the developer decide
