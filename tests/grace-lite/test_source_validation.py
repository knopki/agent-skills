import sys
from pathlib import Path


sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "skills" / "grace-lite" / "scripts"),
)
from grace_check import (
    Findings,
    check_source,
    _find_governed_files,
    _read_governed_file,
    _normalize_css_block,
    _check_file_module_markers,
    _check_file_func_contracts,
    _parse_func_contracts,
    _check_brace_syntax,
    _find_func_end,
    _check_func_sizes,
    _check_file_blocks,
    _parse_module_contract,
)


class TestParseFuncContracts:
    def test_no_contracts(self):
        lines = ["x = 1", "y = 2"]
        assert _parse_func_contracts(lines) == ({}, [])

    def test_paired_contracts(self):
        lines = [
            "# START_CONTRACT: my_func",
            "# END_CONTRACT: my_func",
        ]
        result, unpaired = _parse_func_contracts(lines)
        assert unpaired == []
        assert result == {"my_func": (0, 1)}

    def test_unpaired_start(self):
        lines = ["# START_CONTRACT: my_func"]
        result, unpaired = _parse_func_contracts(lines)
        assert unpaired == []
        assert result == {"my_func": (0, None)}

    def test_unpaired_end(self):
        lines = ["# END_CONTRACT: my_func"]
        result, unpaired = _parse_func_contracts(lines)
        assert result == {}
        assert unpaired == ["my_func"]

    def test_multiple_contracts(self):
        lines = [
            "# START_CONTRACT: foo",
            "# END_CONTRACT: foo",
            "# START_CONTRACT: bar",
            "# END_CONTRACT: bar",
        ]
        result, unpaired = _parse_func_contracts(lines)
        assert unpaired == []
        assert result == {"foo": (0, 1), "bar": (2, 3)}


class TestParseModuleContract:
    def test_extracts_key_value_pairs(self):
        lines = [
            "# START_MODULE_CONTRACT",
            "#   PURPOSE: validate stuff",
            "#   SCOPE: all files",
            "# END_MODULE_CONTRACT",
        ]
        assert _parse_module_contract(lines) == {
            "PURPOSE": "validate stuff",
            "SCOPE": "all files",
        }

    def test_no_module_contract(self):
        lines = ["x = 1", "y = 2"]
        assert _parse_module_contract(lines) == {}

    def test_colons_in_values(self):
        lines = [
            "# START_MODULE_CONTRACT",
            "#   LINKS: M-FOO: extra info",
            "# END_MODULE_CONTRACT",
        ]
        assert _parse_module_contract(lines) == {"LINKS": "M-FOO: extra info"}


class TestNormalizeCssBlock:
    def test_no_block_comments(self):
        lines = [".foo {}", ".bar { color: red; }"]
        assert _normalize_css_block(lines) == lines

    def test_single_line_block_comment(self):
        lines = ["/* comment */"]
        result = _normalize_css_block(lines)
        assert all("#" in ln for ln in result)
        assert "*/" not in "".join(result)

    def test_multi_line_block_comment(self):
        lines = ["/* line 1", "   line 2 */"]
        result = _normalize_css_block(lines)
        assert result == ["# line 1", "# line 2"]

    def test_mixed_content(self):
        lines = [
            "/* header block",
            "   multi-line */",
            ".rule { color: red; }",
        ]
        result = _normalize_css_block(lines)
        assert result[0].startswith("#")
        assert result[1].startswith("#")
        assert result[2] == ".rule { color: red; }"


class TestReadGovernedFile:
    def test_py_file_unchanged(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text("x = 1\n# comment\n")
        lines = _read_governed_file(p)
        assert lines == ["x = 1", "# comment"]

    def test_js_file_converts_comment(self, tmp_path):
        p = tmp_path / "mod.js"
        p.write_text("// comment\nconst x = 1;\n")
        lines = _read_governed_file(p)
        assert lines == ["# comment", "const x = 1;"]

    def test_css_file_normalized(self, tmp_path):
        p = tmp_path / "mod.css"
        p.write_text("/* header */\n.rule {}\n")
        lines = _read_governed_file(p)
        assert lines[0].startswith("#")
        assert lines[1] == ".rule {}"


class TestFindGovernedFiles:
    def test_no_governed_files(self, tmp_path):
        assert _find_governed_files(tmp_path) == []

    def test_py_with_marker_found(self, tmp_path):
        p = tmp_path / "mod.py"
        p.write_text("# START_MODULE_CONTRACT\nx = 1\n")
        files = _find_governed_files(tmp_path)
        assert p in files

    def test_py_without_marker_not_found(self, tmp_path):
        (tmp_path / "mod.py").write_text("x = 1\n")
        assert _find_governed_files(tmp_path) == []

    def test_skip_dirs(self, tmp_path):
        skip = tmp_path / ".git" / "sub"
        skip.mkdir(parents=True)
        (skip / "mod.py").write_text("# START_MODULE_CONTRACT\n")
        assert _find_governed_files(tmp_path) == []

    def test_js_and_css_with_marker_found(self, tmp_path):
        js = tmp_path / "mod.js"
        css = tmp_path / "mod.css"
        js.write_text("// START_MODULE_CONTRACT\n")
        css.write_text("/* START_MODULE_CONTRACT */\n")
        files = _find_governed_files(tmp_path)
        assert js in files
        assert css in files


class TestCheckFileModuleMarkers:
    def test_all_markers_present_small_file(self, tmp_path):
        lines = [
            "# START_MODULE_MAP",
            "# END_MODULE_MAP",
            "# START_CHANGE_SUMMARY",
            "# END_CHANGE_SUMMARY",
        ]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_module_markers(path, lines, findings, tmp_path)
        assert findings.to_json() == []

    def test_missing_start_module_map(self, tmp_path):
        lines = ["# START_CHANGE_SUMMARY"]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_module_markers(path, lines, findings, tmp_path)
        items = findings.to_json()
        assert len(items) == 1
        assert items[0]["rule"] == "source-missing-marker"
        assert "START_MODULE_MAP" in items[0]["message"]

    def test_missing_start_change_summary(self, tmp_path):
        lines = ["# START_MODULE_MAP"]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_module_markers(path, lines, findings, tmp_path)
        items = findings.to_json()
        assert len(items) == 1
        assert items[0]["rule"] == "source-missing-marker"
        assert "START_CHANGE_SUMMARY" in items[0]["message"]

    def test_file_over_1000_lines(self, tmp_path):
        lines = (
            ["# START_MODULE_MAP"]
            + ["#"] * 998
            + ["# START_CHANGE_SUMMARY", "# END_CHANGE_SUMMARY"]
        )
        assert len(lines) == 1001
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_module_markers(path, lines, findings, tmp_path)
        items = findings.to_json()
        rules = {i["rule"] for i in items}
        assert "module-size-hard" in rules

    def test_file_over_500_lines(self, tmp_path):
        lines = (
            ["# START_MODULE_MAP"]
            + ["#"] * 499
            + ["# START_CHANGE_SUMMARY", "# END_CHANGE_SUMMARY"]
        )
        assert len(lines) == 502
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_module_markers(path, lines, findings, tmp_path)
        items = findings.to_json()
        rules = {i["rule"] for i in items}
        assert "module-size-soft" in rules
        assert "module-size-hard" not in rules


class TestCheckBraceSyntax:
    def test_correct_brace_syntax(self):
        lines = [
            "# START_CONTRACT: foo",
            "# INPUTS: {x: int}",
            "# OUTPUTS: {int}",
            "# END_CONTRACT: foo",
        ]
        findings = Findings()
        _check_brace_syntax("foo", 0, 3, lines, "test.py", findings)
        assert findings.to_json() == []

    def test_missing_braces(self):
        lines = [
            "# START_CONTRACT: foo",
            "# INPUTS: x: int",
            "# OUTPUTS: int",
            "# END_CONTRACT: foo",
        ]
        findings = Findings()
        _check_brace_syntax("foo", 0, 3, lines, "test.py", findings)
        items = findings.to_json()
        assert len(items) == 2
        assert all(i["rule"] == "func-brace-syntax" for i in items)


class TestFindFuncEnd:
    def test_simple_def(self):
        lines = ["def foo():", "    pass", "x = 1"]
        assert _find_func_end(lines, 0) == 2

    def test_def_at_end_of_file(self):
        lines = ["def foo():", "    pass"]
        assert _find_func_end(lines, 0) == 2

    def test_multi_line_def(self):
        lines = [
            "def foo(",
            "    x,",
            "):",
            "    pass",
            "x = 1",
        ]
        assert _find_func_end(lines, 0) == 4


class TestCheckFileBlocks:
    def test_paired_blocks_no_errors(self, tmp_path):
        lines = [
            "# START_BLOCK_FOO",
            "some code",
            "# END_BLOCK_FOO",
        ]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_blocks(path, lines, findings, tmp_path)
        assert findings.to_json() == []

    def test_unpaired_start_block(self, tmp_path):
        lines = ["# START_BLOCK_FOO", "some code"]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_blocks(path, lines, findings, tmp_path)
        items = findings.to_json()
        assert len(items) == 1
        assert items[0]["rule"] == "block-unpaired"

    def test_block_over_50_lines(self, tmp_path):
        lines = ["# START_BLOCK_BIG"] + ["#"] * 50 + ["# END_BLOCK_BIG"]
        assert len(lines) == 52
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_blocks(path, lines, findings, tmp_path)
        items = findings.to_json()
        assert len(items) == 1
        assert items[0]["rule"] == "block-size"


class TestCheckFuncSizes:
    def test_contract_within_60_lines(self):
        lines = [
            "# START_CONTRACT: foo",
            "# END_CONTRACT: foo",
            "def foo():",
            "    pass",
        ]
        contracts = {"foo": (0, 1)}
        findings = Findings()
        _check_func_sizes(lines, contracts, "test.py", findings)
        assert findings.to_json() == []

    def test_contract_over_60_lines(self):
        lines = (
            ["# START_CONTRACT: foo"]
            + ["# comment"] * 57
            + ["# END_CONTRACT: foo", "def foo():", "    pass"]
        )
        contracts = {"foo": (0, 58)}
        findings = Findings()
        _check_func_sizes(lines, contracts, "test.py", findings)
        items = findings.to_json()
        assert len(items) == 1
        assert items[0]["rule"] == "func-size"


class TestCheckFileFuncContracts:
    def test_function_with_contract_no_errors(self, tmp_path):
        lines = [
            "# START_CONTRACT: foo",
            "# INPUTS: {x: int}",
            "# OUTPUTS: {int}",
            "# END_CONTRACT: foo",
            "def foo():",
            "    return 42",
        ]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_func_contracts(path, lines, findings, tmp_path)
        assert findings.to_json() == []

    def test_unpaired_contract_error(self, tmp_path):
        lines = [
            "# START_CONTRACT: foo",
            "# PURPOSE: do stuff",
        ]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_func_contracts(path, lines, findings, tmp_path)
        items = findings.to_json()
        assert len(items) == 1
        assert items[0]["rule"] == "func-contract-unpaired"

    def test_unpaired_end_error(self, tmp_path):
        lines = ["# END_CONTRACT: bar"]
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_func_contracts(path, lines, findings, tmp_path)
        items = findings.to_json()
        assert len(items) == 1
        assert items[0]["rule"] == "func-contract-unpaired"

    def test_func_size_warning(self, tmp_path):
        lines = (
            ["# START_CONTRACT: foo"]
            + ["# comment"] * 57
            + ["# END_CONTRACT: foo", "def foo():", "    pass"]
        )
        path = tmp_path / "test.py"
        findings = Findings()
        _check_file_func_contracts(path, lines, findings, tmp_path)
        items = findings.to_json()
        rules = {i["rule"] for i in items}
        assert "func-size" in rules


class TestCheckSource:
    def test_non_existent_root(self, tmp_path):
        root = tmp_path / "nonexistent"
        results = check_source(root, tmp_path / "graph.xml")
        assert len(results) == 1
        assert results[0]["rule"] == "root-missing"

    def test_empty_project_no_governed_files(self, tmp_path):
        xml = tmp_path / "graph.xml"
        results = check_source(tmp_path, xml)
        assert all(r["severity"] == "warning" for r in results)
        assert all(r["rule"] == "xml-missing" for r in results)

    def test_project_with_governed_files(self, tmp_path):
        xml = tmp_path / "graph.xml"
        xml.write_text(
            '<?xml version="1.0"?>\n<KnowledgeGraph>\n'
            '  <Project NAME="test" VERSION="1.0">\n'
            "    <M-FOO>\n"
            "      <purpose>test</purpose>\n"
            "      <path>.</path>\n"
            "      <depends>none</depends>\n"
            "    </M-FOO>\n"
            "  </Project>\n"
            "</KnowledgeGraph>\n"
        )
        (tmp_path / "test.py").write_text(
            "# START_MODULE_CONTRACT\n"
            "#   PURPOSE: test\n"
            "#   LINKS: M-FOO\n"
            "# END_MODULE_CONTRACT\n"
            "#\n"
            "# START_MODULE_MAP\n"
            "# END_MODULE_MAP\n"
            "#\n"
            "# START_CHANGE_SUMMARY\n"
            "# END_CHANGE_SUMMARY\n"
            "\n"
            "def foo():\n"
            "    pass\n"
        )
        results = check_source(tmp_path, xml)
        errors = [r for r in results if r["severity"] == "error"]
        assert errors == [], f"Unexpected errors: {errors}"
