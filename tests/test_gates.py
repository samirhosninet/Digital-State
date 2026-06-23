"""
Gate enforcement tests for Digital State.
These tests verify that the 5 mandatory gates are encoded in governance files.
"""
import os
import re
import yaml


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_evidence_gate():
    """Evidence Gate: No Auditor review without raw evidence from Builder."""
    content = _read(os.path.join(PROJECT_ROOT, "AGENTS.md"))
    assert "Evidence Gate" in content
    assert re.search(r"No Auditor review without raw evidence", content)


def test_implementation_gate():
    """Implementation Gate: No Builder implementation without explicit authorization."""
    content = _read(os.path.join(PROJECT_ROOT, "AGENTS.md"))
    assert "Implementation Gate" in content
    assert re.search(r"No Builder implementation without explicit.*authorization", content)


def test_audit_gate():
    """Audit Gate: No Done state without Auditor APPROVE backed by raw logs."""
    content = _read(os.path.join(PROJECT_ROOT, "AGENTS.md"))
    assert "Audit Gate" in content
    assert re.search(r"No Done state without Auditor APPROVE", content)


def test_risk_gate():
    """Risk Gate: No progress past triggered Premortem without mandatory status."""
    content = _read(os.path.join(PROJECT_ROOT, "AGENTS.md"))
    assert "Risk Gate" in content


def test_concurrency_cap_gate():
    """Concurrency Cap Gate: max_in_progress_per_profile must be 1 in all profiles."""
    for profile in ["prime", "builder", "auditor"]:
        config_path = os.path.join(PROJECT_ROOT, "profiles", profile, "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        kanban = config.get("kanban", {})
        assert kanban.get("max_in_progress_per_profile") == 1, \
            f"{profile}: kanban.max_in_progress_per_profile must be 1, got {kanban.get('max_in_progress_per_profile')}"


def test_role_separation():
    """Core operating rule: Builder produces, Auditor judges, Prime routes."""
    content = _read(os.path.join(PROJECT_ROOT, "AGENTS.md"))
    assert "Builder produces evidence" in content
    assert "Auditor judges evidence" in content
    assert "Prime routes decisions" in content


def test_no_legacy_profiles():
    """No legacy profiles: analyst, researcher, coder, tester must not exist."""
    for legacy in ["analyst", "researcher", "coder", "tester"]:
        legacy_path = os.path.join(PROJECT_ROOT, "profiles", legacy)
        assert not os.path.exists(legacy_path), f"Legacy profile still exists: {legacy}"


def test_constitution_articles():
    """Constitution must exist with Articles I-XV."""
    constitution_path = os.path.join(PROJECT_ROOT, "specs", "constitution.md")
    assert os.path.exists(constitution_path)
    content = _read(constitution_path)
    for art in ["Article I", "Article VIII", "Article IX", "Article XIII", "Article XIV", "Article XV"]:
        assert art in content, f"constitution.md missing {art}"
