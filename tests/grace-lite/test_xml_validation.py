import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "skills" / "grace-lite" / "scripts"))

import xml.etree.ElementTree as ET

from grace_check import (  # type: ignore[import-not-found]
    Findings,
    check_xml,
    _validate_structure,
    _validate_modules,
    _validate_data_flows,
    _validate_cross_links,
    _validate_integrity,
    _collect_module_ids,
)


def _project_from_xml(xml: str) -> ET.Element:
    return ET.fromstring(xml)


def _project_with_modules(xml: str) -> ET.Element:
    return ET.fromstring(f"<Project>{xml}</Project>")


class TestValidateStructure:
    def test_valid(self):
        root = ET.fromstring(
            "<KnowledgeGraph>"
            "<Project NAME='x' VERSION='1'><keywords/><annotation/></Project>"
            "</KnowledgeGraph>"
        )
        findings = Findings()
        _validate_structure(root, findings)
        assert findings.to_json() == []

    def test_root_tag_error(self):
        root = ET.fromstring("<NotKnowledgeGraph><Project/></NotKnowledgeGraph>")
        findings = Findings()
        _validate_structure(root, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert rules == ["root-tag"]

    def test_project_missing(self):
        root = ET.fromstring("<KnowledgeGraph/>")
        findings = Findings()
        _validate_structure(root, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert rules == ["project-missing"]

    def test_project_duplicate(self):
        root = ET.fromstring(
            "<KnowledgeGraph>"
            "<Project NAME='a' VERSION='1'><keywords/><annotation/></Project>"
            "<Project NAME='b' VERSION='2'><keywords/><annotation/></Project>"
            "</KnowledgeGraph>"
        )
        findings = Findings()
        _validate_structure(root, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "project-duplicate" in rules


class TestValidateModules:
    _BASE = (
        "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
        "<purpose>main</purpose><path>core.py</path><depends>none</depends>"
        "</M-CORE>"
    )

    def test_valid(self):
        project = _project_with_modules(self._BASE)
        findings = Findings()
        _validate_modules(project, findings)
        assert findings.to_json() == []

    def test_missing_attr(self):
        project = _project_with_modules(
            "<M-CORE NAME='core'>"
            "<purpose>main</purpose><path>core.py</path><depends>none</depends>"
            "</M-CORE>"
        )
        findings = Findings()
        _validate_modules(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "module-attr" in rules

    def test_invalid_type(self):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='BAD_TYPE' STATUS='implemented'>"
            "<purpose>main</purpose><path>core.py</path><depends>none</depends>"
            "</M-CORE>"
        )
        findings = Findings()
        _validate_modules(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "module-type" in rules

    def test_invalid_status(self):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='unknown'>"
            "<purpose>main</purpose><path>core.py</path><depends>none</depends>"
            "</M-CORE>"
        )
        findings = Findings()
        _validate_modules(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "module-status" in rules

    def test_missing_child(self):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>main</purpose>"
            "</M-CORE>"
        )
        findings = Findings()
        _validate_modules(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "module-child" in rules

    def test_empty_purpose_warning(self):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose></purpose><path>core.py</path><depends>none</depends>"
            "</M-CORE>"
        )
        findings = Findings()
        _validate_modules(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "module-empty" in rules

    def test_duplicate_mid(self):
        project = _project_with_modules(
            self._BASE
            + (
                "<M-CORE NAME='dup' TYPE='CORE_LOGIC' STATUS='planned'>"
                "<purpose>dup</purpose><path>dup.py</path><depends>none</depends>"
                "</M-CORE>"
            )
        )
        findings = Findings()
        _validate_modules(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "module-duplicate" in rules

    def test_invalid_mid_pattern(self):
        project = _project_with_modules(
            "<M- NAME='x' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>x</purpose><path>x.py</path><depends>none</depends>"
            "</M->"
        )
        findings = Findings()
        _validate_modules(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "mid-pattern" in rules


class TestValidateDataFlows:
    def test_valid(self):
        project = _project_with_modules("<DF-DATA NAME='flow1'>M-CORE -> M-UTIL</DF-DATA>")
        findings = Findings()
        _validate_data_flows(project, findings)
        assert findings.to_json() == []

    def test_missing_name(self):
        project = _project_with_modules("<DF-DATA>M-CORE -> M-UTIL</DF-DATA>")
        findings = Findings()
        _validate_data_flows(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "dataflow-attr" in rules

    def test_empty_flow_text(self):
        project = _project_with_modules("<DF-DATA NAME='flow1'></DF-DATA>")
        findings = Findings()
        _validate_data_flows(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "dataflow-empty" in rules

    def test_invalid_tokens(self):
        project = _project_with_modules("<DF-DATA NAME='flow1'>M-CORE bad_token HERE</DF-DATA>")
        findings = Findings()
        _validate_data_flows(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "dataflow-syntax" in rules

    def test_duplicate_dfid(self):
        project = _project_with_modules(
            "<DF-DATA NAME='a'>M-CORE</DF-DATA><DF-DATA NAME='b'>M-UTIL</DF-DATA>"
        )
        findings = Findings()
        _validate_data_flows(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "dataflow-duplicate" in rules


class TestValidateCrossLinks:
    def test_valid(self):
        project = _project_with_modules(
            "<CrossLink from='M-CORE' to='M-UTIL' relation='depends_on'/>"
        )
        findings = Findings()
        _validate_cross_links(project, findings)
        assert findings.to_json() == []

    def test_missing_attr(self):
        project = _project_with_modules("<CrossLink from='M-CORE'/>")
        findings = Findings()
        _validate_cross_links(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "crosslink-attr" in rules

    def test_duplicate(self):
        project = _project_with_modules(
            "<CrossLink from='M-A' to='M-B' relation='r'/>"
            "<CrossLink from='M-A' to='M-B' relation='r'/>"
        )
        findings = Findings()
        _validate_cross_links(project, findings)
        rules = [f["rule"] for f in findings.to_json()]
        assert "crosslink-duplicate" in rules


class TestValidateIntegrity:
    def test_valid_cross_references(self, tmp_path):
        p = tmp_path / "exists.py"
        p.write_text("")
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>core</purpose><path>exists.py</path><depends>M-UTIL</depends>"
            "</M-CORE>"
            "<M-UTIL NAME='util' TYPE='UTILITY' STATUS='implemented'>"
            "<purpose>util</purpose><path>exists.py</path><depends>none</depends>"
            "</M-UTIL>"
            "<CrossLink from='M-CORE' to='M-UTIL' relation='depends_on'/>"
            "<DF-DATA NAME='flow'>M-CORE -> M-UTIL</DF-DATA>"
        )
        findings = Findings()
        _validate_integrity(project, findings, tmp_path)
        assert findings.to_json() == []

    def test_depends_unknown_mid(self, tmp_path):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>core</purpose><path>core.py</path><depends>M-UNKNOWN</depends>"
            "</M-CORE>"
        )
        findings = Findings()
        _validate_integrity(project, findings, tmp_path)
        rules = [f["rule"] for f in findings.to_json()]
        assert "depends-ref" in rules

    def test_crosslink_unknown_mid(self, tmp_path):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>core</purpose><path>core.py</path><depends>none</depends>"
            "</M-CORE>"
            "<CrossLink from='M-CORE' to='M-UNKNOWN' relation='r'/>"
        )
        findings = Findings()
        _validate_integrity(project, findings, tmp_path)
        rules = [f["rule"] for f in findings.to_json()]
        assert "crosslink-ref" in rules

    def test_dataflow_unknown_mid(self, tmp_path):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>core</purpose><path>core.py</path><depends>none</depends>"
            "</M-CORE>"
            "<DF-DATA NAME='flow'>M-CORE -> M-UNKNOWN</DF-DATA>"
        )
        findings = Findings()
        _validate_integrity(project, findings, tmp_path)
        rules = [f["rule"] for f in findings.to_json()]
        assert "dataflow-ref" in rules

    def test_path_not_found(self, tmp_path):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>core</purpose><path>nonexistent.py</path><depends>none</depends>"
            "</M-CORE>"
        )
        findings = Findings()
        _validate_integrity(project, findings, tmp_path)
        rules = [f["rule"] for f in findings.to_json()]
        assert "path-not-found" in rules


class TestCollectModuleIds:
    def test_returns_mids_and_paths(self):
        project = _project_with_modules(
            "<M-CORE NAME='core' TYPE='CORE_LOGIC' STATUS='implemented'>"
            "<purpose>core</purpose><path>core.py</path><depends>none</depends>"
            "</M-CORE>"
        )
        known, paths = _collect_module_ids(project)
        assert known == {"M-CORE"}
        assert paths == {"M-CORE": ["core.py"]}

    def test_empty_project(self):
        project = _project_with_modules("")
        known, paths = _collect_module_ids(project)
        assert known == set()
        assert paths == {}


class TestCheckXml:
    def test_file_missing(self, tmp_path):
        results = check_xml(tmp_path / "nonexistent.xml", tmp_path)
        rules = [r["rule"] for r in results]
        assert "file-missing" in rules

    def test_malformed_xml(self, tmp_path):
        p = tmp_path / "bad.xml"
        p.write_text("<KnowledgeGraph><Project></KnowledgeGraph>")
        results = check_xml(p, tmp_path)
        rules = [r["rule"] for r in results]
        assert "xml-well-formed" in rules

    def test_valid_xml_no_issues(self, tmp_path):
        p = tmp_path / "valid.xml"
        p.write_text(
            "<KnowledgeGraph>"
            "<Project NAME='test' VERSION='1'>"
            "<keywords/><annotation/>"
            "</Project>"
            "</KnowledgeGraph>"
        )
        results = check_xml(p, tmp_path)
        assert results == []

    def test_xml_with_issues(self, tmp_path):
        p = tmp_path / "issues.xml"
        p.write_text("<KnowledgeGraph><Project/></KnowledgeGraph>")
        results = check_xml(p, tmp_path)
        rules = [r["rule"] for r in results]
        assert "project-attr" in rules
        assert "project-child" in rules
