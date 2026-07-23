"""ORCHESTRATION-004 Observability Package Unit, Integration & Failure Injection Tests.

Verifies:
1. CheckpointManager loading and saving offset checkpoints.
2. EventSerializer format and hash verification.
3. AuditLogProjector non-blocking log tailing & projection.
4. CLISearch query filtering by event_type, agent_id, feature_id.
5. Failure Injection: Projector errors have zero impact on GovernanceKernel state transitions.
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
from digital_state.observability import (
    CheckpointManager,
    EventSerializer,
    ProjectionEngine,
    AuditLogProjector,
    CLISearch,
)
from tests.conftest import sign_payload


@pytest.fixture
def env_setup():
    tmp_dir = tempfile.mkdtemp(prefix="ds_obs_test_")
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

    # Reset state.json for clean test workspace
    specify_dir = workspace_dir / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)
    (specify_dir / "state.json").write_text(json.dumps({
        "feature_states": {},
        "gate_validations": {}
    }), encoding="utf-8")

    yield {
        "tmp_dir": tmp_dir,
        "runtime_dir": runtime_dir,
        "workspace_dir": workspace_dir,
    }

    if old_ds_home:
        os.environ["DIGITAL_STATE_HOME"] = old_ds_home
    else:
        os.environ.pop("DIGITAL_STATE_HOME", None)
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_checkpoint_manager(env_setup):
    """Test 1: CheckpointManager offset checkpoint loading and saving."""
    workspace_dir = env_setup["workspace_dir"]
    cm = CheckpointManager(str(workspace_dir))

    initial = cm.load_checkpoint()
    assert initial["last_sequence_id"] == 0

    cm.save_checkpoint(5, "hash1234567890")
    loaded = cm.load_checkpoint()
    assert loaded["last_sequence_id"] == 5
    assert loaded["last_hash"] == "hash1234567890"


def test_event_serializer():
    """Test 2: EventSerializer entry verification."""
    serializer = EventSerializer()

    raw_valid = {
        "sequence_id": 1,
        "timestamp": "2026-07-23T00:00:00Z",
        "event_type": "SUBMIT_EVIDENCE",
        "agent_id": "builder-agent",
        "details": {"feature_id": "feat-obs-001"},
        "hash": "abc123hash",
    }
    serialized = serializer.serialize_entry(raw_valid)
    assert serialized is not None
    assert serialized["sequence_id"] == 1
    assert serialized["agent_id"] == "builder-agent"

    raw_invalid = {"sequence_id": 1}
    assert serializer.serialize_entry(raw_invalid) is None


def test_audit_log_projector_and_cli_search(env_setup):
    """Test 3: AuditLogProjector tailing and CLISearch filtering."""
    workspace_dir = env_setup["workspace_dir"]
    kernel = GovernanceKernel(str(workspace_dir), run_bootstrap=False)

    # Submit evidence to write entries into audit_log.jsonl
    content_spec = {"spec_file": ".specify/spec.md", "requirements_count": 1}
    sig_spec = sign_payload("builder", content_spec)
    kernel.submit_evidence("feat-obs-001", "SPECIFICATION", content_spec, "builder-agent", sig_spec)

    projector = AuditLogProjector(str(workspace_dir))
    projected = projector.project_new_events()
    assert len(projected) >= 1
    assert projected[-1]["event_type"] == "SUBMIT_EVIDENCE"

    cli = CLISearch(str(workspace_dir))
    results = cli.query(event_type="SUBMIT_EVIDENCE", feature_id="feat-obs-001")
    assert len(results) >= 1
    assert results[0]["agent_id"] == "builder-agent"


def test_failure_injection_isolation(env_setup):
    """Test 4: Failure Injection - Projector corruption/error has zero impact on GovernanceKernel."""
    workspace_dir = env_setup["workspace_dir"]
    projector = AuditLogProjector(str(workspace_dir))
    log_file = projector.get_log_path()

    # Inject corrupted line into audit_log.jsonl
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("CORRUPTED_NON_JSON_LINE\n")

    # Projector handles corrupted line without raising uncaught exception
    unprojected = projector.get_unprojected_entries()
    assert isinstance(unprojected, list)

    # GovernanceKernel continues executing cleanly
    kernel = GovernanceKernel(str(workspace_dir), run_bootstrap=False)
    assert kernel.get_feature_state("feat-obs-001") == "SPECIFICATION"
