import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[2] / "skills" / "grace-lite-init" / "scripts")
)
import grace_check  # type: ignore[import-not-found]
from grace_check import main  # type: ignore[import-not-found]

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
