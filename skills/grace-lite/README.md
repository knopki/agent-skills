# GRACE-lite

A lightweight implementation of GRACE (Graph-RAG Anchored Code Engineering)
covering three code-level concerns:

- **Semantic markup** — MODULE_CONTRACT, MODULE_MAP, function contracts,
  semantic block anchors, CHANGE_SUMMARY
- **Knowledge graph** — `docs/knowledge-graph.xml` as navigational index of
  modules, dependencies, and public interfaces
- **Structured logging** — `[Module][function][BLOCK]` format for observability
  and trajectory analysis

## Scope & Limitations

GRACE-lite implements only the **code-level layer** (roughly stages 4-5) of the
full GRACE methodology. It does **not** cover:

- Requirements analysis
- Technology selection
- Architectural planning (DevelopmentPlan.xml)
- Verification planning (verification-plan.xml)
- Multi-agent orchestration (ExecutionPacket, GraphDelta, etc.)
- Controller/Worker execution model

Upstream stages are governed by OpenSpec or equivalent methodology.

## References

- [Bootstrap guide](references/bootstrap.md) — initializing GRACE-lite on a new
  project
- [Graph template](assets/knowledge-graph.xml.template) — used by `--init`

## Acknowledge

- [osovv/grace-marketplace](https://github.com/osovv/grace-marketplace) — GRACE:
  open Agent Skills for contract-driven AI code generation with semantic markup,
  knowledge graphs, and support for Claude Code, Codex CLI, and Kilo Code.
