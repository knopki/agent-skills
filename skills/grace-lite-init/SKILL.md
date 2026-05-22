---
name: grace-lite-init
description: Bootstrap GRACE-lite for a project. Use when user ask you to initialize project with GRACE-lite.
license: MIT
compatibility: Requires Python 3.10+
metadata:
  author: Sergei Korolev <knopki@duck.com>
  url: https://github.com/knopki/agent-skills
---

# grace-lite-init

Bootstrap GRACE-lite (Graph-RAG Anchored Code Engineering) methodology on a project.

## When to Use

- Starting a new project that will use GRACE-lite
- Adding GRACE-lite semantic markup + knowledge graph to an existing project
- Re-initialising after the injected AGENTS.md section was accidentally removed

## What It Does

Runs `scripts/init_grace_lite.py` which:

1. **Injects GRACE-lite methodology** into the project's `AGENTS.md` between
   `<!-- START_GRACE-lite -->` and `<!-- END_GRACE-lite -->` markers. This is
   **forced context** — the agent always reads AGENTS.md and cannot skip it.

2. **Creates `docs/knowledge-graph.xml`** from a template if it doesn't exist.

3. **Copies `grace_check.py`** to `scripts/grace_check.py` for validation.

## Steps

1. Run the init script from the project root:

   ```bash
   python3 .agents/skills/grace-lite-init/scripts/init_grace_lite.py
   ```

2. Edit `docs/knowledge-graph.xml` — update `NAME`, `VERSION`, `keywords`, `annotation`.

3. Add `<M-DOMAIN>` entries for each governed module with `TYPE`, `STATUS`,
   `<purpose>`, `<path>`, `<depends>`.

4. Add GRACE markup to governed source files (see AGENTS.md for reference).

5. Run `python3 scripts/grace_check.py` to validate.

## Output

- Updated `AGENTS.md` with GRACE-lite section injected
- `docs/knowledge-graph.xml` (if not existed)
- `scripts/grace_check.py` (validates XML + source markup)
