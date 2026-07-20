"""Unit Tests for Evidence Governance Subsystem (v1.12.0-evidence).

Validates model serialization, boundary classification, negative-evidence rules,
validation engine downgrades, dual-format report generation, and CLI subcommand.
"""

import json
import pytest
from pathlib import Path
from digital_state.governance.evidence import (
    EvidenceType,
    EvidenceBoundary,
    EvidenceClassification,
    EvidenceRecord,
    resolve_repository_root,
    EvidenceValidationEngine,
    EvidenceReportGenerator,
)
from digital_state.governance.evidence.engine import EvidenceValidationError


def test_models_serialization():
    rec = EvidenceRecord(
        statement="Test PEP 427 built wheel specification rule",
        evidence_type=EvidenceType.AUTHORITATIVE_SPECIFICATION,
        boundary=EvidenceBoundary.PYTHON_PACKAGING_SPEC,
        source="PEP 427",
        classification=EvidenceClassification.VERIFIED_ABSENCE,
        justification="Wheel standard rules out post-install script execution.",
        doc_ref="PEP 427"
    )
    data = rec.to_dict()
    assert data["schema_version"] == "v1.0"
    assert data["classification"] == "VERIFIED ABSENCE"
    assert data["boundary"] == "Python Packaging Specification"

    deserialized = EvidenceRecord.from_dict(data)
    assert deserialized.statement == rec.statement
    assert deserialized.classification == rec.classification


def test_repository_root_resolution():
    root = resolve_repository_root()
    assert root.exists()
    assert (root / "pyproject.toml").exists()


def test_rule1_downgrade_doc_silence():
    # If VERIFIED_ABSENCE is claimed based on doc silence without spec or valid repo path, engine degrades to NOT_FOUND...
    rec = EvidenceRecord(
        statement="Undocumented capability absence claim",
        evidence_type=EvidenceType.OFFICIAL_DOCUMENTATION,
        boundary=EvidenceBoundary.HERMES_AGENT_FRAMEWORK,
        source="plugins.md",
        classification=EvidenceClassification.VERIFIED_ABSENCE,
        justification="Feature is not mentioned in docs.",
        doc_ref="plugins.md"
    )
    engine = EvidenceValidationEngine()
    validated = engine.validate_record(rec)

    assert validated.classification == EvidenceClassification.NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION
    assert "[Rule Downgrade]" in validated.justification


def test_rule2_external_boundary_isolation():
    rec = EvidenceRecord(
        statement="External platform unverified behavior",
        evidence_type=EvidenceType.EXTERNAL_RUNTIME,
        boundary=EvidenceBoundary.EXTERNAL_PLATFORM,
        source="Unverified desktop runtime assumptions",
        classification=EvidenceClassification.VERIFIED,
        justification="Unproven external platform behavior."
    )
    engine = EvidenceValidationEngine()
    validated = engine.validate_record(rec)

    assert validated.classification == EvidenceClassification.UNVERIFIED


def test_rule3_repository_path_validation():
    engine = EvidenceValidationEngine()

    # Valid path
    valid_rec = EvidenceRecord(
        statement="Valid pyproject.toml reference",
        evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
        boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
        source="pyproject.toml entrypoint registration",
        classification=EvidenceClassification.VERIFIED,
        justification="Entrypoint is registered in pyproject.toml",
        repo_path="pyproject.toml"
    )
    assert engine.validate_record(valid_rec).classification == EvidenceClassification.VERIFIED

    # Invalid path raises EvidenceValidationError
    invalid_rec = EvidenceRecord(
        statement="Invalid path reference",
        evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
        boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
        source="nonexistent_file.py",
        classification=EvidenceClassification.VERIFIED,
        justification="Claims file exists.",
        repo_path="nonexistent_file.py"
    )
    with pytest.raises(EvidenceValidationError):
        engine.validate_record(invalid_rec)


def test_rule4_mandatory_non_empty_fields():
    engine = EvidenceValidationEngine()
    empty_stmt = EvidenceRecord(
        statement="",
        evidence_type=EvidenceType.OFFICIAL_DOCUMENTATION,
        boundary=EvidenceBoundary.HERMES_AGENT_FRAMEWORK,
        source="docs",
        classification=EvidenceClassification.UNVERIFIED,
        justification="justification"
    )
    with pytest.raises(EvidenceValidationError):
        engine.validate_record(empty_stmt)


def test_dual_format_report_generation():
    rec = EvidenceRecord(
        statement="PEP 427 wheel specification rule",
        evidence_type=EvidenceType.AUTHORITATIVE_SPECIFICATION,
        boundary=EvidenceBoundary.PYTHON_PACKAGING_SPEC,
        source="PEP 427",
        classification=EvidenceClassification.VERIFIED_ABSENCE,
        justification="Wheel standard rules out post-install script execution.",
        doc_ref="PEP 427"
    )
    generator = EvidenceReportGenerator()

    # Markdown table
    md = generator.render_markdown_table([rec])
    assert "| Statement | Evidence Type | Boundary | Source | Classification | Justification |" in md
    assert "PEP 427 wheel specification rule" in md
    assert "VERIFIED ABSENCE" in md

    # JSON manifest
    manifest_json = generator.render_json_manifest([rec])
    manifest_data = json.loads(manifest_json)
    assert manifest_data["schema_version"] == "v1.0"
    assert manifest_data["total_records"] == 1
    assert manifest_data["records"][0]["classification"] == "VERIFIED ABSENCE"
