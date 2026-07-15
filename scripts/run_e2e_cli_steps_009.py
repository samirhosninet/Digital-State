import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from digital_state.cli.cli import run_cli

def load_private_key(agent_id):
    key_path = f".specify/keys/{agent_id}_private.pem"
    with open(key_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def get_sig(privkey, content):
    serialized = json.dumps(content, sort_keys=True).encode("utf-8")
    signature_bytes = privkey.sign(serialized, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature_bytes).decode("utf-8")

def main():
    feature_id = "feat-009"
    
    # Load keys
    prime_priv = load_private_key("prime")
    builder_priv = load_private_key("builder")
    auditor_priv = load_private_key("auditor")
    
    # 1. SPECIFICATION -> PLANNING
    spec_content = {
        "spec_file": "specs/003-hermes-runtime-integration/spec.md",
        "requirements_count": 3
    }
    sig = get_sig(prime_priv, spec_content)
    evidence_payload = spec_content.copy()
    evidence_payload["signature"] = sig
    
    print("--- 1. Submitting Spec Evidence ---")
    code = run_cli([
        "submit", "--feature", feature_id, "--gate", "SPECIFICATION",
        "--agent", "prime-agent", "--evidence", json.dumps(evidence_payload)
    ])
    assert code == 0
    
    # 2. PLANNING -> TASKS
    plan_content = {
        "plan_file": "specs/003-hermes-runtime-integration/plan.md",
        "technical_context_complete": True
    }
    sig = get_sig(builder_priv, plan_content)
    evidence_payload = plan_content.copy()
    evidence_payload["signature"] = sig
    
    print("--- 2. Submitting Planning Evidence ---")
    code = run_cli([
        "submit", "--feature", feature_id, "--gate", "PLANNING",
        "--agent", "builder-agent", "--evidence", json.dumps(evidence_payload)
    ])
    assert code == 0
    
    print("--- 3. Approving Planning Gate ---")
    code = run_cli([
        "approve", "--feature", feature_id, "--gate", "PLANNING",
        "--agent", "auditor-agent"
    ])
    assert code == 0
    
    # 3. TASKS -> IMPLEMENTATION
    tasks_content = {
        "tasks_file": "specs/003-hermes-runtime-integration/tasks.md",
        "tasks_count": 3,
        "requirements_count": 3
    }
    sig = get_sig(builder_priv, tasks_content)
    evidence_payload = tasks_content.copy()
    evidence_payload["signature"] = sig
    
    print("--- 4. Submitting Tasks Evidence ---")
    code = run_cli([
        "submit", "--feature", feature_id, "--gate", "TASKS",
        "--agent", "builder-agent", "--evidence", json.dumps(evidence_payload)
    ])
    assert code == 0
    
    print("--- 5. Approving Tasks Gate ---")
    code = run_cli([
        "approve", "--feature", feature_id, "--gate", "TASKS",
        "--agent", "auditor-agent"
    ])
    assert code == 0
    
    # 4. IMPLEMENTATION -> VERIFICATION
    impl_content = {
        "tasks_file": "specs/003-hermes-runtime-integration/tasks.md",
        "all_tasks_completed": True
    }
    sig = get_sig(builder_priv, impl_content)
    evidence_payload = impl_content.copy()
    evidence_payload["signature"] = sig
    
    print("--- 6. Submitting Implementation Evidence ---")
    code = run_cli([
        "submit", "--feature", feature_id, "--gate", "IMPLEMENTATION",
        "--agent", "builder-agent", "--evidence", json.dumps(evidence_payload)
    ])
    assert code == 0
    
    print("--- 7. Approving Implementation Gate ---")
    code = run_cli([
        "approve", "--feature", feature_id, "--gate", "IMPLEMENTATION",
        "--agent", "auditor-agent"
    ])
    assert code == 0
    
    # 5. VERIFICATION -> COMPLETED
    ver_content = {
        "walkthrough_file": "specs/003-hermes-runtime-integration/walkthrough.md",
        "all_tests_passed": True
    }
    sig = get_sig(auditor_priv, ver_content)
    evidence_payload = ver_content.copy()
    evidence_payload["signature"] = sig
    
    print("--- 8. Submitting Verification Evidence ---")
    code = run_cli([
        "submit", "--feature", feature_id, "--gate", "VERIFICATION",
        "--agent", "auditor-agent", "--evidence", json.dumps(evidence_payload)
    ])
    assert code == 0
    
    print("--- 9. Approving Verification Gate ---")
    code = run_cli([
        "approve", "--feature", feature_id, "--gate", "VERIFICATION",
        "--agent", "prime-agent"
    ])
    assert code == 0
    
    print("--- E2E CLI Steps completed successfully for feat-009. ---")

if __name__ == "__main__":
    main()
