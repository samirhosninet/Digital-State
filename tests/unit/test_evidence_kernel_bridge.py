"""Unit Tests for Phase 1 Kernel Evidence Bridge (v1.13.0-platform).

Validates programmatic creation, engine rule enforcement via bridge,
and gate evidence satisfaction evaluation for WorkflowKernel.
"""

import json
import pytest
from digital_state.governance.evidence import (
    EvidenceType,
    EvidenceBoundary,
    EvidenceClassification,
    EvidenceRecord,
    KernelEvidenceBridge,
)


def test_kernel_bridge_create_and_validate():
    bridge = KernelEvidenceBridge()
    rec = bridge.create_and_validate_record(
        statement="Valid pyproject.toml registration",
        evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
        boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
        source="pyproject.toml entrypoint",
        classification=EvidenceClassification.VERIFIED,
        justification="Entrypoint is registered in pyproject.toml",
        repo_path="pyproject.toml"
    )
    assert rec.classification == EvidenceClassification.VERIFIED
    assert rec.statement == "Valid pyproject.toml registration"


def test_kernel_bridge_evaluate_gate_satisfied():
    bridge = KernelEvidenceBridge()
    rec1 = bridge.create_and_validate_record(
        statement="PyPA PEP 427 wheel specification rule",
        evidence_type=EvidenceType.AUTHORITATIVE_SPECIFICATION,
        boundary=EvidenceBoundary.PYTHON_PACKAGING_SPEC,
        source="PEP 427",
        classification=EvidenceClassification.VERIFIED_ABSENCE,
        justification="Wheel standard rules out post-install script execution.",
        doc_ref="PEP 427"
    )
    rec2 = bridge.create_and_validate_record(
        statement="CLI audit subcommand implemented",
        evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
        boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
        source="cli.py",
        classification=EvidenceClassification.VERIFIED,
        justification="audit-evidence subcommand is implemented in cli.py",
        repo_path="src/digital_state/cli/cli.py"
    )

    evaluation = bridge.evaluate_gate_evidence(
        gate_id="G3_IMPLEMENTATION_VERIFICATION",
        feature_id="v1.13.0-platform",
        evidence_records=[rec1, rec2]
    )

    assert evaluation["gate_id"] == "G3_IMPLEMENTATION_VERIFICATION"
    assert evaluation["feature_id"] == "v1.13.0-platform"
    assert evaluation["is_evidence_satisfied"] is True
    assert evaluation["total_records"] == 2
    assert evaluation["unverified_count"] == 0
    assert "manifest_json" in evaluation
    assert "report_markdown" in evaluation


def test_kernel_bridge_evaluate_gate_unsatisfied():
    bridge = KernelEvidenceBridge()
    # Record with doc silence degrades to NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION, making is_evidence_satisfied False
    rec_unverified = bridge.create_and_validate_record(
        statement="Undocumented capability absence claim",
        evidence_type=EvidenceType.OFFICIAL_DOCUMENTATION,
        boundary=EvidenceBoundary.HERMES_AGENT_FRAMEWORK,
        source="plugins.md",
        classification=EvidenceClassification.VERIFIED_ABSENCE,
        justification="Feature is not mentioned in docs.",
        doc_ref="plugins.md"
    )

    evaluation = bridge.evaluate_gate_evidence(
        gate_id="G3_IMPLEMENTATION_VERIFICATION",
        feature_id="v1.13.0-platform",
        evidence_records=[rec_unverified]
    )

    assert evaluation["is_evidence_satisfied"] is False
    assert evaluation["unverified_count"] == 1
    assert "Undocumented capability absence claim" in evaluation["unverified_statements"]
