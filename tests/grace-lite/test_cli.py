import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "grace-lite" / "scripts"))
from grace_check import main, init_template
import grace_check

_ORIGINAL_PROJECT_ROOT = grace_check.PROJECT_ROOT


@pytest.fixture(autouse=True)
def _restore_project_root():
    yield
    grace_check.PROJECT_ROOT = _ORIGINAL_PROJECT_ROOT


def _make_valid_xml(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<KnowledgeGraph>\n"
        '  <Project NAME="test" VERSION="1.0">\n'
        "    <keywords/>\n"
        "    <annotation/>\n"
        "  </Project>\n"
        "</KnowledgeGraph>\n"
    )


class TestInitTemplate:
    def test_creates_file(self, tmp_path, monkeypatch):
        template = tmp_path / "template.xml"
        template.write_text("<root/>")
        monkeypatch.setattr(grace_check, "TEMPLATE_PATH", template)
        target = tmp_path / "docs" / "knowledge-graph.xml"
        rc = init_template(target)
        assert rc == 0
        assert target.exists()
        assert target.read_text() == "<root/>"

    def test_already_exists(self, tmp_path, monkeypatch, capfd):
        template = tmp_path / "template.xml"
        template.write_text("<root/>")
        monkeypatch.setattr(grace_check, "TEMPLATE_PATH", template)
        target = tmp_path / "docs" / "knowledge-graph.xml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("existing")
        rc = init_template(target)
        out, _ = capfd.readouterr()
        assert "already exists" in out
        assert rc == 1
        assert target.read_text() == "existing"

    def test_template_missing(self, tmp_path, monkeypatch, capfd):
        monkeypatch.setattr(grace_check, "TEMPLATE_PATH", tmp_path / "nonexistent.xml")
        target = tmp_path / "docs" / "knowledge-graph.xml"
        rc = init_template(target)
        assert rc == 1
        _, err = capfd.readouterr()
        assert "template not found" in err


class TestMain:
    def test_check_xml_valid(self, tmp_path, capfd):
        _make_valid_xml(tmp_path / "docs" / "knowledge-graph.xml")
        rc = main(["--check-xml", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert rc == 0
        assert out == ""

    def test_check_xml_json(self, tmp_path, capfd):
        _make_valid_xml(tmp_path / "docs" / "knowledge-graph.xml")
        rc = main(["--check-xml", "--json", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert rc == 0
        assert out == ""

    def test_check_xml_nonexistent(self, tmp_path, capfd):
        rc = main(["--check-xml", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert "file-missing" in out
        assert rc == 1

    def test_init_creates_file(self, tmp_path, monkeypatch, capfd):
        template = tmp_path / "template.xml"
        template.write_text("<root/>")
        monkeypatch.setattr(grace_check, "TEMPLATE_PATH", template)
        rc = main(["--init", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert "created:" in out
        assert rc == 0
        assert (tmp_path / "docs" / "knowledge-graph.xml").exists()

    def test_init_when_exists(self, tmp_path, monkeypatch, capfd):
        xml_path = tmp_path / "docs" / "knowledge-graph.xml"
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        xml_path.write_text("existing")
        template = tmp_path / "template.xml"
        template.write_text("<root/>")
        monkeypatch.setattr(grace_check, "TEMPLATE_PATH", template)
        rc = main(["--init", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert "already exists" in out
        assert rc == 1

    def test_check_source_empty(self, tmp_path, capfd):
        _make_valid_xml(tmp_path / "docs" / "knowledge-graph.xml")
        rc = main(["--check-source", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert rc == 0
        assert out == ""

    def test_default_runs_both(self, tmp_path, capfd):
        _make_valid_xml(tmp_path / "docs" / "knowledge-graph.xml")
        rc = main(["--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert rc == 0
        assert out == ""

    def test_root_flag(self, tmp_path, capfd, monkeypatch):
        monkeypatch.setattr(grace_check, "PROJECT_ROOT", Path("/nonexistent"))
        _make_valid_xml(tmp_path / "docs" / "knowledge-graph.xml")
        rc = main(["--check-xml", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert rc == 0
        assert out == ""

    def test_path_flag(self, tmp_path, capfd):
        custom_xml = tmp_path / "custom" / "graph.xml"
        _make_valid_xml(custom_xml)
        rc = main(["--check-xml", "--path", str(custom_xml)])
        out, _ = capfd.readouterr()
        assert rc == 0
        assert out == ""

    def test_check_xml_malformed(self, tmp_path, capfd):
        xml_path = tmp_path / "docs" / "knowledge-graph.xml"
        xml_path.parent.mkdir(parents=True, exist_ok=True)
        xml_path.write_text("<root><unclosed>")
        rc = main(["--check-xml", "--root", str(tmp_path)])
        out, _ = capfd.readouterr()
        assert "xml-well-formed" in out
        assert rc == 1

    def test_invalid_args(self):
        with pytest.raises(SystemExit) as exc:
            main(["--unknown-flag"])
        assert exc.value.code == 2
