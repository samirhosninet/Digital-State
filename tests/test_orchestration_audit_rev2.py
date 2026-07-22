"""ORCHESTRATION-002 Complete Lifecycle Enforcement Audit Tests.

Required Test Matrix (8 Tests):
1. Direct Builder Invocation Test -> BLOCK
2. Builder Without Spec Test -> BLOCK
3. Builder Without Plan Test -> BLOCK
4. Builder Without Tasks Test -> BLOCK
5. Builder Without Assignment Test -> BLOCK
6. Builder With Complete Prime Authorization Test -> PASS
7. Completion Without Auditor Test -> BLOCK
8. Full Lifecycle Test (Prime -> SpecKit artifacts -> Kanban assignment -> Builder execution -> Evidence submission -> Auditor verification -> Prime approval -> COMPLETED) -> PASS
"""

import json
import os
import shutil
import tempfile
import pytest
from pathlib import Path

from digital_state.bootstrap.installer import BootstrapInstaller
from digital_state.bootstrap.manager import RuntimeBootstrapManager
from digital_state.core.engine import GovernanceKernel
from digital_state.hermes.plugin import DigitalStatePlugin
from digital_state.sdk import validate_builder_execution_gate, validate_gate_approval


class DummyContext:
    def __init__(self, workspace_root: Path):
        self.workspace_root = str(workspace_root)
        self.skills = {}
        self.hooks = {}
        self.commands = {}

    def register_skill(self, name, path): pass
    def register_hook(self, name, handler): pass
    def register_command(self, name, handler): pass


@pytest.fixture
def env_setup():
    tmp_dir = tempfile.mkdtemp(prefix="ds_orch002_")
    tmp_path = Path(tmp_dir)
    runtime_dir = tmp_path / "runtime_store"
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)

    old_ds_home = os.environ.get("DIGITAL_STATE_HOME")
    os.environ["DIGITAL_STATE_HOME"] = str(runtime_dir)

    installer = BootstrapInstaller(workspace_root=workspace_dir)
    installer.run_bootstrap()

    manager = RuntimeBootstrapManager(workspace_root=workspace_dir)
    manager.ensure_bootstrapped()

    ctx = DummyContext(workspace_dir)
    plugin = DigitalStatePlugin(ctx)
    plugin.initialize()

    yield {
        "tmp_dir": tmp_dir,
        "runtime_dir": runtime_dir,
        "workspace_dir": workspace_dir,
        "plugin": plugin,
    }

    if old_ds_home:
        os.environ["DIGITAL_STATE_HOME"] = old_ds_home
    else:
        os.environ.pop("DIGITAL_STATE_HOME", None)
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_1_direct_builder_invocation_is_blocked(env_setup):
    """Test 1: Direct Builder Invocation Test -> BLOCK."""
    plugin = env_setup["plugin"]
    builder_context = {
        "feature_id": "feat-001",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    res = plugin.pre_tool_call_handler("read_file", {"path": "main.py"}, builder_context)
    assert res["action"] == "block"
    assert "Builder execution gate blocked" in res["message"]


def test_2_builder_without_spec_is_blocked(env_setup):
    """Test 2: Builder Without Spec Test -> BLOCK."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    (specify_dir / "plan.md").write_text("# Plan", encoding="utf-8")
    (specify_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")

    state_file = specify_dir / "state.json"
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "SPECIFICATION"},
        "gate_validations": {"feat-001": {"assignments": {"feat-001": "builder-agent"}}},
    }), encoding="utf-8")

    builder_context = {
        "feature_id": "feat-001",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    res = plugin.pre_tool_call_handler("read_file", {"path": "main.py"}, builder_context)
    assert res["action"] == "block"
    assert "Builder execution gate blocked" in res["message"]


def test_3_builder_without_plan_is_blocked(env_setup):
    """Test 3: Builder Without Plan Test -> BLOCK."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    (specify_dir / "spec.md").write_text("# Spec", encoding="utf-8")
    (specify_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")

    state_file = specify_dir / "state.json"
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "PLANNING"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "assignments": {"feat-001": "builder-agent"}}},
    }), encoding="utf-8")

    builder_context = {
        "feature_id": "feat-001",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    res = plugin.pre_tool_call_handler("read_file", {"path": "main.py"}, builder_context)
    assert res["action"] == "block"
    assert "Builder execution gate blocked" in res["message"]


def test_4_builder_without_tasks_is_blocked(env_setup):
    """Test 4: Builder Without Tasks Test -> BLOCK."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    (specify_dir / "spec.md").write_text("# Spec", encoding="utf-8")
    (specify_dir / "plan.md").write_text("# Plan", encoding="utf-8")

    state_file = specify_dir / "state.json"
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "TASKS"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "PLANNING": True, "assignments": {"feat-001": "builder-agent"}}},
    }), encoding="utf-8")

    builder_context = {
        "feature_id": "feat-001",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    res = plugin.pre_tool_call_handler("read_file", {"path": "main.py"}, builder_context)
    assert res["action"] == "block"
    assert "Builder execution gate blocked" in res["message"]


def test_5_builder_without_assignment_is_blocked(env_setup):
    """Test 5: Builder Without Assignment Test -> BLOCK."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    (specify_dir / "spec.md").write_text("# Spec", encoding="utf-8")
    (specify_dir / "plan.md").write_text("# Plan", encoding="utf-8")
    (specify_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")

    state_file = specify_dir / "state.json"
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "IMPLEMENTATION"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "PLANNING": True, "TASKS": True}},
    }), encoding="utf-8")

    builder_context = {
        "feature_id": "feat-001",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    res = plugin.pre_tool_call_handler("read_file", {"path": "main.py"}, builder_context)
    assert res["action"] == "block"
    assert "Missing approved implementation assignment" in res["message"]


def test_6_builder_with_complete_prime_authorization_passes(env_setup):
    """Test 6: Builder With Complete Prime Authorization Test -> PASS."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    (specify_dir / "spec.md").write_text("# Spec", encoding="utf-8")
    (specify_dir / "plan.md").write_text("# Plan", encoding="utf-8")
    (specify_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")

    (specify_dir / "kanban.json").write_text(json.dumps({
        "cards": {"feat-001": {"assigned_to": "builder-agent", "status": "IN_PROGRESS"}}
    }), encoding="utf-8")

    state_file = specify_dir / "state.json"
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "IMPLEMENTATION"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "PLANNING": True, "TASKS": True}},
    }), encoding="utf-8")

    builder_context = {
        "feature_id": "feat-001",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    gate_passed, reason = validate_builder_execution_gate("feat-001", builder_context["agent_key"], workspace_root=str(workspace_dir))
    assert gate_passed is True
    assert "passed" in reason.lower()


def test_7_completion_without_auditor_is_blocked(env_setup):
    """Test 7: Completion Without Auditor Test -> BLOCK."""
    workspace_dir = env_setup["workspace_dir"]
    specify_dir = workspace_dir / ".specify"

    # State is at VERIFICATION phase, but Auditor has NOT verified gate (VERIFICATION: False)
    state_file = specify_dir / "state.json"
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "VERIFICATION"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "PLANNING": True, "TASKS": True, "IMPLEMENTATION": True, "VERIFICATION": False}},
    }), encoding="utf-8")

    prime_key = {"key_id": "key-prime", "role": "Prime", "tenant_id": "default_tenant"}

    # Prime attempts to close/approve completion without Auditor verification
    authorized = validate_gate_approval("feat-001", prime_key, workspace_root=str(workspace_dir))
    assert authorized is False


def test_8_full_lifecycle_pass(env_setup):
    """Test 8: Full Lifecycle Test -> PASS (Prime -> Spec -> Plan -> Tasks -> Kanban -> Builder -> Evidence -> Auditor -> Prime -> COMPLETED)."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Prime creates Spec Kit artifacts
    (specify_dir / "spec.md").write_text("# Spec", encoding="utf-8")
    (specify_dir / "plan.md").write_text("# Plan", encoding="utf-8")
    (specify_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")

    # Step 2: Prime creates Kanban assignment
    (specify_dir / "kanban.json").write_text(json.dumps({
        "cards": {"feat-001": {"assigned_to": "builder-agent", "status": "IN_PROGRESS"}}
    }), encoding="utf-8")

    # Step 3: Prime approves pre-orchestration gates and advances state to IMPLEMENTATION
    state_file = specify_dir / "state.json"
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "IMPLEMENTATION"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "PLANNING": True, "TASKS": True}},
    }), encoding="utf-8")

    builder_key = {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"}
    auditor_key = {"key_id": "key-auditor", "role": "Auditor", "tenant_id": "default_tenant"}
    prime_key = {"key_id": "key-prime", "role": "Prime", "tenant_id": "default_tenant"}

    # Step 4: Builder execution gate check
    gate_passed, reason = validate_builder_execution_gate("feat-001", builder_key, workspace_root=str(workspace_dir))
    assert gate_passed is True

    # Step 5: Builder finishes implementation and submits evidence -> State moves to VERIFICATION
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "VERIFICATION"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "PLANNING": True, "TASKS": True, "IMPLEMENTATION": True}},
    }), encoding="utf-8")

    # Step 6: Auditor validates implementation evidence -> VERIFICATION gate set to True
    state_file.write_text(json.dumps({
        "feature_states": {"feat-001": "VERIFICATION"},
        "gate_validations": {"feat-001": {"SPECIFICATION": True, "PLANNING": True, "TASKS": True, "IMPLEMENTATION": True, "VERIFICATION": True}},
    }), encoding="utf-8")

    # Step 7: Prime gives final completion approval -> Authorized
    authorized = validate_gate_approval("feat-001", prime_key, workspace_root=str(workspace_dir))
    assert authorized is True
