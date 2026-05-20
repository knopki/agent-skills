import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "grace-lite" / "scripts"))
from grace_check import Findings, Finding, _report  # type: ignore[import-not-found]


class TestFindings:
    def test_starts_empty(self):
        f = Findings()
        assert f._items == []
        assert f.has_errors is False
        assert f.to_json() == []

    def test_error_adds_error_finding(self):
        f = Findings()
        f.error("E001", "something went wrong")
        assert f.has_errors is True
        items = f.to_json()
        assert len(items) == 1
        assert items[0]["severity"] == "error"
        assert items[0]["rule"] == "E001"
        assert items[0]["message"] == "something went wrong"
        assert items[0]["location"] == ""

    def test_warning_adds_warning_finding(self):
        f = Findings()
        f.warning("W001", "caution advised")
        assert f.has_errors is False
        items = f.to_json()
        assert len(items) == 1
        assert items[0]["severity"] == "warning"

    def test_multiple_errors_and_warnings(self):
        f = Findings()
        f.error("E1", "first error")
        f.warning("W1", "first warning")
        f.error("E2", "second error")
        f.warning("W2", "second warning")
        items = f.to_json()
        assert len(items) == 4
        assert [i["severity"] for i in items] == [
            "error",
            "warning",
            "error",
            "warning",
        ]
        assert f.has_errors is True

    def test_to_json_dict_keys(self):
        f = Findings()
        f.error("R1", "msg", location="foo.py")
        item = f.to_json()[0]
        assert set(item.keys()) == {"severity", "rule", "message", "location"}

    def test_location_defaults_to_empty_string(self):
        f = Findings()
        f.error("R1", "msg")
        assert f.to_json()[0]["location"] == ""


class TestFinding:
    def test_direct_construction(self):
        finding = Finding("error", "R1", "msg", "loc")
        assert finding.severity == "error"
        assert finding.rule == "R1"
        assert finding.message == "msg"
        assert finding.location == "loc"

    def test_default_location_is_empty(self):
        finding = Finding("warning", "R1", "msg")
        assert finding.location == ""


class TestReport:
    def test_empty_results(self, capfd):
        rc = _report([])
        out, err = capfd.readouterr()
        assert out == "OK: no issues found.\n"
        assert rc == 0

    def test_errors_only(self, capfd):
        results = [
            {"severity": "error", "rule": "E1", "message": "fail", "location": ""},
        ]
        rc = _report(results)
        out, err = capfd.readouterr()
        assert "ERROR  E1: fail" in out
        assert "0 warning(s)" in out
        assert rc == 1

    def test_warnings_only(self, capfd):
        results = [
            {"severity": "warning", "rule": "W1", "message": "caution", "location": ""},
        ]
        rc = _report(results)
        out, err = capfd.readouterr()
        assert "WARN   W1: caution" in out
        assert rc == 0

    def test_mixed_errors_and_warnings_ordering(self, capfd):
        results = [
            {"severity": "error", "rule": "E1", "message": "first", "location": ""},
            {"severity": "warning", "rule": "W1", "message": "second", "location": ""},
        ]
        rc = _report(results)
        out, err = capfd.readouterr()
        lines = out.splitlines()
        assert lines[0].startswith("ERROR")
        assert lines[1].startswith("WARN")
        assert rc == 1

    def test_json_output_no_errors(self, capfd):
        results = [
            {"severity": "warning", "rule": "W1", "message": "warn", "location": ""},
        ]
        rc = _report(results, use_json=True)
        out, err = capfd.readouterr()
        import json

        parsed = json.loads(out)
        assert len(parsed) == 1
        assert parsed[0]["severity"] == "warning"
        assert rc == 0

    def test_json_output_with_errors(self, capfd):
        results = [
            {"severity": "error", "rule": "E1", "message": "err", "location": ""},
        ]
        rc = _report(results, use_json=True)
        out, err = capfd.readouterr()
        import json

        parsed = json.loads(out)
        assert len(parsed) == 1
        assert parsed[0]["severity"] == "error"
        assert rc == 1

    def test_location_shown_in_brackets(self, capfd):
        results = [
            {"severity": "error", "rule": "E1", "message": "bad", "location": "foo.py"},
        ]
        rc = _report(results)
        out, err = capfd.readouterr()
        assert "ERROR  E1 [foo.py]: bad" in out
        assert rc == 1

    def test_no_location_no_brackets(self, capfd):
        results = [
            {"severity": "error", "rule": "E1", "message": "bad", "location": ""},
        ]
        rc = _report(results)
        out, err = capfd.readouterr()
        assert "ERROR  E1: bad" in out
        assert "[" not in out
        assert rc == 1
