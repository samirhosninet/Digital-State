"""ORCHESTRATION-001 Remediation Tests.

Verifies:
1. Builder execution gate blocks direct Builder tool invocation when Prime pre-orchestration or Spec Kit artifacts are missing.
2. Prime -> Builder approved workflow succeeds when Spec Kit prerequisite artifacts (spec.md, plan.md, tasks.md) exist and gates are approved.
"""

import json
import os
import shutil
import tempfile
import pytest
from pathlib import Path

from digital_state.bootstrap.installer import BootstrapInstaller
from digital_state.bootstrap.manager import RuntimeBootstrapManager
from digital_state.hermes.plugin import DigitalStatePlugin
from digital_state.sdk import validate_builder_execution_gate, validate_gate_approval


class DummyHermesContext:
    def __init__(self, workspace_root: Path):
        self.workspace_root = str(workspace_root)
        self.registered_skills = {}
        self.registered_hooks = {}
        self.registered_commands = {}

    def register_skill(self, name, path):
        self.registered_skills[name] = path

    def register_hook(self, name, handler):
        self.registered_hooks[name] = handler

    def register_command(self, name, handler):
        self.registered_commands[name] = handler


@pytest.fixture
def env_setup():
    tmp_dir = tempfile.mkdtemp(prefix="ds_orch_test_")
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

    ctx = DummyHermesContext(workspace_dir)
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


def test_builder_direct_invocation_without_spec_artifacts_is_blocked(env_setup):
    """Negative Test: Builder attempting direct execution without Prime pre-orchestration is blocked."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]

    builder_context = {
        "feature_id": "014-adapter-fix-verification",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    # Pre-orchestration is incomplete (spec.md, plan.md, tasks.md missing)
    res = plugin.pre_tool_call_handler("read_file", {"path": "main.py"}, builder_context)
    assert res["action"] == "block"
    assert "Builder execution gate blocked" in res["message"]


def test_builder_invocation_with_unapproved_prime_gates_is_blocked(env_setup):
    """Negative Test: Builder execution is blocked if Prime has not approved SPECIFICATION and PLANNING gates."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]

    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy artifact files, but gate validations in state.json remain unapproved
    (specify_dir / "spec.md").write_text("# Feature Spec", encoding="utf-8")
    (specify_dir / "plan.md").write_text("# Plan", encoding="utf-8")
    (specify_dir / "tasks.md").write_text("# Tasks", encoding="utf-8")

    state_file = specify_dir / "state.json"
    state_file.write_text(
        json.dumps({
            "feature_states": {"014-adapter-fix-verification": "SPECIFICATION"},
            "gate_validations": {"014-adapter-fix-verification": {"SPECIFICATION": False, "PLANNING": False}},
        }),
        encoding="utf-8",
    )

    builder_context = {
        "feature_id": "014-adapter-fix-verification",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    res = plugin.pre_tool_call_handler("read_file", {"path": "main.py"}, builder_context)
    assert res["action"] == "block"
    assert "Builder execution gate blocked" in res["message"]
    assert "Prime pre-orchestration incomplete" in res["message"]


def test_prime_to_builder_approved_workflow_succeeds(env_setup):
    """Positive Test: Approved Prime -> Builder workflow with artifacts & gate approvals succeeds."""
    workspace_dir = env_setup["workspace_dir"]
    plugin = env_setup["plugin"]

    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)

    # Prime creates required Spec Kit artifacts
    (specify_dir / "spec.md").write_text("# Feature Specification", encoding="utf-8")
    (specify_dir / "plan.md").write_text("# Implementation Plan", encoding="utf-8")
    (specify_dir / "tasks.md").write_text("# Task List", encoding="utf-8")
    (specify_dir / "analysis.md").write_text("# Consistency Analysis", encoding="utf-8")

    # Prime & Auditor approve SPECIFICATION, PLANNING, and TASKS gates
    state_file = specify_dir / "state.json"
    state_file.write_text(
        json.dumps({
            "feature_states": {"014-adapter-fix-verification": "IMPLEMENTATION"},
            "gate_validations": {
                "014-adapter-fix-verification": {
                    "SPECIFICATION": True,
                    "PLANNING": True,
                    "TASKS": True,
                }
            },
        }),
        encoding="utf-8",
    )

    builder_context = {
        "feature_id": "014-adapter-fix-verification",
        "agent_key": {"key_id": "key-builder", "role": "Builder", "tenant_id": "default_tenant"},
    }

    # Builder execution passes execution gate
    gate_passed, reason = validate_builder_execution_gate(
        "014-adapter-fix-verification", builder_context["agent_key"], workspace_root=str(workspace_dir)
    )
    assert gate_passed is True
    assert "passed" in reason.lower()
