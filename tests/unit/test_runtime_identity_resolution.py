"""SPEC-012 SECOND REMEDIATION — authority-divergence test (Auditor CRITICAL-01/03).

This replaces the previous regression tests. It proves the locked-baseline
invariant required by the auditor's CRITICAL-03 scenario:

    Runtime:   identity_id = X   public_key = A
    Workspace: identity_id = X   public_key = B

Assertions:
    registry.get_agent(X).public_key == A
    registry.get_agent(X).public_key != B
    Signature(A-private) -> PASS
    Signature(B-private) -> FAIL

No ADR/IA changes. No production commit/push.
"""

import os
import json
import base64
import tempfile

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from digital_state.core.registry import AgentRegistry
from digital_state.runtime.store import RuntimeStore
from digital_state.runtime.stores import IdentityRecord
from digital_state.runtime.provision import bootstrap_runtime
from digital_state.core.verifier import CryptoVerifier


@pytest.fixture(autouse=True)
def isolated_runtime(monkeypatch, tmp_path):
    """Point the Runtime at an isolated temp dir so the proof is independent."""
    rt = tmp_path / "runtime"
    rt.mkdir()
    monkeypatch.setenv("DIGITAL_STATE_HOME", str(rt))
    yield rt


def _key_pair():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub_pem = priv.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return priv, pub_pem


def _pub_dict(value: str, key_id: str) -> dict:
    return {
        "key_id": key_id,
        "status": "Active",
        "algorithm": "ECDSA_P256",
        "value": value,
    }


def _workspace_file() -> str:
    d = tempfile.mkdtemp(prefix="ds_ws_")
    return os.path.join(d, "agents.json")


def test_runtime_authority_divergence():
    """CRITICAL-01/03: Runtime identity X (key A) must win over the same-id
    workspace identity X (key B)."""
    # bootstrap_runtime() with no arg uses DIGITAL_STATE_HOME from the fixture.
    store = bootstrap_runtime()

    # Runtime: identity X -> public key A
    rt_priv, rt_pub = _key_pair()
    store.identity.upsert(
        IdentityRecord(
            identity_id="X",
            role="Prime",
            public_key=_pub_dict(rt_pub, "key-rt-A"),
        )
    )

    # Workspace: identity X -> public key B (divergent)
    ws_file = _workspace_file()
    ws_priv, ws_pub = _key_pair()
    with open(ws_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "X": {
                    "agent_id": "X",
                    "role": "Prime",
                    "permissions": ["define_goals"],
                    "status": "Active",
                    "public_key": _pub_dict(ws_pub, "key-ws-B"),
                }
            },
            f,
        )

    reg = AgentRegistry(ws_file)
    agent = reg.get_agent("X")

    # Assertions required by the auditor.
    assert agent is not None
    assert agent.public_key["value"].strip() == rt_pub.strip()   # == A
    assert agent.public_key["value"].strip() != ws_pub.strip()   # != B

    # CRITICAL-02: signature authority follows the engine-resolved (A) key.
    payload = {"spec": "spec-012", "identity_id": "X"}
    sig_a = base64.b64encode(
        rt_priv.sign(
            json.dumps(payload, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256())
        )
    ).decode()
    sig_b = base64.b64encode(
        ws_priv.sign(
            json.dumps(payload, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256())
        )
    ).decode()

    # Signature(A-private) must verify against the resolved identity.
    assert CryptoVerifier.verify(agent.public_key, payload, sig_a) is True

    # Signature(B-private) must NOT verify — B has no effective authority.
    with pytest.raises(Exception):
        CryptoVerifier.verify(agent.public_key, payload, sig_b)


def test_workspace_fallback_only_when_runtime_absent(tmp_path):
    """Sanity: when the Runtime has no entry for X, the workspace entry is used
    (legacy fallback), proving the workspace path is still reachable but only as
    a secondary source."""
    ws_file = _workspace_file()
    ws_priv, ws_pub = _key_pair()
    with open(ws_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "X": {
                    "agent_id": "X",
                    "role": "Prime",
                    "permissions": ["define_goals"],
                    "status": "Active",
                    "public_key": _pub_dict(ws_pub, "key-ws-B"),
                }
            },
            f,
        )

    reg = AgentRegistry(ws_file)
    agent = reg.get_agent("X")
    assert agent is not None
    assert agent.public_key["value"].strip() == ws_pub.strip()

    # And when X exists nowhere, resolution is None.
    assert reg.get_agent("nonexistent") is None
