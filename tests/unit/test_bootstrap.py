import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from digital_state.core.bootstrap import BootstrapValidator
from digital_state.core.exceptions import GovernanceError


def test_bootstrap_validator_success():
    """Verify bootstrap process succeeds under fully valid environment mocks."""
    validator = BootstrapValidator(workspace_root="/mock/root")

    with patch.object(validator, "verify_workspace_readiness", return_value=True), \
         patch.object(validator, "verify_hermes_availability", return_value=True), \
         patch.object(validator, "verify_speckit_availability", return_value=True), \
         patch.object(validator, "verify_runtime_adapter_readiness", return_value=True):
        
        # Must execute without raising error
        validator.run_bootstrap()


def test_bootstrap_validator_failures():
    """Verify bootstrap validator aborts early with GovernanceError if checks fail."""
    validator = BootstrapValidator(workspace_root="/mock/root")

    # 1. Fail Workspace
    with patch.object(validator, "verify_workspace_readiness", return_value=False):
        with pytest.raises(GovernanceError) as exc:
            validator.run_bootstrap()
        assert "Workspace not initialized" in str(exc.value)

    # 2. Fail Hermes
    with patch.object(validator, "verify_workspace_readiness", return_value=True), \
         patch.object(validator, "verify_hermes_availability", return_value=False):
        with pytest.raises(GovernanceError) as exc:
            validator.run_bootstrap()
        assert "Hermes Agent runtime is unavailable" in str(exc.value)

    # 3. Fail SpecKit
    with patch.object(validator, "verify_workspace_readiness", return_value=True), \
         patch.object(validator, "verify_hermes_availability", return_value=True), \
         patch.object(validator, "verify_speckit_availability", return_value=False):
        with pytest.raises(GovernanceError) as exc:
            validator.run_bootstrap()
        assert "SpecKit CLI execution path not found" in str(exc.value)

    # 4. Fail Adapter
    with patch.object(validator, "verify_workspace_readiness", return_value=True), \
         patch.object(validator, "verify_hermes_availability", return_value=True), \
         patch.object(validator, "verify_speckit_availability", return_value=True), \
         patch.object(validator, "verify_runtime_adapter_readiness", return_value=False):
        with pytest.raises(GovernanceError) as exc:
            validator.run_bootstrap()
        assert "Hermes runtime adapter initialization failed" in str(exc.value)
