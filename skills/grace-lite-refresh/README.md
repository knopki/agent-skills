# grace-lite-refresh

Stripped version of
[grace-refresh](https://github.com/osovv/grace-marketplace/tree/main/skills/grace/grace-refresh).

Synchronizes GRACE shared artifacts (`docs/knowledge-graph.xml`) with the actual
codebase. Detects drift between the documented module graph and real source
files, then applies targeted fixes with user approval.

## What's included

- **Two refresh modes**: `targeted` (scan changed modules only) and `full` (scan
  entire source tree)
- **Structured drift detection**: identifies missing modules, orphaned graph
  entries, stale cross-links, missing contracts, and stale verification
  references
- **Integrity report**: a standardized text report summarizing all detected
  drift
- **Guided fix process**: proposes concrete fixes for each issue and applies
  them only after user confirmation
- **Escalation logic**: promotes `targeted` → `full` when localized scan reveals
  broader inconsistency
- **OpenAI agent interface**: pre-configured display name, short description,
  and brand color
