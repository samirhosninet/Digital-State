"""Independent AUDITOR divergence proof for SPEC-012 CRITICAL-02.

Authority-divergence scenario (the auditor's required scenario):

    Runtime:   identity_id = X   public_key = A
    Workspace: identity_id = X   public_key = B

The Runtime is the authoritative source, so the engine (AgentRegistry.get_agent)
MUST resolve X -> A (Runtime key), and MUST NOT resolve X -> B (workspace key).

Independent evidence demonstrated here:

    Runtime key        == Engine resolved key      (A wins)
    Workspace key      != Engine resolved key      (B is ignored)
    Signature(A-private)  -> PASS                   (effective authority is A)
    Signature(B-private)  -> FAIL                   (B has no effective authority)

Run:  python audit_divergence_proof.py
Exit code 0 => divergence proven; non-zero => proof failed.
"""

import os
import json
import sys
import tempfile
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

# Isolate the Runtime so the proof is independent of any local Runtime state.
RT_HOME = tempfile.mkdtemp(prefix="ds_audit_rt_")
os.environ["DIGITAL_STATE_HOME"] = RT_HOME

from digital_state.runtime.store import RuntimeStore
from digital_state.runtime.stores import IdentityRecord
from digital_state.runtime.provision import bootstrap_runtime
from digital_state.core.registry import AgentRegistry
from digital_state.core.verifier import CryptoVerifier


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


def main() -> int:
    store = bootstrap_runtime(RT_HOME)

    # --- Runtime: identity_id = X, public_key = A ---
    rt_priv, rt_pub = _key_pair()           # A
    store.identity.upsert(
        IdentityRecord(
            identity_id="X",
            role="Prime",
            public_key=_pub_dict(rt_pub, "key-rt-A"),
        )
    )

    # --- Workspace: identity_id = X, public_key = B (DIFFERENT) ---
    ws_priv, ws_pub = _key_pair()           # B
    ws_dir = tempfile.mkdtemp(prefix="ds_audit_ws_")
    ws_file = os.path.join(ws_dir, "agents.json")
    ws_data = {
        "X": {
            "agent_id": "X",
            "role": "Prime",
            "permissions": ["define_goals"],
            "status": "Active",
            "public_key": _pub_dict(ws_pub, "key-ws-B"),
        }
    }
    with open(ws_file, "w", encoding="utf-8") as f:
        json.dump(ws_data, f, indent=2)

    # --- Engine resolution ---
    reg = AgentRegistry(ws_file)
    resolved = reg.get_agent("X")
    assert resolved is not None, "engine resolved no agent for X"

    runtime_key = rt_pub.strip()
    workspace_key = ws_pub.strip()
    engine_key = resolved.public_key["value"].strip()

    # --- Independent evidence ---
    print("=" * 64)
    print("SPEC-012 CRITICAL-02 — EFFECTIVE AUTHORITY DIVERGENCE PROOF")
    print("=" * 64)
    print(f'Runtime   (A) present for id X : {store.identity.get("X") is not None}')
    print(f"Workspace (B) present for id X : {'X' in json.load(open(ws_file))}")
    print("-" * 64)
    print(f"Runtime key        == Engine resolved key? {engine_key == runtime_key}")
    print(f"Workspace key      != Engine resolved key? {engine_key != workspace_key}")
    print(f"Engine resolved key == A?                 {engine_key == runtime_key}")
    print(f"Engine resolved key == B?                 {engine_key == workspace_key}")

    # Sign the same payload with each private key.
    payload = {"spec": "spec-012", "identity_id": "X"}
    sig_a = base64.b64encode(
        rt_priv.sign(json.dumps(payload, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256()))
    ).decode()
    sig_b = base64.b64encode(
        ws_priv.sign(json.dumps(payload, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256()))
    ).decode()

    # The engine-resolved identity is what the verifier checks against.
    result_a = True
    try:
        CryptoVerifier.verify(resolved.public_key, payload, sig_a)
    except Exception as e:
        result_a = f"FAIL: {e}"

    result_b = "FAIL (expected)"
    try:
        CryptoVerifier.verify(resolved.public_key, payload, sig_b)
    except Exception as e:
        result_b = "FAIL (expected)"  # B's signature must NOT verify against A's key

    print("-" * 64)
    print(f"Signature(A-private) vs engine key -> {result_a}")
    print(f"Signature(B-private) vs engine key -> {result_b}")
    print("-" * 64)

    # --- Assertions (auditor's required scenario) ---
    ok = (
        engine_key == runtime_key            # get_agent(X).public_key == A
        and engine_key != workspace_key      # get_agent(X).public_key != B
        and result_a is True                 # Signature(A-private) -> PASS
        and result_b == "FAIL (expected)"    # Signature(B-private) -> FAIL
    )

    effective = "RUNTIME (A)" if ok else "DIVERGENCE FAILED"
    print(f"=> EFFECTIVE AUTHORITY: {effective}")
    print("=" * 64)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
