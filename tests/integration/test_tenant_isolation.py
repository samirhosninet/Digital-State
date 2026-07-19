"""Integration tests for multi-tenant key server authentication and tenant isolation (011-multi-tenant-key-server)."""

import os
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
    store = RuntimeStore(str(tmp_path))
    store.provision()
    rec_a = IdentityRecord(
        identity_id="builder-agent-a",
        role="builder",
        public_key={"key_id": "key-a", "algorithm": "ECDSA_P256", "value": "pub-key-a"},
        tenant_id="tenant-alpha",
    )
    store.identity.upsert(rec_a)

    monkeypatch.setenv("HERMES_WORKSPACE", str(tmp_path))
    monkeypatch.setenv("DS_FEATURE_ID", "FEAT-TENANT-ISO")
    monkeypatch.setenv("DS_TENANT_ID", "tenant-alpha")

    feature_id, agent_key = resolve_governance_context(workspace_root=str(tmp_path))
    assert feature_id == "FEAT-TENANT-ISO"
    assert agent_key["tenant_id"] == "tenant-alpha"
    assert agent_key["key_id"] == "key-a"
