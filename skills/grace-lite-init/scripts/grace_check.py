#!/usr/bin/env python3
# FILE: grace_check.py
# VERSION: 0.5.0

# START_MODULE_CONTRACT
#   PURPOSE: Validate docs/knowledge-graph.xml and GRACE-lite source markup.
#   SCOPE: XML structural validation, source file markers, contract fields, function/block sizes,
#           brace syntax, cross-references.
#   DEPENDS: none
#   LINKS: none
# END_MODULE_CONTRACT
#
# START_MODULE_MAP
#   main                           CLI entry point
#   check_xml                      Run all XML validation rules
#   check_source                   Run all source markup validation rules
#   _validate_structure            Root/project element checks
#   _check_project_attrs           Project attribute validation
#   _check_project_children        Project child element validation
#   _validate_modules              Module entry iteration and duplicate detection
#   _check_module_attrs            Single module attribute and child validation
#   _check_module_annotations      Annotation prefix and PURPOSE validation
#   _validate_data_flows           Data flow entry iteration and syntax checks
#   _validate_cross_links          CrossLink attribute checks
#   _validate_integrity            Cross-reference integrity orchestrator
#   _collect_module_ids            Collect M-IDs and paths from project
#   _check_depends_refs            Validate depends references
#   _check_crosslink_refs          Validate CrossLink from/to references
#   _check_dataflow_refs           Validate data flow M-ID references
#   _check_path_existence          Validate module path existence on disk
#   _find_governed_files           Find .py/.js/.css files with START_MODULE_CONTRACT
#   _read_governed_file            Read governed file with JS/CSS comment normalization
#   _normalize_css_block           Normalize leading /* */ GRACE block to # comments
#   _check_source_modules          Check module markers and file sizes
#   _check_file_module_markers     Per-file marker presence and size check
#   _parse_module_contract         Extract MODULE_CONTRACT fields as dict
#   _check_function_contracts      Check contract pairing, syntax, func sizes
#   _check_file_func_contracts     Per-file function contract validation
#   _parse_func_contracts          Parse START/END_CONTRACT ranges
#   _check_brace_syntax            Validate INPUTS/OUTPUTS brace syntax
#   _find_func_end                 Find line index after function body
#   _check_func_sizes              Check function + contract line counts
#   _check_block_markers           Check block pairing and sizes
#   _check_file_blocks             Per-file block marker validation
#   _check_cross_references        Check LINKS references against XML M-IDs
#   _report                        Format and emit findings
# END_MODULE_MAP
#
# START_CHANGE_SUMMARY
#   LAST_CHANGE: v0.5.1 - Removed --init/init_template (delegated to init_grace_lite.py).
#   PREVIOUS_CHANGE: v0.5.0 - Portable skill version: auto-detect PROJECT_ROOT, --root flag,
#                    TEMPLATE_PATH from skill assets, Python 3.10+ compat.
# END_CHANGE_SUMMARY

"""GRACE-lite knowledge graph validator and source markup checker.

Usage:
    python grace_check.py              # validate XML + source markup
    python grace_check.py --check-xml  # explicit XML validation
    python grace_check.py --check-source  # source markup checks
    python grace_check.py --json       # machine-readable JSON output
    python grace_check.py --root DIR   # explicit project root directory
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

# --- Paths ---

_SKILL_DIR = Path(__file__).resolve().parent.parent
_GRAPH_RELATIVE = Path("docs") / "knowledge-graph.xml"


def _detect_project_root() -> Path:
    """Auto-detect project root by searching for docs/knowledge-graph.xml.

    Search order:
    1. Current working directory
    2. Walking up from the script directory (handles skill installed inside a project)
    Falls back to cwd if not found.
    """
    cwd = Path.cwd()
    if (cwd / _GRAPH_RELATIVE).exists():
        return cwd
    for parent in Path(__file__).resolve().parent.parents:
        if (parent / _GRAPH_RELATIVE).exists():
            return parent
    return cwd


PROJECT_ROOT = _detect_project_root()
_SELF_PATH = Path(__file__).resolve()

# --- Constants ---

VALID_MODULE_TYPES = frozenset(
    {
        "ENTRY_POINT",
        "CORE_LOGIC",
        "DATA_LAYER",
        "UI_COMPONENT",
        "UTILITY",
        "INTEGRATION",
    }
)
VALID_MODULE_STATUSES = frozenset({"planned", "partial", "implemented"})
VALID_ANNOTATION_PREFIXES = frozenset({"fn-", "class-", "type-", "export-", "const-"})
VALID_PROJECT_CHILDREN = frozenset({"keywords", "annotation"})
MID_REF_RE = re.compile(r"\bM-[A-Z][A-Z0-9-]*\b")
MID_TAG_RE = re.compile(r"^M-[A-Z][A-Z0-9-]*$")
DFID_TAG_RE = re.compile(r"^DF-[A-Z][A-Z0-9-]*$")

CONTRACT_START_RE = re.compile(r"^\s*#\s*START_CONTRACT:\s*(\w+)")
CONTRACT_END_RE = re.compile(r"^\s*#\s*END_CONTRACT:\s*(\w+)")
FUNC_DEF_RE = re.compile(r"^(?:async\s+)?def\s+(\w+)\s*\(")
SRC_BLOCK_START_RE = re.compile(r"^\s*#\s*START_BLOCK_(\w+)")
SRC_BLOCK_END_RE = re.compile(r"^\s*#\s*END_BLOCK_(\w+)")
_GOVERNED_SUFFIXES = (".py", ".js", ".css")
_SKIP_DIRS = frozenset(
    {
        ".agents",
        ".codex",
        ".claude",
        ".direnv",
        ".devenv",
        ".git",
        ".tox",
        ".venv",
        ".opencode",
        "__pycache__",
        "node_modules",
        "openspec",
        "venv",
    }
)

# --- Data structures ---


@dataclass
class Finding:
    severity: str  # "error" or "warning"
    rule: str
    message: str
    location: str = ""


# START_BLOCK_FINDINGS_COLLECTOR
class Findings:
    """Collect and report validation findings."""

    def __init__(self) -> None:
        self._items: list[Finding] = []

    def error(self, rule: str, message: str, location: str = "") -> None:
        self._items.append(Finding("error", rule, message, location))

    def warning(self, rule: str, message: str, location: str = "") -> None:
        self._items.append(Finding("warning", rule, message, location))

    @property
    def has_errors(self) -> bool:
        return any(f.severity == "error" for f in self._items)

    def to_json(self) -> list[dict]:
        return [
            {
                "severity": f.severity,
                "rule": f.rule,
                "message": f.message,
                "location": f.location,
            }
            for f in self._items
        ]


# END_BLOCK_FINDINGS_COLLECTOR


# --- XML validation rules ---


# START_BLOCK_VALIDATE_STRUCTURE
def _validate_structure(root: ET.Element, findings: Findings) -> None:
    if root.tag != "KnowledgeGraph":
        findings.error("root-tag", f"Root element is <{root.tag}>, expected <KnowledgeGraph>")
        return
    projects = root.findall("Project")
    if not projects:
        findings.error("project-missing", "No <Project> element under <KnowledgeGraph>")
        return
    if len(projects) > 1:
        findings.error("project-duplicate", f"Found {len(projects)} <Project> elements, expected 1")
    project = projects[0]
    _check_project_attrs(project, findings)
    _check_project_children(project, findings)


# END_BLOCK_VALIDATE_STRUCTURE


def _check_project_attrs(project: ET.Element, findings: Findings) -> None:
    for attr in ("NAME", "VERSION"):
        if attr not in project.attrib:
            findings.error("project-attr", f"<Project> missing required attribute '{attr}'")
    for child in ("keywords", "annotation"):
        if project.find(child) is None:
            findings.error("project-child", f"<Project> missing <{child}> child")


def _check_project_children(project: ET.Element, findings: Findings) -> None:
    for child in project:
        if child.tag in VALID_PROJECT_CHILDREN:
            continue
        if child.tag.startswith(("M-", "DF-")) or child.tag == "CrossLink":
            continue
        findings.warning(
            "project-child-unknown",
            f"Unexpected <{child.tag}> inside <Project>",
            location=f"<Project> -> <{child.tag}>",
        )


# START_CONTRACT: _check_module_attrs
# PURPOSE: Validate a single module's required attributes and children.
# INPUTS: { elem: ET.Element - module element, findings: Findings - collector }
# OUTPUTS: { None }
# END_CONTRACT: _check_module_attrs
def _check_module_attrs(elem: ET.Element, findings: Findings) -> None:
    loc = f"<{elem.tag}>"
    for attr in ("NAME", "TYPE", "STATUS"):
        if attr not in elem.attrib:
            findings.error(
                "module-attr",
                f"{loc} missing required attribute '{attr}'",
                location=loc,
            )
    mod_type = elem.get("TYPE", "")
    if mod_type and mod_type not in VALID_MODULE_TYPES:
        findings.error(
            "module-type",
            f"{loc} TYPE='{mod_type}' not in: {', '.join(sorted(VALID_MODULE_TYPES))}",
            location=loc,
        )
    mod_status = elem.get("STATUS", "")
    if mod_status and mod_status not in VALID_MODULE_STATUSES:
        findings.error(
            "module-status",
            f"{loc} STATUS='{mod_status}' not in: {', '.join(sorted(VALID_MODULE_STATUSES))}",
            location=loc,
        )
    for child_tag in ("purpose", "path", "depends"):
        if elem.find(child_tag) is None:
            findings.error("module-child", f"{loc} missing <{child_tag}> child", location=loc)
    for tag in ("purpose", "path"):
        child = elem.find(tag)
        if child is not None and not (child.text or "").strip():
            findings.warning("module-empty", f"{loc} <{tag}> is empty", location=loc)


# START_CONTRACT: _check_module_annotations
# PURPOSE: Validate annotation prefix, PURPOSE attribute, and duplicates.
# INPUTS: { elem: ET.Element - module element, findings: Findings - collector }
# OUTPUTS: { None }
# END_CONTRACT: _check_module_annotations
def _check_module_annotations(elem: ET.Element, findings: Findings) -> None:
    annotations = elem.find("annotations")
    if annotations is None:
        return
    loc = f"<{elem.tag}>"
    seen_ann: set[str] = set()
    for ann in annotations:
        tag = ann.tag
        if tag in seen_ann:
            findings.error("annotation-duplicate", f"{loc} duplicate <{tag}>", location=loc)
        seen_ann.add(tag)
        valid_prefix = any(tag.startswith(p) for p in VALID_ANNOTATION_PREFIXES)
        if not valid_prefix:
            findings.error(
                "annotation-prefix",
                f"{loc} <{tag}> prefix not in: {', '.join(sorted(VALID_ANNOTATION_PREFIXES))}",
                location=f"{loc} -> <{tag}>",
            )
        if "PURPOSE" not in ann.attrib:
            findings.warning(
                "annotation-purpose",
                f"{loc} <{tag}> missing PURPOSE attribute",
                location=f"{loc} -> <{tag}>",
            )


# START_BLOCK_VALIDATE_MODULES
def _validate_modules(project: ET.Element, findings: Findings) -> None:
    seen: dict[str, int] = {}
    # START_BLOCK_ITERATE_MODULES
    for elem in project:
        if not elem.tag.startswith("M-"):
            continue
        if not MID_TAG_RE.match(elem.tag):
            findings.error(
                "mid-pattern",
                f"<{elem.tag}> is not a valid M-ID",
                location=f"<{elem.tag}>",
            )
            continue
        seen[elem.tag] = seen.get(elem.tag, 0) + 1
        _check_module_attrs(elem, findings)
        _check_module_annotations(elem, findings)
    # END_BLOCK_ITERATE_MODULES
    # START_BLOCK_CHECK_DUPLICATE_MIDS
    for mid, count in seen.items():
        if count > 1:
            findings.error(
                "module-duplicate",
                f"<{mid}> appears {count} times",
                location=f"<{mid}>",
            )
    # END_BLOCK_CHECK_DUPLICATE_MIDS


# END_BLOCK_VALIDATE_MODULES


# START_BLOCK_VALIDATE_DATA_FLOWS
def _validate_data_flows(project: ET.Element, findings: Findings) -> None:
    seen: dict[str, int] = {}
    # START_BLOCK_ITERATE_DATAFLOWS
    for elem in project:
        if not elem.tag.startswith("DF-"):
            continue
        if not DFID_TAG_RE.match(elem.tag):
            findings.error(
                "dfid-pattern",
                f"<{elem.tag}> is not a valid DF-ID",
                location=f"<{elem.tag}>",
            )
            continue
        seen[elem.tag] = seen.get(elem.tag, 0) + 1
        loc = f"<{elem.tag}>"
        if "NAME" not in elem.attrib:
            findings.error("dataflow-attr", f"{loc} missing 'NAME' attribute", location=loc)
        _check_df_syntax(elem, loc, findings)
    # END_BLOCK_ITERATE_DATAFLOWS
    # START_BLOCK_CHECK_DUPLICATE_DFIDS
    for dfid, count in seen.items():
        if count > 1:
            findings.error(
                "dataflow-duplicate",
                f"<{dfid}> appears {count} times",
                location=f"<{dfid}>",
            )
    # END_BLOCK_CHECK_DUPLICATE_DFIDS


# END_BLOCK_VALIDATE_DATA_FLOWS


# START_CONTRACT: _check_df_syntax
# PURPOSE: Validate data flow text contains only M-IDs and allowed separators.
# INPUTS: { elem: ET.Element - DF element, loc: str, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_df_syntax
def _check_df_syntax(elem: ET.Element, loc: str, findings: Findings) -> None:
    text = (elem.text or "").strip()
    if not text:
        findings.error("dataflow-empty", f"{loc} has no flow text", location=loc)
        return
    stripped = re.sub(r"\bM-[A-Z][A-Z0-9-]*\b", "", text)
    stripped = stripped.replace("->", "").replace(";", "").replace("/", "").strip()
    if stripped:
        findings.error("dataflow-syntax", f"{loc} unexpected tokens: '{stripped}'", location=loc)


# START_BLOCK_VALIDATE_CROSS_LINKS
def _validate_cross_links(project: ET.Element, findings: Findings) -> None:
    seen: set[str] = set()
    for elem in project:
        if elem.tag != "CrossLink":
            continue
        loc = "<CrossLink>"
        for attr in ("from", "to", "relation"):
            if attr not in elem.attrib:
                findings.error("crosslink-attr", f"<CrossLink> missing '{attr}'", location=loc)
        key = f"{elem.get('from', '')}:{elem.get('to', '')}:{elem.get('relation', '')}"
        if key in seen:
            findings.warning("crosslink-duplicate", f"Duplicate CrossLink {key}", location=loc)
        seen.add(key)
        relation = elem.get("relation", "")
        if relation and not relation.strip():
            findings.warning("crosslink-relation", "<CrossLink> empty relation", location=loc)


# END_BLOCK_VALIDATE_CROSS_LINKS


# --- Integrity helpers ---


# START_CONTRACT: _collect_module_ids
# PURPOSE: Collect all M-ID tags and their paths from the project element.
# INPUTS: { project: ET.Element }
# OUTPUTS: { tuple[set[str], dict[str, list[str]]] - known M-IDs and module paths }
# END_CONTRACT: _collect_module_ids
def _collect_module_ids(project: ET.Element) -> tuple[set[str], dict[str, list[str]]]:
    known: set[str] = set()
    paths: dict[str, list[str]] = {}
    for elem in project:
        if not elem.tag.startswith("M-"):
            continue
        known.add(elem.tag)
        path_elem = elem.find("path")
        if path_elem is not None and path_elem.text:
            paths.setdefault(elem.tag, []).append(path_elem.text.strip())
    return known, paths


# START_CONTRACT: _check_depends_refs
# PURPOSE: Validate that depends references point to existing M-IDs.
# INPUTS: { project: ET.Element, known_mids: set[str], findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_depends_refs
def _check_depends_refs(project: ET.Element, known_mids: set[str], findings: Findings) -> None:
    for elem in project:
        if not elem.tag.startswith("M-"):
            continue
        depends = elem.find("depends")
        if depends is None:
            continue
        dep_text = (depends.text or "").strip()
        if not dep_text or dep_text.lower() == "none":
            continue
        for dep in re.split(r"[,\s]+", dep_text):
            dep = dep.strip()
            if dep.startswith("M-") and dep not in known_mids:
                findings.error(
                    "depends-ref",
                    f"<{elem.tag}> references unknown module '{dep}'",
                    location=f"<{elem.tag}>",
                )


# START_CONTRACT: _check_crosslink_refs
# PURPOSE: Validate CrossLink from/to point to existing M-IDs.
# INPUTS: { project: ET.Element, known_mids: set[str], findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_crosslink_refs
def _check_crosslink_refs(project: ET.Element, known_mids: set[str], findings: Findings) -> None:
    for elem in project:
        if elem.tag != "CrossLink":
            continue
        for attr in ("from", "to"):
            ref = elem.get(attr, "")
            if ref.startswith("M-") and ref not in known_mids:
                findings.error(
                    "crosslink-ref",
                    f"<CrossLink {attr}='{ref}'> references unknown module",
                    location=f"<CrossLink {attr}='{ref}'>",
                )


# START_CONTRACT: _check_dataflow_refs
# PURPOSE: Validate data flow M-ID references point to existing modules.
# INPUTS: { project: ET.Element, known_mids: set[str], findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_dataflow_refs
def _check_dataflow_refs(project: ET.Element, known_mids: set[str], findings: Findings) -> None:
    for elem in project:
        if not elem.tag.startswith("DF-"):
            continue
        for ref in MID_REF_RE.findall(elem.text or ""):
            if ref not in known_mids:
                findings.error(
                    "dataflow-ref",
                    f"<{elem.tag}> references unknown module '{ref}'",
                    location=f"<{elem.tag}>",
                )


# START_CONTRACT: _check_path_existence
# PURPOSE: Validate that module paths exist on disk.
# INPUTS: { module_paths: dict[str, list[str]], project_root: Path, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_path_existence
def _check_path_existence(
    module_paths: dict[str, list[str]], project_root: Path, findings: Findings
) -> None:
    for mid, raw_paths in module_paths.items():
        for raw in raw_paths:
            for p in raw.split(";"):
                p = p.strip()
                if p and not (project_root / p).exists():
                    findings.warning(
                        "path-not-found",
                        f"<{mid}> path '{p}' does not exist",
                        location=f"<{mid}> -> <path>",
                    )


# START_BLOCK_VALIDATE_INTEGRITY
def _validate_integrity(project: ET.Element, findings: Findings, project_root: Path) -> None:
    known_mids, module_paths = _collect_module_ids(project)
    # START_BLOCK_CHECK_REFS
    _check_depends_refs(project, known_mids, findings)
    _check_crosslink_refs(project, known_mids, findings)
    _check_dataflow_refs(project, known_mids, findings)
    # END_BLOCK_CHECK_REFS
    _check_path_existence(module_paths, project_root, findings)


# END_BLOCK_VALIDATE_INTEGRITY


# --- Source scanning helpers ---


# START_CONTRACT: _find_governed_files
# PURPOSE: Find all governed files (.py, .js, .css) under root containing START_MODULE_CONTRACT.
# INPUTS: { root: Path - project root to scan }
# OUTPUTS: { list[Path] - sorted list of governed file paths }
# END_CONTRACT: _find_governed_files
def _find_governed_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for suffix in _GOVERNED_SUFFIXES:
        for p in root.rglob(f"*{suffix}"):
            if any(part in _SKIP_DIRS for part in p.parts):
                continue
            if p.resolve() == _SELF_PATH:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if "START_MODULE_CONTRACT" in text:
                files.append(p)
    return sorted(files)


def _read_governed_file(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    suffix = path.suffix
    if suffix == ".js":
        return [re.sub(r"^(\s*)//", r"\1#", ln) for ln in lines]
    if suffix == ".css":
        return _normalize_css_block(lines)
    return lines


def _normalize_css_block(lines: list[str]) -> list[str]:
    result: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip()
        if not in_block and stripped.startswith("/*"):
            in_block = True
            line = re.sub(r"/\*", "#", line, count=1)
            if "*/" in line:
                line = line.replace("*/", "")
                in_block = False
            result.append(line)
            continue
        if in_block:
            if "*/" in line:
                content = line.replace("*/", "").strip()
                if content:
                    result.append("# " + content)
                in_block = False
                continue
            result.append(("# " + stripped) if stripped else "")
        else:
            result.append(line)
    return result


# --- Source: module markers and size ---


# START_CONTRACT: _check_source_modules
# PURPOSE: Check module-level markers and file sizes for all governed files.
# INPUTS: { project_root: Path, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_source_modules
def _check_source_modules(project_root: Path, findings: Findings) -> None:
    for path in _find_governed_files(project_root):
        lines = _read_governed_file(path)
        _check_file_module_markers(path, lines, findings, project_root)


# START_CONTRACT: _check_file_module_markers
# PURPOSE: Check that a governed file has all required module markers and respects size limits.
# INPUTS: { path: Path, lines: list[str], findings: Findings, project_root: Path }
# OUTPUTS: { None }
# END_CONTRACT: _check_file_module_markers
def _check_file_module_markers(
    path: Path, lines: list[str], findings: Findings, project_root: Path
) -> None:
    loc = str(path.relative_to(project_root))
    text = "\n".join(lines)
    for marker in ("START_MODULE_MAP", "START_CHANGE_SUMMARY"):
        if marker not in text:
            findings.error("source-missing-marker", f"Missing {marker}", location=loc)
    count = len(lines)
    if count > 1000:
        findings.error("module-size-hard", f"{count} lines (limit 1000)", location=loc)
    elif count > 500:
        findings.warning("module-size-soft", f"{count} lines (soft limit 500)", location=loc)


# --- Source: function contracts ---


# START_CONTRACT: _check_function_contracts
# PURPOSE: Check function contract pairing, brace syntax, and function sizes.
# INPUTS: { project_root: Path, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_function_contracts
def _check_function_contracts(project_root: Path, findings: Findings) -> None:
    for path in _find_governed_files(project_root):
        lines = _read_governed_file(path)
        _check_file_func_contracts(path, lines, findings, project_root)


# START_CONTRACT: _check_file_func_contracts
# PURPOSE: Per-file function contract validation: pairing, syntax, sizes.
# INPUTS: { path: Path, lines: list[str], findings: Findings, project_root: Path }
# OUTPUTS: { None }
# END_CONTRACT: _check_file_func_contracts
def _check_file_func_contracts(
    path: Path, lines: list[str], findings: Findings, project_root: Path
) -> None:
    loc = str(path.relative_to(project_root))
    contracts, unpaired_end = _parse_func_contracts(lines)
    for name in unpaired_end:
        findings.error(
            "func-contract-unpaired",
            f"END_CONTRACT: {name} without start",
            location=loc,
        )
    for name, (start, end) in contracts.items():
        if end is None:
            findings.error(
                "func-contract-unpaired",
                f"START_CONTRACT: {name} without end",
                location=loc,
            )
            continue
        _check_brace_syntax(name, start, end, lines, loc, findings)
    _check_func_sizes(lines, contracts, loc, findings)


# START_CONTRACT: _parse_func_contracts
# PURPOSE: Parse START_CONTRACT/END_CONTRACT ranges from source lines.
# INPUTS: { lines: list[str] }
# OUTPUTS: { tuple[dict, list] - contracts {name: (start, end|None)} and unpaired end names }
# END_CONTRACT: _parse_func_contracts
def _parse_func_contracts(
    lines: list[str],
) -> tuple[dict[str, tuple[int, int | None]], list[str]]:
    contracts: dict[str, tuple[int, int | None]] = {}
    active: dict[str, int] = {}
    unpaired_end: list[str] = []
    for i, line in enumerate(lines):
        m = CONTRACT_START_RE.match(line)
        if m:
            active[m.group(1)] = i
        m2 = CONTRACT_END_RE.match(line)
        if m2:
            name = m2.group(1)
            if name in active:
                contracts[name] = (active.pop(name), i)
            else:
                unpaired_end.append(name)
    for name, start in active.items():
        contracts[name] = (start, None)
    return contracts, unpaired_end


# START_CONTRACT: _check_brace_syntax
# PURPOSE: Validate INPUTS/OUTPUTS use object-like brace syntax in a contract.
# INPUTS: { name: str, start: int, end: int, lines: list[str], loc: str, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_brace_syntax
def _check_brace_syntax(
    name: str, start: int, end: int, lines: list[str], loc: str, findings: Findings
) -> None:
    for i in range(start, end + 1):
        stripped = lines[i].strip()
        if stripped.startswith("# INPUTS:") or stripped.startswith("# OUTPUTS:"):
            _, _, value = stripped.partition(":")
            value = value.strip()
            if not value.startswith("{") or "}" not in value:
                label = stripped.split(":")[0].strip().lstrip("# ")
                findings.error(
                    "func-brace-syntax",
                    f"{name}: {label} must use {{ }} syntax",
                    location=loc,
                )


# START_CONTRACT: _find_func_end
# PURPOSE: Find line index after function body, handling multi-line signatures.
# INPUTS: { lines: list[str], start: int - def line index }
# OUTPUTS: { int - first line index after function body }
# END_CONTRACT: _find_func_end
def _find_func_end(lines: list[str], start: int) -> int:
    body_start = start + 1
    if not lines[start].rstrip().endswith(":"):
        while body_start < len(lines):
            stripped = lines[body_start].rstrip()
            if stripped.endswith(":") and ")" in stripped:
                body_start += 1
                break
            body_start += 1
    for k in range(body_start, len(lines)):
        line = lines[k]
        if line and not line[0].isspace() and line.strip() and not line.startswith("#"):
            return k
    return len(lines)


# START_CONTRACT: _check_func_sizes
# PURPOSE: Check function + adjacent contract ≤ 60 lines and bare functions ≤ 60.
# INPUTS: { lines: list[str], contracts: dict, loc: str, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_func_sizes
def _check_func_sizes(
    lines: list[str],
    contracts: dict[str, tuple[int, int | None]],
    loc: str,
    findings: Findings,
) -> None:
    func_starts: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = FUNC_DEF_RE.match(line)
        if m:
            func_starts[m.group(1)] = i
    for name, fstart in func_starts.items():
        fend = _find_func_end(lines, fstart)
        if name in contracts:
            cstart, cend = contracts[name]
            if cend is not None and 0 < fstart - cend <= 10:
                total = fend - cstart
                if total > 60:
                    findings.warning(
                        "func-size",
                        f"{name}: {total} lines with contract (limit 60)",
                        location=loc,
                    )
                continue
        size = fend - fstart
        if size > 60:
            findings.warning("func-size", f"{name}: {size} lines (limit 60)", location=loc)


# --- Source: block markers ---


# START_CONTRACT: _check_block_markers
# PURPOSE: Check block marker pairing and size limits across governed files.
# INPUTS: { project_root: Path, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_block_markers
def _check_block_markers(project_root: Path, findings: Findings) -> None:
    for path in _find_governed_files(project_root):
        lines = _read_governed_file(path)
        _check_file_blocks(path, lines, findings, project_root)


# START_CONTRACT: _check_file_blocks
# PURPOSE: Per-file block marker pairing and size validation.
# INPUTS: { path: Path, lines: list[str], findings: Findings, project_root: Path }
# OUTPUTS: { None }
# END_CONTRACT: _check_file_blocks
def _check_file_blocks(
    path: Path, lines: list[str], findings: Findings, project_root: Path
) -> None:
    loc = str(path.relative_to(project_root))
    active: dict[str, int] = {}
    for i, line in enumerate(lines):
        m = SRC_BLOCK_START_RE.match(line)
        if m:
            active[m.group(1)] = i
        m2 = SRC_BLOCK_END_RE.match(line)
        if m2 and m2.group(1) in active:
            name = m2.group(1)
            size = i - active[name] + 1
            if size > 50:
                findings.warning(
                    "block-size", f"BLOCK_{name}: {size} lines (limit 50)", location=loc
                )
            del active[name]
    for name in active:
        findings.error(
            "block-unpaired",
            f"START_BLOCK_{name} without END_BLOCK_{name}",
            location=loc,
        )


# --- Source: cross-references ---


# START_CONTRACT: _parse_module_contract
# PURPOSE: Extract key-value fields from START_MODULE_CONTRACT block.
# INPUTS: { lines: list[str] - source file lines }
# OUTPUTS: { dict[str, str] - field name to value mapping }
# END_CONTRACT: _parse_module_contract
def _parse_module_contract(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    inside = False
    for line in lines:
        stripped = line.strip()
        if stripped == "# START_MODULE_CONTRACT":
            inside = True
            continue
        if stripped == "# END_MODULE_CONTRACT":
            break
        if inside and stripped.startswith("#"):
            content = stripped.lstrip("#").strip()
            if ":" in content:
                key, _, value = content.partition(":")
                fields[key.strip()] = value.strip()
    return fields


# START_CONTRACT: _check_cross_references
# PURPOSE: Check that LINKS fields in source reference existing M-IDs from XML.
# INPUTS: { project_root: Path, xml_root: ET.Element, findings: Findings }
# OUTPUTS: { None }
# END_CONTRACT: _check_cross_references
def _check_cross_references(project_root: Path, xml_root: ET.Element, findings: Findings) -> None:
    project = xml_root.find("Project")
    if project is None:
        return
    xml_mids: set[str] = {e.tag for e in project if e.tag.startswith("M-")}
    for path in _find_governed_files(project_root):
        lines = _read_governed_file(path)
        fields = _parse_module_contract(lines)
        links = fields.get("LINKS", "")
        loc = str(path.relative_to(project_root))
        for ref in MID_REF_RE.findall(links):
            if ref not in xml_mids:
                findings.warning(
                    "source-links-ref",
                    f"LINKS references unknown '{ref}'",
                    location=loc,
                )


# --- Public API ---


# START_CONTRACT: check_xml
# PURPOSE: Run all XML structural validation rules against the knowledge graph.
# INPUTS: { xml_path: Path - path to knowledge-graph.xml }
# OUTPUTS: { list[dict] - findings with severity/rule/message/location keys }
# END_CONTRACT: check_xml
def check_xml(xml_path: Path, project_root: Path) -> list[dict]:
    findings = Findings()
    if not xml_path.exists():
        findings.error("file-missing", f"File not found: {xml_path}")
        return findings.to_json()
    # START_BLOCK_PARSE_XML
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as exc:
        findings.error("xml-well-formed", f"XML parse error: {exc}", location=str(xml_path))
        return findings.to_json()
    # END_BLOCK_PARSE_XML
    root = tree.getroot()
    assert root is not None  # guaranteed by successful ET.parse above
    if root.tag != "KnowledgeGraph":
        findings.error("root-tag", f"Root is <{root.tag}>, expected <KnowledgeGraph>")
        return findings.to_json()
    project = root.find("Project")
    if project is None:
        findings.error("project-missing", "No <Project> under <KnowledgeGraph>")
        return findings.to_json()
    _validate_structure(root, findings)
    _validate_modules(project, findings)
    _validate_data_flows(project, findings)
    _validate_cross_links(project, findings)
    _validate_integrity(project, findings, project_root)
    return findings.to_json()


# START_CONTRACT: check_source
# PURPOSE: Run all source-level GRACE-lite markup validation checks.
# INPUTS: { project_root: Path, xml_path: Path }
# OUTPUTS: { list[dict] - findings }
# END_CONTRACT: check_source
def check_source(project_root: Path, xml_path: Path) -> list[dict]:
    findings = Findings()
    if not project_root.exists():
        findings.error("root-missing", f"Project root not found: {project_root}")
        return findings.to_json()
    if not xml_path.exists():
        findings.warning("xml-missing", f"Knowledge graph not found: {xml_path}")
    _check_source_modules(project_root, findings)
    _check_function_contracts(project_root, findings)
    _check_block_markers(project_root, findings)
    xml_root: ET.Element | None = None
    try:
        xml_root = ET.parse(xml_path).getroot() if xml_path.exists() else None
    except ET.ParseError:
        pass
    if xml_root is not None:
        _check_cross_references(project_root, xml_root, findings)
    return findings.to_json()


# --- Reporting ---


# START_CONTRACT: _report
# PURPOSE: Format findings for stdout output and return exit code.
# INPUTS: { results: list[dict], use_json: bool }
# OUTPUTS: { int - 1 if any error, 0 otherwise }
# END_CONTRACT: _report
def _report(results: list[dict], *, use_json: bool = False) -> int:
    if use_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return 1 if any(r["severity"] == "error" for r in results) else 0
    if not results:
        print("OK: no issues found.")
        return 0
    errors = [r for r in results if r["severity"] == "error"]
    warnings = [r for r in results if r["severity"] == "warning"]
    for r in errors:
        loc = f" [{r['location']}]" if r["location"] else ""
        print(f"ERROR  {r['rule']}{loc}: {r['message']}")
    for r in warnings:
        loc = f" [{r['location']}]" if r["location"] else ""
        print(f"WARN   {r['rule']}{loc}: {r['message']}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


# --- CLI ---


# START_CONTRACT: main
# PURPOSE: Parse CLI args, resolve project root, dispatch checks.
# INPUTS: { argv: list[str] | None }
# OUTPUTS: { int - exit code: 0 success, 1 failure, 2 usage error }
# END_CONTRACT: main
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="GRACE-lite knowledge graph validator", prog="grace_check"
    )
    parser.add_argument("--check-xml", action="store_true", help="Validate knowledge-graph.xml")
    parser.add_argument("--check-source", action="store_true", help="Check source markup")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")
    parser.add_argument("--root", type=Path, default=None, help="Project root directory")
    parser.add_argument("--path", type=Path, default=None, help="Explicit XML file path")
    args = parser.parse_args(argv)

    # START_BLOCK_RESOLVE_ROOT
    global PROJECT_ROOT
    if args.root:
        PROJECT_ROOT = args.root.resolve()
    # else: keep auto-detected value from _detect_project_root()
    project_root = PROJECT_ROOT
    # END_BLOCK_RESOLVE_ROOT

    # START_BLOCK_RESOLVE_XML_PATH
    if args.path:
        xml_path = args.path.resolve()
    else:
        xml_path = project_root / _GRAPH_RELATIVE
    # END_BLOCK_RESOLVE_XML_PATH

    # Default: run both XML and source checks
    if not args.check_xml and not args.check_source:
        args.check_xml = True
        args.check_source = True

    # START_BLOCK_MISSING_HINT
    if not xml_path.exists() and (args.check_xml or args.check_source):
        print(f"No knowledge-graph.xml found at {xml_path}", file=sys.stderr)
        print("Run init_grace_lite.py to create one from template.", file=sys.stderr)
        print(file=sys.stderr)
    # END_BLOCK_MISSING_HINT

    all_results: list[dict] = []
    if args.check_xml:
        all_results.extend(check_xml(xml_path, project_root))
    if args.check_source:
        all_results.extend(check_source(project_root, xml_path))
    if all_results:
        return _report(all_results, use_json=args.json_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
