"""End-to-end product-validation smoke test (AC #11).

Runs the FULL governance lifecycle against a clean workspace using the
Runtime-first identity model that shipped broken (BUG-VAL-001: role-case
mismatch → permissions=[]). This script is the independent acceptance proof
that an external user can complete the workflow after remediation.

Run from the project root with an isolated interpreter (PYTHONPATH unset):
    PYTHONPATH= .venv-install/Scripts/python.exe scripts/smoke_e2e.py
"""
import base64
import json
import os
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CLI = os.path.join(REPO, ".venv-install", "Scripts", "digitalstate.exe")


def run_cli(args, cwd):
    res = subprocess.run(
        [CLI, *args], cwd=cwd, capture_output=True, text=True
    )
    if res.returncode != 0:
        raise SystemExit(
            f"CLI FAILED ({args}): rc={res.returncode}\nstdout={res.stdout}\nstderr={res.stderr}"
        )
    return res.stdout.strip()


def make_keys():
    """Generate a real ECDSA P-256 keypair; return (pem_priv, pem_pub)."""
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()
    priv_pem = priv.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode()
    return priv_pem, pub, priv


def sign(priv, payload):
    sig = priv.sign(json.dumps(payload, sort_keys=True).encode(), ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(sig).decode()


def main():
    tmp = tempfile.mkdtemp(prefix="ds-smoke-")
    os.environ["DIGITAL_STATE_HOME"] = os.path.join(tmp, "runtime")
    os.makedirs(os.environ["DIGITAL_STATE_HOME"], exist_ok=True)

    # 0. Initialize a clean workspace (also bootstraps the Runtime identity store)
    run_cli(["init"], cwd=tmp)

    role_keys = {}
    for role in ("prime", "builder", "auditor"):
        priv_pem, pub, priv = make_keys()
        role_keys[role] = {"priv": priv, "pub": pub}
        # write public key file
        pub_path = os.path.join(tmp, f"{role}.pem")
        with open(pub_path, "w", encoding="utf-8") as f:
            f.write(pub)
        # BUG-VAL-002 proof: re-register the seeded trust-root ID with --force
        out = run_cli([
            "register", "--id", f"{role}-agent", "--role", role.capitalize(),
            "--public-key-file", pub_path, "--key-id", f"key-{role}", "--force",
        ], cwd=tmp)
        assert "registered successfully" in out, out

    feature = "feat-val-e2e"
    states = []

    # SPECIFICATION gate (prime submits, auditor approves)
    spec = {"spec_file": "specs/val.md", "requirements_count": 3}
    sig = sign(role_keys["prime"]["priv"], spec)
    spec["signature"] = sig
    run_cli(["submit", "--feature", feature, "--gate", "SPECIFICATION",
             "--evidence", json.dumps(spec), "--agent", "prime-agent"], cwd=tmp)
    run_cli(["approve", "--feature", feature, "--gate", "SPECIFICATION",
             "--agent", "auditor-agent"], cwd=tmp)
    states.append("PLANNING")

    # PLANNING gate (builder submits, auditor approves)
    plan = {"plan_file": "specs/val-plan.md", "technical_context_complete": True}
    sig = sign(role_keys["builder"]["priv"], plan)
    plan["signature"] = sig
    run_cli(["submit", "--feature", feature, "--gate", "PLANNING",
             "--evidence", json.dumps(plan), "--agent", "builder-agent"], cwd=tmp)
    run_cli(["approve", "--feature", feature, "--gate", "PLANNING",
             "--agent", "auditor-agent"], cwd=tmp)
    states.append("TASKS")

    # TASKS gate (builder submits, auditor approves)
    tasks = {"tasks_file": "specs/val-tasks.md", "tasks_count": 4}
    sig = sign(role_keys["builder"]["priv"], tasks)
    tasks["signature"] = sig
    run_cli(["submit", "--feature", feature, "--gate", "TASKS",
             "--evidence", json.dumps(tasks), "--agent", "builder-agent"], cwd=tmp)
    run_cli(["approve", "--feature", feature, "--gate", "TASKS",
             "--agent", "auditor-agent"], cwd=tmp)
    states.append("IMPLEMENTATION")

    # IMPLEMENTATION gate (builder submits, auditor verifies)
    impl = {"tasks_file": "specs/val-tasks.md", "all_tasks_completed": True}
    sig = sign(role_keys["builder"]["priv"], impl)
    impl["signature"] = sig
    run_cli(["submit", "--feature", feature, "--gate", "IMPLEMENTATION",
             "--evidence", json.dumps(impl), "--agent", "builder-agent"], cwd=tmp)
    run_cli(["approve", "--feature", feature, "--gate", "IMPLEMENTATION",
             "--agent", "auditor-agent"], cwd=tmp)
    states.append("VERIFICATION")

    # VERIFICATION gate (auditor submits, prime approves to COMPLETED)
    ver = {"walkthrough_file": "specs/val-walkthrough.md", "all_tests_passed": True}
    sig = sign(role_keys["auditor"]["priv"], ver)
    ver["signature"] = sig
    run_cli(["submit", "--feature", feature, "--gate", "VERIFICATION",
             "--evidence", json.dumps(ver), "--agent", "auditor-agent"], cwd=tmp)
    run_cli(["approve", "--feature", feature, "--gate", "VERIFICATION",
             "--agent", "prime-agent"], cwd=tmp)
    states.append("COMPLETED")

    # Verify final state via status
    status_out = run_cli(["status", "--feature", feature], cwd=tmp)
    status = json.loads(status_out)
    print("FINAL STATE:", status["current_state"])
    print("HISTORY LEN:", len(status["history"]))
    print("HISTORY:", [h["to_state"] for h in status["history"]])

    assert status["current_state"] == "COMPLETED", "Lifecycle did not reach COMPLETED"
    assert len(status["history"]) == 5, "Expected 5 transitions"
    print("\nE2E SMOKE TEST: PASS ✅ (full lifecycle SPECIFICATION -> COMPLETED via Runtime-first identities)")


if __name__ == "__main__":
    main()
