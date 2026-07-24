"""Automated Unit Test Suite for Prime Operating Model Specification Artifacts (v2.0).

Verifies presence, structure, and link integrity for all mandatory Prime Operating Model
documentation files, specifications, state machines, and ADR-005.
"""

from pathlib import Path
import pytest


WORKSPACE_ROOT = Path(__file__).parent.parent


def test_prime_operating_model_documents_exist():
    """Verify all 10 Prime Operating Model artifacts exist in the repository."""
    required_files = [
        WORKSPACE_ROOT / "docs" / "PRIME_OPERATING_MODEL.md",
        WORKSPACE_ROOT / "docs" / "WORKFLOW_SPECIFICATION.md",
        WORKSPACE_ROOT / "docs" / "PLANNING_ENGINE_SPECIFICATION.md",
        WORKSPACE_ROOT / "docs" / "LIFECYCLE_STATE_MACHINE.md",
        WORKSPACE_ROOT / "docs" / "FAILURE_AND_RECOVERY_POLICY.md",
        WORKSPACE_ROOT / "docs" / "TASK_GRAPH_AND_KANBAN_SPECIFICATION.md",
        WORKSPACE_ROOT / "docs" / "AGENT_DISPATCH_AND_VERIFICATION_RULES.md",
        WORKSPACE_ROOT / "docs" / "REPOSITORY_CONVENTION_RULES.md",
        WORKSPACE_ROOT / "governance" / "self-governance" / "015-prime-operating-model" / "ADR-005-prime-operating-model.md",
        WORKSPACE_ROOT / "README.md",
    ]
    for path in required_files:
        assert path.exists(), f"Missing required Prime Operating Model artifact: {path}"
        assert path.stat().st_size > 100, f"Artifact is empty or incomplete: {path}"


def test_prime_operating_model_readme_integration():
    """Verify README.md contains links to all Prime Operating Model specifications."""
    readme_path = WORKSPACE_ROOT / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    assert "Prime Operating Model Architecture (v2.0)" in content
    assert "docs/PRIME_OPERATING_MODEL.md" in content
    assert "docs/WORKFLOW_SPECIFICATION.md" in content
    assert "docs/PLANNING_ENGINE_SPECIFICATION.md" in content
    assert "docs/LIFECYCLE_STATE_MACHINE.md" in content
    assert "docs/FAILURE_AND_RECOVERY_POLICY.md" in content
    assert "docs/TASK_GRAPH_AND_KANBAN_SPECIFICATION.md" in content
    assert "docs/AGENT_DISPATCH_AND_VERIFICATION_RULES.md" in content
    assert "docs/REPOSITORY_CONVENTION_RULES.md" in content
    assert "ADR-005" in content


def test_adr_005_structure():
    """Verify ADR-005 adheres to standard architecture decision record format."""
    adr_path = WORKSPACE_ROOT / "governance" / "self-governance" / "015-prime-operating-model" / "ADR-005-prime-operating-model.md"
    content = adr_path.read_text(encoding="utf-8")

    assert "ADR-005: PRIME OPERATING MODEL ARCHITECTURE" in content
    assert "ACCEPTED" in content
    assert "Context and Problem Statement" in content
    assert "Decision Outcome" in content
    assert "Consequences" in content
