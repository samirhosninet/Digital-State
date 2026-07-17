"""Regression tests for Product Validation defects BUG-VAL-001 and BUG-VAL-002.

These lock in fixes that the proxy install surfaced: independent users could
not complete the governance workflow because (1) Runtime-provisioned identities
carry a capitalized role ("Auditor") that missed the lowercase roles.json keys
→ permissions=[], and (2) re-registering a seeded trust-root ID was rejected.
"""
import os
import json
import tempfile

import pytest

from digital_state.core.registry import AgentRegistry, Agent
from digital_state.core.exceptions import RegistryError


@pytest.mark.usefixtures("isolate_runtime_home")
def test_bug_val_001_role_case_normalization():
    """BUG-VAL-001: a capitalized role must resolve real permissions.

    AgentRegistry._permissions_for_role is the single lookup point used by both
    the workspace-seeded defaults and the Runtime-first get_agent() path. A
    capitalized role (as stored by Governance Provisioning) must NOT silently
    fall back to [].
    """
    # Lowercase key lookup (canonical).
    assert AgentRegistry._permissions_for_role("auditor") == [
        "approve_plan",
        "approve_tasks",
        "approve_spec",
        "veto_gate",
        "verify_evidence",
    ]
    # Capitalized role (as provisioned into the Runtime) must match.
    assert AgentRegistry._permissions_for_role("Auditor") == (
        AgentRegistry._permissions_for_role("auditor")
    )
    # Whitespace is tolerated.
    assert AgentRegistry._permissions_for_role("  Builder ") == (
        AgentRegistry._permissions_for_role("builder")
    )
    # Unknown role still safely returns [] (no exception).
    assert AgentRegistry._permissions_for_role("Nope") == []


@pytest.mark.usefixtures("isolate_runtime_home")
def test_bug_val_001_permissions_drives_policy():
    """BUG-VAL-001: a Runtime-seeded identity with a capitalized role must be
    authorized to approve, i.e. its resolved permissions are non-empty."""
    with tempfile.TemporaryDirectory() as tmpdir:
        reg_file = os.path.join(tmpdir, "agents.json")
        registry = AgentRegistry(reg_file)
        # Seed an identity the way the Runtime would (capitalized role).
        agent = Agent(
            agent_id="u-auditor",
            role="Auditor",
            permissions=registry._permissions_for_role("Auditor"),
        )
        assert agent.permissions, "Capitalized role must resolve non-empty permissions"
        assert "approve_spec" in agent.permissions


@pytest.mark.usefixtures("isolate_runtime_home")
def test_bug_val_002_force_overwrites_existing():
    """BUG-VAL-002: --force lets a user re-key a seeded trust-root ID."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    with tempfile.TemporaryDirectory() as tmpdir:
        reg_file = os.path.join(tmpdir, "agents.json")
        registry = AgentRegistry(reg_file)

        def _pub_pem(seed: int) -> dict:
            priv = ec.generate_private_key(ec.SECP256R1())
            pem = priv.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            ).decode()
            return {"key_id": f"key-{seed}", "status": "Active",
                    "algorithm": "ECDSA_P256", "value": pem}

        # Seeded default occupies the canonical ID.
        assert registry.agents.get("prime-agent") is not None
        before = registry.get_agent("prime-agent").public_key

        # Without --force the re-register is rejected.
        with pytest.raises(RegistryError):
            registry.register_agent(
                agent_id="prime-agent",
                role="Prime",
                permissions=["define_goals", "approve_spec", "approve_completed"],
                public_key=_pub_pem(1),
            )

        # With force=True the same ID is overwritten with the new keypair.
        new_key = _pub_pem(2)
        registry.register_agent(
            agent_id="prime-agent",
            role="Prime",
            permissions=["define_goals", "approve_spec", "approve_completed"],
            public_key=new_key,
            force=True,
        )
        after = registry.get_agent("prime-agent").public_key
        assert after["key_id"] == "key-2"
        assert after["value"] != None
