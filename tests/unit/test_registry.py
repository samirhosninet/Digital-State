import os
import tempfile
import pytest

from digital_state.core.registry import AgentRegistry
from digital_state.core.lifecycle import LifecycleEngine
from digital_state.core.exceptions import RegistryError


def test_agent_registry_initialization():
    """Verify that AgentRegistry correctly loads and registers agent roles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        reg_file = os.path.join(tmpdir, "agents.json")
        registry = AgentRegistry(reg_file)

        # Baseline profiles must be auto-populated
        prime = registry.get_agent("prime-agent")
        builder = registry.get_agent("builder-agent")
        auditor = registry.get_agent("auditor-agent")

        assert prime is not None and prime.role == "Prime"
        assert builder is not None and builder.role == "Builder"
        assert auditor is not None and auditor.role == "Auditor"

        # Test status updating
        registry.update_agent_status("builder-agent", "Suspended")
        assert registry.get_agent("builder-agent").status == "Suspended"

        # Check update validation
        with pytest.raises(RegistryError):
            registry.update_agent_status("unknown-agent", "Active")


def test_lifecycle_specification_defaults():
    """Verify that LifecycleEngine initializes features to SPECIFICATION state."""
    lifecycle = LifecycleEngine()
    state = lifecycle.get_state("feat-test-123")
    assert state == "SPECIFICATION"
