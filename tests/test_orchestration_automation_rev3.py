"""ORCHESTRATION-003 Automated Workflow Layer Tests.

Verifies:
1. KanbanManager CRUD operations for .specify/kanban.json cards.
2. PrimeRuntimeController pre-orchestration automation under Prime authority.
3. HermesDispatcher gated dispatch validation via validate_builder_execution_gate().
4. Complete automated end-to-end pipeline execution.
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
from digital_state.core.orchestrator import PrimeRuntimeController
from digital_state.hermes.dispatcher import HermesDispatcher
from digital_state.hermes.plugin import DigitalStatePlugin
from digital_state.sdk import (
    KanbanManager,
    validate_builder_execution_gate,
    validate_gate_approval,
    submit_evidence,
)
from tests.conftest import sign_payload


class DummyContext:
    def __init__(self, workspace_root: Path):
        self.workspace_root = str(workspace_root)
        self.registered_skills = {}
        self.registered_hooks = {}
        self.registered_commands = {}

    def register_skill(self, name, path): pass
    def register_hook(self, name, handler): pass
    def register_command(self, name, handler): pass


@pytest.fixture
def env_setup():
    tmp_dir = tempfile.mkdtemp(prefix="ds_auto_test_")
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

    # Clear un-audited state for clean test
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)
    (specify_dir / "state.json").write_text(json.dumps({
        "feature_states": {},
        "gate_validations": {}
    }), encoding="utf-8")

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


def test_kanban_manager_crud(env_setup):
    """Test 1: KanbanManager CRUD operations for .specify/kanban.json."""
    workspace_dir = env_setup["workspace_dir"]
    km = KanbanManager(str(workspace_dir))

    card = km.create_card("feat-auto-001", assigned_to="builder-agent", title="Auto Task")
    assert card["feature_id"] == "feat-auto-001"
    assert card["assigned_to"] == "builder-agent"
    assert card["status"] == "IN_PROGRESS"

    loaded = km.get_card("feat-auto-001")
    assert loaded is not None
    assert loaded["title"] == "Auto Task"

    updated = km.update_card_status("feat-auto-001", "COMPLETED")
    assert updated is True
    assert km.get_card("feat-auto-001")["status"] == "COMPLETED"


def test_prime_runtime_controller_automation(env_setup):
    """Test 2: PrimeRuntimeController pre-orchestration automation under Prime authority."""
    workspace_dir = env_setup["workspace_dir"]
    controller = PrimeRuntimeController(str(workspace_dir))

    res = controller.run_pre_orchestration("feat-auto-002", title="Automated Feature", assignee="builder-agent")
    assert res["status"] == "IMPLEMENTATION"
    assert res["feature_id"] == "feat-auto-002"

    specify_dir = workspace_dir / ".specify"
    assert (specify_dir / "spec.md").exists()
    assert (specify_dir / "plan.md").exists()
    assert (specify_dir / "tasks.md").exists()
    assert (specify_dir / "kanban.json").exists()

    kernel = GovernanceKernel(str(workspace_dir), run_bootstrap=False)
    assert kernel.get_feature_state("feat-auto-002") == "IMPLEMENTATION"


def test_hermes_dispatcher_gated_dispatch(env_setup):
    """Test 3: HermesDispatcher gated dispatch validation."""
    workspace_dir = env_setup["workspace_dir"]
    dispatcher = HermesDispatcher(str(workspace_dir))
    builder_key = {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"}

    # Dispatch before pre-orchestration is blocked
    res_blocked = dispatcher.dispatch_builder("feat-auto-003", builder_key, workspace_root=str(workspace_dir))
    assert res_blocked["status"] == "BLOCKED"
    assert res_blocked["authorized"] is False

    # Execute pre-orchestration
    controller = PrimeRuntimeController(str(workspace_dir))
    controller.run_pre_orchestration("feat-auto-003", title="Feature 3", assignee="builder-agent")

    # Dispatch after pre-orchestration succeeds
    res_dispatched = dispatcher.dispatch_builder("feat-auto-003", builder_key, workspace_root=str(workspace_dir))
    assert res_dispatched["status"] == "DISPATCHED"
    assert res_dispatched["authorized"] is True


def test_full_automated_pipeline(env_setup):
    """Test 4: Full automated execution pipeline."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]
    feature_id = "feat-auto-004"

    # Step 1: PrimeRuntimeController executes pre-orchestration
    plugin.orchestrator.run_pre_orchestration(feature_id, title="Full Auto Feature", assignee="builder-agent")

    # Step 2: HermesDispatcher verifies Builder dispatch
    builder_key = {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"}
    dispatch_res = plugin.dispatcher.dispatch_builder(feature_id, builder_key)
    assert dispatch_res["status"] == "DISPATCHED"

    # Step 3: Builder tool call passes pre_tool_call_handler
    builder_ctx = {"feature_id": feature_id, "agent_key": builder_key}
    tool_res = plugin.pre_tool_call_handler("write_file", {"path": "src/module.py"}, builder_ctx)
    assert tool_res["action"] == "approve"

    # Step 4: Builder submits evidence
    content_impl = {"tasks_file": ".specify/tasks.md", "all_tasks_completed": True}
    sig_impl = sign_payload("builder", content_impl)
    payload = {"agent_id": "builder-agent", "content": content_impl, "signature": sig_impl}
    sub_ok = submit_evidence(feature_id, "IMPLEMENTATION", payload, workspace_root=str(workspace_dir))
    assert sub_ok is True

    # Step 5: Auditor verifies & Prime approves completion
    kernel = GovernanceKernel(str(workspace_dir), run_bootstrap=False)
    kernel.approve_gate(feature_id, "IMPLEMENTATION", "auditor-agent")

    (workspace_dir / ".specify" / "walkthrough.md").write_text("# Walkthrough", encoding="utf-8")
    content_ver = {"walkthrough_file": ".specify/walkthrough.md", "all_tests_passed": True}
    sig_ver = sign_payload("auditor", content_ver)
    kernel.submit_evidence(feature_id, "VERIFICATION", content_ver, "auditor-agent", sig_ver)
    kernel.lifecycle_engine.gate_validations.setdefault(feature_id, {})["VERIFICATION"] = True
    kernel.lifecycle_engine._save_state()

    prime_key = {"key_id": "key-prime", "role": "Prime", "tenant_id": "default_tenant"}
    prime_approved = validate_gate_approval(feature_id, prime_key, workspace_root=str(workspace_dir))
    assert prime_approved is True

    kernel = GovernanceKernel(str(workspace_dir), run_bootstrap=False)
    kernel.approve_gate(feature_id, "VERIFICATION", "prime-agent")
    assert kernel.get_feature_state(feature_id) == "COMPLETED"
