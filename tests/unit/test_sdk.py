import os
import tempfile
import pytest
from digital_state.sdk import (
    is_compatible,
    validate_gate_approval,
    check_governance_status,
    verify_audit_log,
)

def test_sdk_version_compatibility():
    """Verify SDK version checks function correctly."""
    assert is_compatible("0.1.0") is True
    assert is_compatible("0.1.5") is True
    assert is_compatible("0.2.0") is False
    assert is_compatible("") is False

def test_sdk_status_query():
    """Verify check_governance_status handles clean states."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        
        status = check_governance_status("feature-001", workspace_root=tmpdir)
        assert status["feature_id"] == "feature-001"
        assert status["status"] == "SPECIFICATION"
