# grace-lite-fix

Debug an issue using GRACE-lite semantic navigation. The agent locates the
relevant module via the knowledge graph, navigates to the mismatching semantic
block, analyses the contract vs actual behaviour, and applies a targeted fix
within block boundaries.

## Scope & Limitations

grace-lite-fix is a **debug-and-fix skill** — it modifies code to resolve bugs,
but only within existing semantic blocks and after confirming the contract is
correct.

The lite variant is designed for projects that only use the knowledge graph and
AGENTS.md — no full GRACE document suite is required.

If the bug is architectural (wrong contract), the agent escalates to the user
instead of silently patching the contract.

## Usage

This is an **agent skill**, not a CLI tool. Trigger it by asking the agent to
debug a bug, error, or unexpected behaviour — the agent will follow the SKILL.md
workflow:

1. Load `docs/knowledge-graph.xml` and identify the relevant module
2. Follow CrossLinks and read the MODULE_CONTRACT
3. Navigate to the mismatching semantic block via module map or log references
4. Analyse the contract vs actual code mismatch
5. Apply a targeted fix within block boundaries
6. Update CHANGE_SUMMARY, CONTRACT (if needed), and CrossLinks

## Acknowledge

This skill is an almost complete copy of
[grace-fix](https://github.com/osovv/grace-marketplace/tree/main/skills/grace/grace-fix)
— the original GRACE fix skill stripped down to the GRACE-lite artifact set
(knowledge graph only, no GRACE CLI, no verification/operations docs). The full
GRACE ecosystem lives at
[osovv/grace-marketplace](https://github.com/osovv/grace-marketplace).
