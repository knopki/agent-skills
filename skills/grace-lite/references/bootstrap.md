# Bootstrap: GRACE-lite on a New Project

## Quick Start

```bash
SKILL=.agents/skills/grace-lite

# Create initial knowledge graph from template
python $SKILL/scripts/grace_check.py --init

# Verify
python $SKILL/scripts/grace_check.py --check-xml
```

## Step-by-step

1. **Create the graph**: `--init` creates `docs/knowledge-graph.xml` from the
   bundled template. Edit `NAME`, `VERSION`, `keywords`, and `annotation`.

2. **Add module entries**: For each governed module, add an `<M-DOMAIN>` entry
   with `TYPE`, `STATUS`, `<purpose>`, `<path>`, `<depends>`. Use unique
   M-IDs as tag names (e.g. `<M-AUTH>`, `<M-STORAGE>`).

3. **Mark up source files**: Add `START_MODULE_CONTRACT`, `START_MODULE_MAP`,
   and `START_CHANGE_SUMMARY` blocks to each governed source file.

4. **Add function contracts and block markers**: For public callables and
   semantic code sections, add `START_CONTRACT`/`END_CONTRACT` and
   `START_BLOCK_*/END_BLOCK_*` markers.

5. **Add data flows and cross-links**: Trace execution paths as `<DF-*>`
   entries. Add `<CrossLink>` elements for semantic relationships.

6. **Validate**: Run `grace_check.py` (no args). Fix errors, review warnings.

7. **Commit**: Include `docs/knowledge-graph.xml` and marked-up sources.

8. Append `AGENTS.md` file from template `assets/AGENTS.md.template`

## Minimal Example

`docs/knowledge-graph.xml`:

```xml
<KnowledgeGraph>
  <Project NAME="my-app" VERSION="0.1.0">
    <keywords>web, API</keywords>
    <annotation>A simple web application.</annotation>
    <M-APP NAME="Application" TYPE="ENTRY_POINT" STATUS="implemented">
      <purpose>Main application entry point.</purpose>
      <path>src/app.py</path>
      <depends>none</depends>
      <annotations>
        <fn-main PURPOSE="Start the application" />
      </annotations>
    </M-APP>
  </Project>
</KnowledgeGraph>
```

`src/app.py`:

```python
# FILE: src/app.py
# VERSION: 0.1.0

# START_MODULE_CONTRACT
#   PURPOSE: Main application entry point.
#   SCOPE: CLI parsing and server startup.
#   DEPENDS: none
#   LINKS: M-APP
# END_MODULE_CONTRACT

# START_MODULE_MAP
#   main                           CLI entry point
# END_MODULE_MAP

# START_CHANGE_SUMMARY
#   LAST_CHANGE: v0.1.0 - Initial module with markup.
# END_CHANGE_SUMMARY

# START_CONTRACT: main
#   PURPOSE: Parse CLI args and start the server.
#   INPUTS: { argv: list[str] - command line arguments }
#   OUTPUTS: { int - exit code }
# END_CONTRACT: main
def main(argv=None):
    ...
```
