"""Unit tests for tenant-scoped runtime context resolution (011-multi-tenant-key-server)."""

import os
from digital_state.runtime.adapter import resolve_governance_context
from digital_state.runtime.stores import IdentityRecord, IdentityStore
from digital_state.runtime.store import RuntimeStore


def test_resolve_governance_context_explicit_tenant(tmp_path):
    context = {
        "feature_id": "FEAT-TENANT-001",
        "tenant_id": "tenant-alpha",
        "agent_key": {
            "key_id": "key-001",
            "signature": "sig-001",
            "role": "builder",
            "public_key": {"key_id": "key-001"},
        },
    }
    feature_id, agent_key = resolve_governance_context(context, workspace_root=str(tmp_path))
    assert feature_id == "FEAT-TENANT-001"
    assert agent_key["tenant_id"] == "tenant-alpha"


def test_resolve_governance_context_env_tenant(monkeypatch, tmp_path):
    monkeypatch.setenv("DS_FEATURE_ID", "FEAT-ENV-001")
    monkeypatch.setenv("DS_TENANT_ID", "tenant-beta")
    monkeypatch.setenv(
        "DS_AGENT_KEY",
        '{"key_id": "key-002", "signature": "sig-002", "role": "builder", "public_key": {"key_id": "key-002"}}',
    )
    feature_id, agent_key = resolve_governance_context(workspace_root=str(tmp_path))
    assert feature_id == "FEAT-ENV-001"
    assert agent_key["tenant_id"] == "tenant-beta"


def test_resolve_governance_context_default_tenant_fallback(monkeypatch, tmp_path):
    monkeypatch.setenv("DS_FEATURE_ID", "FEAT-DEFAULT-001")
    monkeypatch.setenv(
        "DS_AGENT_KEY",
        '{"key_id": "key-003", "signature": "sig-003", "role": "builder", "public_key": {"key_id": "key-003"}}',
    )
    monkeypatch.delenv("DS_TENANT_ID", raising=False)
    feature_id, agent_key = resolve_governance_context(workspace_root=str(tmp_path))
    assert feature_id == "FEAT-DEFAULT-001"
    assert agent_key["tenant_id"] == "default_tenant"


def test_identity_store_tenant_filtering(tmp_path):
    store = IdentityStore(str(tmp_path))
    rec1 = IdentityRecord("id-1", "builder", {"key_id": "k1"}, tenant_id="tenant-alpha")
    rec2 = IdentityRecord("id-2", "auditor", {"key_id": "k2"}, tenant_id="tenant-beta")
    store.upsert(rec1)
    store.upsert(rec2)

    alpha_records = store.all_for_tenant("tenant-alpha")
    assert "id-1" in alpha_records
    assert "id-2" not in alpha_records

    beta_records = store.all_for_tenant("tenant-beta")
    assert "id-2" in beta_records
    assert "id-1" not in beta_records
