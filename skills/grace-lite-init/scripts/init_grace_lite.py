#!/usr/bin/env python3
# FILE: scripts/init_grace_lite.py
# VERSION: 0.1.0

# START_MODULE_CONTRACT
#   PURPOSE: Bootstrap GRACE-lite on a project — inject AGENTS.md forced context,
#            create knowledge-graph.xml, copy grace_check.py.
#   SCOPE: AGENTS.md injection, docs/ and scripts/ creation, template copying.
#   DEPENDS: none
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   main                           CLI entry point
#   _find_agents_md                 Locate existing AGENTS.md or pick creation target
#   _inject_grace_lite              Insert/update GRACE-lite section in AGENTS.md
#   _init_knowledge_graph           Copy knowledge-graph.xml template if missing
#   _copy_grace_check               Copy grace_check.py to project scripts/
# END_MODULE_MAP

"""GRACE-lite project initializer.

Usage:
    python3 init_grace_lite.py          # bootstrap current directory
    python3 init_grace_lite.py --root /path/to/project
    python3 init_grace_lite.py --dry-run  # preview actions without writing
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# --- Paths ---

_SKILL_DIR = Path(__file__).resolve().parent.parent
_INJECTION_TEMPLATE = _SKILL_DIR / "assets" / "AGENTS.tmpl.md"
_GRAPH_TEMPLATE = _SKILL_DIR / "assets" / "knowledge-graph.tmpl.xml"
_GRACE_LITE_SKILL_DIR = _SKILL_DIR.parent / "grace-lite-init"
_GRACE_CHECK_SRC = _GRACE_LITE_SKILL_DIR / "scripts" / "grace_check.py"

_START_MARKER = "<!-- START_GRACE-lite -->"
_END_MARKER = "<!-- END_GRACE-lite -->"

_AGENTS_CANDIDATES = ("AGENTS.md", "CLAUDE.md", ".agents/AGENTS.md", ".claude/CLAUDE.md")


# --- Discovery ---


def _find_agents_md(project_root: Path) -> Path:
    """Find existing AGENTS.md or determine creation target.

    Returns the path where AGENTS.md should be written/updated.
    """
    for rel in _AGENTS_CANDIDATES:
        candidate = project_root / rel
        if candidate.exists():
            return candidate
    return project_root / "AGENTS.md"


# --- AGENTS.md injection ---


def _inject_grace_lite(agents_path: Path, injection: str, *, dry_run: bool = False) -> str:
    """Insert or update GRACE-lite section in AGENTS.md.

    Returns action description for reporting.
    """
    if dry_run:
        if agents_path.exists():
            content = agents_path.read_text(encoding="utf-8")
            if _START_MARKER in content:
                return f"Would update GRACE-lite section in {agents_path}"
            return f"Would append GRACE-lite section to {agents_path}"
        return f"Would create {agents_path} with GRACE-lite section"

    if agents_path.exists():
        content = agents_path.read_text(encoding="utf-8")
        if _START_MARKER in content and _END_MARKER in content:
            # Replace existing section
            start_idx = content.index(_START_MARKER)
            end_idx = content.index(_END_MARKER) + len(_END_MARKER)
            new_content = content[:start_idx] + injection + content[end_idx:]
            agents_path.write_text(new_content, encoding="utf-8")
            return f"Updated GRACE-lite section in {agents_path}"

        # Append at end with separator
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + injection + "\n"
        agents_path.write_text(content, encoding="utf-8")
        return f"Appended GRACE-lite section to {agents_path}"

    # Create new file
    agents_path.parent.mkdir(parents=True, exist_ok=True)
    agents_path.write_text(injection + "\n", encoding="utf-8")
    return f"Created {agents_path} with GRACE-lite section"


# --- Knowledge graph ---


def _init_knowledge_graph(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Create docs/knowledge-graph.xml from template if it doesn't exist.

    Returns action description or None if already exists.
    """
    target = project_root / "docs" / "knowledge-graph.xml"
    if target.exists():
        return None
    if not _GRAPH_TEMPLATE.exists():
        return f"Skipping knowledge graph: template not found at {_GRAPH_TEMPLATE}"
    if dry_run:
        return f"Would create {target}"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_GRAPH_TEMPLATE, target)
    return f"Created {target}"


# --- grace_check.py ---


def _copy_grace_check(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Copy grace_check.py to project scripts/ directory.

    Copies only if the source exists and the target is missing or older.
    Returns action description or None if skipped.
    """
    if not _GRACE_CHECK_SRC.exists():
        return f"Skipping grace_check.py: source not found at {_GRACE_CHECK_SRC}"
    target = project_root / "scripts" / "grace_check.py"
    if target.exists():
        src_mtime = _GRACE_CHECK_SRC.stat().st_mtime
        tgt_mtime = target.stat().st_mtime
        if tgt_mtime >= src_mtime:
            return None  # already up to date
        if dry_run:
            return f"Would update {target} (newer version available)"
        action = "Updated"
    else:
        if dry_run:
            return f"Would copy {target}"
        action = "Copied"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_GRACE_CHECK_SRC, target)
    return f"{action} {target}"


# --- CLI ---


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap GRACE-lite on a project.",
        prog="init_grace_lite",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing any files",
    )
    args = parser.parse_args(argv)

    project_root = args.root.resolve()
    dry_run: bool = args.dry_run  # type: ignore[assignment]

    if not project_root.exists():
        print(f"Project root not found: {project_root}", file=sys.stderr)
        return 1

    if not _INJECTION_TEMPLATE.exists():
        print(f"Injection template not found: {_INJECTION_TEMPLATE}", file=sys.stderr)
        return 1

    injection = _INJECTION_TEMPLATE.read_text(encoding="utf-8").rstrip("\n")

    actions: list[str] = []

    # 1. AGENTS.md injection
    agents_path = _find_agents_md(project_root)
    actions.append(_inject_grace_lite(agents_path, injection, dry_run=dry_run))

    # 2. Knowledge graph
    graph_action = _init_knowledge_graph(project_root, dry_run=dry_run)
    if graph_action:
        actions.append(graph_action)

    # 3. grace_check.py
    checker_action = _copy_grace_check(project_root, dry_run=dry_run)
    if checker_action:
        actions.append(checker_action)

    # Report
    mode = "[DRY RUN] " if dry_run else ""
    print(f"GRACE-lite init {mode}for {project_root}")
    print("-" * 50)
    for a in actions:
        print(f"  {a}")
    print()

    if not dry_run:
        print("Next steps:")
        print("  1. Edit docs/knowledge-graph.xml (NAME, VERSION, keywords)")
        print("  2. Add M- entries for each governed module")
        print("  3. Add GRACE markup to source files (see AGENTS.md)")
        print("  4. Run: python3 scripts/grace_check.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
