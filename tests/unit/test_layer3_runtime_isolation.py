"""Unit Tests for Layer 3 Runtime Isolation Boundaries (ECR-002).

Asserts that Layer 3 core packages (core, device, hermes) contain
zero installation or Hermes provisioner dependencies.
"""

import sys
import pytest
import importlib
from pathlib import Path


def test_layer3_runtime_has_no_bootstrap_engine_imports():
    """Verify Layer 3 core modules do not import Layer 2 bootstrap engine components."""
    layer3_modules = [
        "digital_state.core.engine",
        "digital_state.core.audit",
        "digital_state.core.contracts",
        "digital_state.device.keystore",
        "digital_state.device.evidence",
        "digital_state.device.policy_engine",
        "digital_state.hermes.plugin",
    ]

    for mod_name in layer3_modules:
        mod = importlib.import_module(mod_name)
        assert mod is not None
        # Assert module file does not contain bootstrap engine references
        mod_file = getattr(mod, "__file__", "")
        if mod_file and mod_file.endswith(".py"):
            with open(mod_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "from digital_state.bootstrap.engine" not in content
                assert "import digital_state.bootstrap.engine" not in content


def test_layer3_governance_kernel_runs_without_installation_code(tmp_path):
    """Verify GovernanceKernel instantiates cleanly without triggering installation logic."""
    from digital_state.core.engine import GovernanceKernel

    specify_dir = tmp_path / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    kernel = GovernanceKernel(workspace_root=str(tmp_path), run_bootstrap=False)
    assert kernel is not None
    assert str(kernel.workspace_root) == str(tmp_path)
