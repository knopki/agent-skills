import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent.parent / "skills" / "grace-lite-init" / "scripts")
)
import init_grace_lite as sut  # type: ignore[import-not-found]


@pytest.fixture
def injection_text() -> str:
    return "<!-- START_GRACE-lite -->\n## GRACE-lite\ncontent\n<!-- END_GRACE-lite -->"


@pytest.fixture
def graph_template(tmp_path) -> Path:
    p = tmp_path / "graph_template.xml"
    p.write_text(
        "<KnowledgeGraph><Project NAME='t' VERSION='1'><keywords/><annotation/></Project></KnowledgeGraph>"
    )
    return p


@pytest.fixture
def grace_check_src(tmp_path) -> Path:
    p = tmp_path / "grace_check.py"
    p.write_text("#!/usr/bin/env python3\nprint('ok')\n")
    return p


# --- _find_agents_md ---


class TestFindAgentsMd:
    def test_none_exist(self, tmp_path):
        result = sut._find_agents_md(tmp_path)
        assert result == tmp_path / "AGENTS.md"

    def test_agents_md_first(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("root")
        result = sut._find_agents_md(tmp_path)
        assert result.name == "AGENTS.md"
        assert result.parent == tmp_path

    def test_claude_md_second(self, tmp_path):
        (tmp_path / "CLAUDE.md").write_text("root claude")
        result = sut._find_agents_md(tmp_path)
        assert result.name == "CLAUDE.md"

    def test_agents_dot_agents(self, tmp_path):
        (tmp_path / ".agents").mkdir()
        (tmp_path / ".agents" / "AGENTS.md").write_text("dot agents")
        result = sut._find_agents_md(tmp_path)
        assert result.name == "AGENTS.md"
        assert ".agents" in str(result)

    def test_priority_order(self, tmp_path):
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".claude" / "CLAUDE.md").write_text("subdir")
        (tmp_path / "CLAUDE.md").write_text("root claude")
        result = sut._find_agents_md(tmp_path)
        assert result == tmp_path / "CLAUDE.md"


# --- _inject_grace_lite ---


class TestInjectGraceLite:
    def test_creates_new_file(self, tmp_path, injection_text):
        agents = tmp_path / "AGENTS.md"
        action = sut._inject_grace_lite(agents, injection_text)
        assert "Created" in action
        content = agents.read_text()
        assert sut._START_MARKER in content
        assert sut._END_MARKER in content

    def test_appends_to_existing(self, tmp_path, injection_text):
        agents = tmp_path / "AGENTS.md"
        agents.write_text("# My Project\n")
        action = sut._inject_grace_lite(agents, injection_text)
        assert "Appended" in action
        content = agents.read_text()
        assert "# My Project" in content
        assert sut._START_MARKER in content

    def test_updates_existing_section(self, tmp_path, injection_text):
        agents = tmp_path / "AGENTS.md"
        agents.write_text(
            "# My Project\n"
            "<!-- START_GRACE-lite -->\n"
            "old content\n"
            "<!-- END_GRACE-lite -->\n"
            "# After\n"
        )
        action = sut._inject_grace_lite(agents, injection_text)
        assert "Updated" in action
        content = agents.read_text()
        assert "# My Project" in content
        assert "# After" in content
        assert "old content" not in content
        assert "## GRACE-lite" in content

    def test_updates_preserves_marker_positions(self, tmp_path, injection_text):
        agents = tmp_path / "AGENTS.md"
        before = "PREAMBLE LINE 1\nPREAMBLE LINE 2\n"
        after = "\nPOSTAMBLE LINE 1\nPOSTAMBLE LINE 2\n"
        agents.write_text(
            before + "<!-- START_GRACE-lite -->\nOLD\n<!-- END_GRACE-lite -->" + after
        )
        sut._inject_grace_lite(agents, injection_text)
        content = agents.read_text()
        assert content.startswith(before)
        assert content.endswith(after)

    def test_dry_run_no_file_write(self, tmp_path, injection_text):
        agents = tmp_path / "AGENTS.md"
        action = sut._inject_grace_lite(agents, injection_text, dry_run=True)
        assert "Would create" in action
        assert not agents.exists()

    def test_dry_run_existing_file_not_modified(self, tmp_path, injection_text):
        agents = tmp_path / "AGENTS.md"
        agents.write_text("original")
        sut._inject_grace_lite(agents, injection_text, dry_run=True)
        assert agents.read_text() == "original"


# --- _init_knowledge_graph ---


class TestInitKnowledgeGraph:
    def test_creates_when_missing(self, tmp_path, graph_template, monkeypatch):
        monkeypatch.setattr(sut, "_GRAPH_TEMPLATE", graph_template)
        result = sut._init_knowledge_graph(tmp_path)
        assert result is not None
        assert "Created" in result
        graph = tmp_path / "docs" / "knowledge-graph.xml"
        assert graph.exists()

    def test_skips_when_exists(self, tmp_path, graph_template, monkeypatch):
        monkeypatch.setattr(sut, "_GRAPH_TEMPLATE", graph_template)
        target = tmp_path / "docs" / "knowledge-graph.xml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")
        result = sut._init_knowledge_graph(tmp_path)
        assert result is None
        assert target.read_text() == "existing"

    def test_template_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sut, "_GRAPH_TEMPLATE", tmp_path / "nonexistent.xml")
        result = sut._init_knowledge_graph(tmp_path)
        assert "Skipping" in result

    def test_dry_run(self, tmp_path, graph_template, monkeypatch):
        monkeypatch.setattr(sut, "_GRAPH_TEMPLATE", graph_template)
        result = sut._init_knowledge_graph(tmp_path, dry_run=True)
        assert "Would create" in result
        assert not (tmp_path / "docs" / "knowledge-graph.xml").exists()


# --- _copy_grace_check ---


class TestCopyGraceCheck:
    def test_copies_when_missing(self, tmp_path, grace_check_src, monkeypatch):
        monkeypatch.setattr(sut, "_GRACE_CHECK_SRC", grace_check_src)
        result = sut._copy_grace_check(tmp_path)
        assert result is not None
        assert "Copied" in result
        target = tmp_path / "scripts" / "grace_check.py"
        assert target.exists()

    def test_skips_when_newer_exists(self, tmp_path, grace_check_src, monkeypatch):
        monkeypatch.setattr(sut, "_GRACE_CHECK_SRC", grace_check_src)
        target = tmp_path / "scripts" / "grace_check.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("newer")
        # touch source to be older than target
        import os

        os.utime(grace_check_src, (0, 0))
        result = sut._copy_grace_check(tmp_path)
        assert result is None
        assert target.read_text() == "newer"

    def test_updates_when_source_newer(self, tmp_path, grace_check_src, monkeypatch):
        monkeypatch.setattr(sut, "_GRACE_CHECK_SRC", grace_check_src)
        target = tmp_path / "scripts" / "grace_check.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("old")
        import os

        os.utime(target, (0, 0))
        result = sut._copy_grace_check(tmp_path)
        assert "Updated" in result
        assert target.read_text() == grace_check_src.read_text()

    def test_source_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sut, "_GRACE_CHECK_SRC", tmp_path / "nonexistent.py")
        result = sut._copy_grace_check(tmp_path)
        assert "Skipping" in result
        assert "source not found" in result

    def test_dry_run(self, tmp_path, grace_check_src, monkeypatch):
        monkeypatch.setattr(sut, "_GRACE_CHECK_SRC", grace_check_src)
        result = sut._copy_grace_check(tmp_path, dry_run=True)
        assert "Would copy" in result
        assert not (tmp_path / "scripts" / "grace_check.py").exists()


# --- main (integration) ---


class TestMain:
    @pytest.fixture(autouse=True)
    def _setup(self, tmp_path, injection_text, graph_template, grace_check_src, monkeypatch):
        self.root = tmp_path / "project"
        self.root.mkdir()
        self.injection = injection_text
        monkeypatch.setattr(sut, "_INJECTION_TEMPLATE", _fake_template(injection_text, tmp_path))
        monkeypatch.setattr(sut, "_GRAPH_TEMPLATE", graph_template)
        monkeypatch.setattr(sut, "_GRACE_CHECK_SRC", grace_check_src)
        monkeypatch.setattr(sut, "_SKILL_DIR", tmp_path / "skill")

    def test_full_init(self):
        rc = sut.main(["--root", str(self.root)])
        assert rc == 0
        agents = self.root / "AGENTS.md"
        assert agents.exists()
        assert sut._START_MARKER in agents.read_text()
        graph = self.root / "docs" / "knowledge-graph.xml"
        assert graph.exists()
        checker = self.root / "scripts" / "grace_check.py"
        assert checker.exists()

    def test_uses_claude_md_if_agents_absent(self):
        (self.root / "CLAUDE.md").write_text("claude root")
        rc = sut.main(["--root", str(self.root)])
        assert rc == 0
        content = (self.root / "CLAUDE.md").read_text()
        assert sut._START_MARKER in content
        assert "claude root" in content

    def test_dry_run_no_files(self):
        rc = sut.main(["--root", str(self.root), "--dry-run"])
        assert rc == 0
        assert not (self.root / "AGENTS.md").exists()
        assert not (self.root / "docs").exists()
        assert not (self.root / "scripts").exists()

    def test_root_not_found(self):
        rc = sut.main(["--root", "/nonexistent/path/12345"])
        assert rc == 1

    def test_idempotent(self):
        sut.main(["--root", str(self.root)])
        mtime_before = (self.root / "docs" / "knowledge-graph.xml").stat().st_mtime
        rc = sut.main(["--root", str(self.root)])
        assert rc == 0
        mtime_after = (self.root / "docs" / "knowledge-graph.xml").stat().st_mtime
        # Graph should not be recreated
        assert mtime_before == mtime_after
        # AGENTS.md section should be updated (replaced with same content)
        content = (self.root / "AGENTS.md").read_text()
        assert content.count(sut._START_MARKER) == 1


def _fake_template(text: str, tmp_path: Path) -> Path:
    p = tmp_path / "injection_template.md"
    p.write_text(text)
    return p
