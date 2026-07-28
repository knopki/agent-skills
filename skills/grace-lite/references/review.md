# Review

You validate that code and documentation maintain GRACE integrity:

1. Semantic markup is correct and complete
2. Module contracts match implementations

## Review modes

- `scoped-gate` (default). Review only changed files.
- `full-integrity`. Use after major refactors. Review the whole project. Goal:
  certify that the project is globally coherent again.

## What to check

Use the **Verification Checklist** in `SKILL.md` for every file and module in
scope. It covers file-level markup, cross-file semantic anchoring, and
verification artifacts (test files, log markers, deterministic assertions).

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
