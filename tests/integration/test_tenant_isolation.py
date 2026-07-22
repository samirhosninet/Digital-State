"""Integration tests for multi-tenant key server authentication and tenant isolation (011-multi-tenant-key-server)."""

import os
import json
from digital_state.runtime.store import RuntimeStore
from digital_state.runtime.stores import IdentityRecord
from digital_state.runtime.adapter import resolve_governance_context


def test_tenant_key_isolation_in_runtime_store(tmp_path):
    store = RuntimeStore(str(tmp_path))
    store.provision()

    # Register identities for Tenant A and Tenant B
    rec_a = IdentityRecord(
        identity_id="builder-agent-a",
        role="builder",
        public_key={"key_id": "key-a", "algorithm": "ECDSA_P256", "value": "pub-key-a"},
        tenant_id="tenant-alpha",
    )
    rec_b = IdentityRecord(
        identity_id="builder-agent-b",
        role="builder",
        public_key={"key_id": "key-b", "algorithm": "ECDSA_P256", "value": "pub-key-b"},
        tenant_id="tenant-beta",
    )
    store.identity.upsert(rec_a)
    store.identity.upsert(rec_b)

    # Query Tenant A records
    tenant_a_records = store.identity.all_for_tenant("tenant-alpha")
    assert "builder-agent-a" in tenant_a_records
    assert "builder-agent-b" not in tenant_a_records
    assert tenant_a_records["builder-agent-a"].public_key["value"] == "pub-key-a"

    # Query Tenant B records
    tenant_b_records = store.identity.all_for_tenant("tenant-beta")
    assert "builder-agent-b" in tenant_b_records
    assert "builder-agent-a" not in tenant_b_records
    assert tenant_b_records["builder-agent-b"].public_key["value"] == "pub-key-b"


def test_tenant_context_resolution_isolation(monkeypatch, tmp_path):
    # ARCHITECTURAL CONTRACT (DS-GOV-BOOTSTRAP-001 / ADR-011-01 / ADR-011-04):
    # Workspace Context (ws_root) and Runtime Context (resolve_runtime_root) are
    # INDEPENDENT roots. The adapter must resolve the agent identity from the
    # authoritative Runtime at DIGITAL_STATE_HOME, NOT from the workspace root.
    #
    # The conftest.py isolate_runtime_home autouse fixture points DIGITAL_STATE_HOME
    # at tmp_path/ds-runtime — a path DISTINCT from the workspace below. We
    # provision the authoritative Runtime there so the test asserts the real
    # separation instead of masking the coupling defect.
    rt_root = os.environ.get("DIGITAL_STATE_HOME")
    assert rt_root and rt_root != str(tmp_path), "Runtime root must be independent of workspace root"

    store = RuntimeStore(rt_root)
    store.provision()
    rec_a = IdentityRecord(
        identity_id="builder-agent-a",
        role="builder",
        public_key={"key_id": "key-a", "algorithm": "ECDSA_P256", "value": "pub-key-a"},
        tenant_id="tenant-alpha",
    )
    store.identity.upsert(rec_a)

    # Workspace is a SEPARATE path, holding a schema-valid .specify/state.json.
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    specify = workspace / ".specify"
    specify.mkdir()
    (specify / "state.json").write_text(
        json.dumps({
            "feature_states": {"feat-iso-001": "SPECIFICATION"},
            "gate_validations": {},
        }),
        encoding="utf-8",
    )

    monkeypatch.setenv("HERMES_WORKSPACE", str(workspace))
    monkeypatch.setenv("DS_TENANT_ID", "tenant-alpha")
    # No DS_FEATURE_ID/DS_AGENT_KEY -> feature_id from Workspace Tier 3a,
    # agent_key from Runtime Tier 3b (authoritative Runtime at DIGITAL_STATE_HOME).

    feature_id, agent_key = resolve_governance_context(workspace_root=str(workspace))
    # Workspace Context -> feature_id resolved from .specify/state.json schema.
    assert feature_id == "feat-iso-001"
    # Runtime Context -> agent_key resolved from authoritative Runtime (independent root).
    assert agent_key["tenant_id"] == "tenant-alpha"
    assert agent_key["key_id"] == "key-a"
