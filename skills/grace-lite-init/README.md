# grace-lite-init

One-shot bootstrap for GRACE-lite on a project. Three actions:

- **Forced context injection** — injects GRACE-lite methodology section into
  `AGENTS.md` between `<!-- START_GRACE-lite -->` / `<!-- END_GRACE-lite -->`
  markers. The agent always reads AGENTS.md and cannot skip it.
- **Knowledge graph template** — creates `docs/knowledge-graph.xml` from a
  pre-built template if it doesn't exist.
- **Validation script** — copies `grace_check.py` to `scripts/grace_check.py`
  for validating XML structure and source markup.

## Scope & Limitations

grace-lite-init is a **one-shot bootstrap** — it sets up the initial GRACE-lite
artifacts and then exits. It does **not** cover:

- Ongoing maintenance of the knowledge graph or markup
- Adding module entries or updating annotations
- Running validation (use `scripts/grace_check.py` directly)
- Re-initialization of a project already under GRACE-lite governance (re-run
  manually if markers are lost)

## Usage

```bash
python3 .agents/skills/grace-lite-init/scripts/init_grace_lite.py
# Or with a project root explicit:
python3 .agents/skills/grace-lite-init/scripts/init_grace_lite.py --root /path/to/project
# Preview without writing:
python3 .agents/skills/grace-lite-init/scripts/init_grace_lite.py --dry-run
```

## Post-init steps

1. Edit `docs/knowledge-graph.xml` — update `NAME`, `VERSION`, `keywords`, `annotation`
2. Add `<M-DOMAIN>` entries for each governed module
3. Add GRACE markup to source files (see injected AGENTS.md section for reference)
4. Run `python3 scripts/grace_check.py` to validate

## References

- [AGENTS.md template](assets/AGENTS.tmpl.md) — injected section content
- [Knowledge graph template](assets/knowledge-graph.tmpl.xml) — XML structure
  for `docs/`

## Acknowledge

- [osovv/grace-marketplace](https://github.com/osovv/grace-marketplace) — GRACE:
  open Agent Skills for contract-driven AI code generation with semantic markup,
  knowledge graphs, and support for Claude Code, Codex CLI, and Kilo Code.
