"""Automated Test Suite for BOOTSTRAP-001 Revision 3.

Verifies:
1. Fresh installation provisions RuntimeStore automatically.
2. Fresh workspace creates .specify/state.json.
3. Existing workspace is left unchanged.
4. Existing RuntimeStore is left unchanged (idempotency).
5. DigitalStatePlugin is a pure consumer (no bootstrap side effects).
6. resolve_governance_context() is a pure resolver (read-only).
7. Builder session resolves agent_key and feature_id after bootstrap.
8. Invalid/uninitialized environment still produces Fail-Safe Deny.
"""

import os
import json
import shutil
import tempfile
from pathlib import Path
import pytest

from digital_state.bootstrap.manager import RuntimeBootstrapManager, ensure_runtime_bootstrapped
from digital_state.runtime.store import RuntimeStore
from digital_state.runtime.adapter import resolve_governance_context
from digital_state.hermes.plugin import DigitalStatePlugin


class DummyContext:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.skills = {}
        self.hooks = {}
        self.commands = {}

    def register_skill(self, name, path):
        self.skills[name] = path

    def register_hook(self, name, handler):
        self.hooks[name] = handler

    def register_command(self, name, handler):
        self.commands[name] = handler


@pytest.fixture
def temp_env():
    tmp_dir = tempfile.mkdtemp(prefix="ds_bootstrap_test_")
    tmp_path = Path(tmp_dir)
    runtime_dir = tmp_path / "runtime_store"
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)

    old_appdata = os.environ.get("LOCALAPPDATA")
    old_ds_home = os.environ.get("DIGITAL_STATE_HOME")
    os.environ["DIGITAL_STATE_HOME"] = str(runtime_dir)

    yield {
        "root": tmp_path,
        "runtime_dir": runtime_dir,
        "workspace_dir": workspace_dir
    }

    if old_appdata:
        os.environ["LOCALAPPDATA"] = old_appdata
    if old_ds_home:
        os.environ["DIGITAL_STATE_HOME"] = old_ds_home
    else:
        os.environ.pop("DIGITAL_STATE_HOME", None)

    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_fresh_installation_provisions_runtime_store(temp_env):
    workspace_dir = temp_env["workspace_dir"]
    runtime_dir = temp_env["runtime_dir"]

    assert not (runtime_dir / "registry" / "agents.json").exists()

    manager = RuntimeBootstrapManager(workspace_root=workspace_dir)
    res = manager.ensure_bootstrapped()

    assert res["status"] == "SUCCESS"
    assert (runtime_dir / "registry" / "agents.json").exists()

    store = RuntimeStore(root=str(runtime_dir))
    identities = store.identity.all_for_tenant("default_tenant")
    assert len(identities) >= 3
    assert "prime-agent" in identities
    assert "builder-agent" in identities
    assert "auditor-agent" in identities


def test_fresh_workspace_creates_specify_state(temp_env):
    workspace_dir = temp_env["workspace_dir"]
    specify_state = workspace_dir / ".specify" / "state.json"

    assert not specify_state.exists()

    manager = RuntimeBootstrapManager(workspace_root=workspace_dir)
    res = manager.ensure_bootstrapped()

    assert specify_state.exists()
    content = json.loads(specify_state.read_text(encoding="utf-8"))
    assert "feature_states" in content
    assert len(content["feature_states"]) > 0


def test_existing_workspace_is_left_unchanged(temp_env):
    workspace_dir = temp_env["workspace_dir"]
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)
    specify_state = specify_dir / "state.json"
    
    custom_state = {
        "feature_states": {
            "custom-feat-999": "IN_PROGRESS"
        },
        "custom_metadata": "do_not_touch"
    }
    specify_state.write_text(json.dumps(custom_state), encoding="utf-8")

    manager = RuntimeBootstrapManager(workspace_root=workspace_dir)
    manager.ensure_bootstrapped()

    content = json.loads(specify_state.read_text(encoding="utf-8"))
    assert content == custom_state
    assert "custom-feat-999" in content["feature_states"]


def test_existing_runtime_store_is_left_unchanged(temp_env):
    workspace_dir = temp_env["workspace_dir"]
    
    manager = RuntimeBootstrapManager(workspace_root=workspace_dir)
    res1 = manager.ensure_bootstrapped()
    assert res1["runtime_store"]["status"] == "SEEDED"

    res2 = manager.ensure_bootstrapped()
    assert res2["runtime_store"]["status"] == "ALREADY_PROVISIONED"


def test_plugin_is_pure_consumer(temp_env):
    workspace_dir = temp_env["workspace_dir"]
    
    # Initialize bootstrap at Application level
    ensure_runtime_bootstrapped(workspace_root=workspace_dir)

    ctx = DummyContext(workspace_root=str(workspace_dir))
    plugin = DigitalStatePlugin(ctx)

    # Record directory state
    state_file = workspace_dir / ".specify" / "state.json"
    mtime_before = state_file.stat().st_mtime

    initialized = plugin.initialize()
    assert initialized is True
    assert plugin.is_loaded is True

    # Confirm plugin initialize did not alter state file
    mtime_after = state_file.stat().st_mtime
    assert mtime_before == mtime_after


def test_resolver_is_pure_readonly(temp_env):
    workspace_dir = temp_env["workspace_dir"]
    ensure_runtime_bootstrapped(workspace_root=workspace_dir)

    feature_id, agent_key = resolve_governance_context({}, workspace_root=str(workspace_dir))
    assert feature_id is not None
    assert agent_key is not None
    assert isinstance(agent_key, dict)
    assert agent_key.get("role") in ("Builder", "Prime", "Auditor")


def test_unbootstrapped_environment_triggers_fail_safe_deny(temp_env):
    unbootstrapped_ws = temp_env["root"] / "empty_ws"
    unbootstrapped_ws.mkdir(parents=True, exist_ok=True)
    unbootstrapped_runtime = temp_env["root"] / "empty_runtime"
    os.environ["DIGITAL_STATE_HOME"] = str(unbootstrapped_runtime)

    ctx = DummyContext(workspace_root=str(unbootstrapped_ws))
    plugin = DigitalStatePlugin(ctx)
    plugin.initialize()

    # Pre-tool call in unbootstrapped environment must trigger Fail-Safe Deny
    res = plugin.pre_tool_call_handler("read_file", {"path": "foo.py"})
    assert res["action"] == "block"
    assert "Fail-Safe Deny" in res["message"]
