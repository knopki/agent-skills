# grace-lite-ask

Answer a question about a GRACE-lite project using full project context. The
agent loads GRACE-lite artifacts (AGENTS.md, knowledge graph), navigates the
module structure, and provides a grounded answer with citations.

## Scope & Limitations

grace-lite-ask is a **read-only query skill** — it analyses the project and
answers questions, but does **not** modify code or documents.

The lite variant is designed for projects that only use the knowledge graph and
AGENTS.md — no full GRACE document suite is required.

## Usage

This is an **agent skill**, not a CLI tool. Trigger it by asking the agent a
question about the codebase, architecture, or implementation — the agent will
follow the SKILL.md workflow:

1. Load `AGENTS.md` and `docs/knowledge-graph.xml`
2. Identify relevant modules via the knowledge graph
3. Read MODULE_CONTRACTs, MODULE_MAPs, and source blocks as needed
4. Answer with citations to the actual artifacts

## Acknowledge

This skill is an almost complete copy of
[grace-ask](https://github.com/osovv/grace-marketplace/tree/main/skills/grace/grace-ask)
— the original GRACE ask skill stripped down to the GRACE-lite artifact set
(knowledge graph only, no GRACE CLI, no
requirements/technology/development/verification docs). The full GRACE ecosystem
lives at [osovv/grace-marketplace](https://github.com/osovv/grace-marketplace).
