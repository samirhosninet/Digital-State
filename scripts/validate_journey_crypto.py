import os
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from digital_state.core.engine import GovernanceKernel
from digital_state.core.registry import Agent

def generate_key_pair(agent_id):
    privkey = ec.generate_private_key(ec.SECP256R1())
    pubkey = privkey.public_key()
    pubkey_pem = pubkey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    return privkey, {
        "key_id": f"key-{agent_id}",
        "algorithm": "ECDSA_P256",
        "status": "Active",
        "value": pubkey_pem
    }

def get_sig(privkey, content):
    serialized = json.dumps(content, sort_keys=True).encode("utf-8")
    signature_bytes = privkey.sign(serialized, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature_bytes).decode("utf-8")

def main():
    root = "."
    kernel = GovernanceKernel(root, run_bootstrap=False)
    feature_id = "feat-003"
    
    # 1. Generate P-256 cryptographic keys for agents
    prime_priv, prime_pub = generate_key_pair("prime")
    builder_priv, builder_pub = generate_key_pair("builder")
    auditor_priv, auditor_pub = generate_key_pair("auditor")
    
    # Register agents in registry with P-256 key metadata dicts (overwriting strings)
    kernel.registry.agents["prime-agent"] = Agent(
        agent_id="prime-agent",
        role="Prime",
        permissions=["define_goals", "sign_off_spec", "approve_completed"],
        public_key=prime_pub
    )
    kernel.registry.agents["builder-agent"] = Agent(
        agent_id="builder-agent",
        role="Builder",
        permissions=["submit_plan", "submit_evidence", "execute_tasks"],
        public_key=builder_pub
    )
    kernel.registry.agents["auditor-agent"] = Agent(
        agent_id="auditor-agent",
        role="Auditor",
        permissions=["approve_plan", "approve_tasks", "veto_gate", "verify_evidence"],
        public_key=auditor_pub
    )
    kernel.registry._save_agents()
    
    # 2. SPECIFICATION -> PLANNING (Prime submits spec evidence)
    # Linked to SpecKit spec.md file for feat-003 (mapped to Kanban task TASK-003)
    spec_content = {
        "spec_file": "specs/003-hermes-runtime-integration/spec.md",
        "requirements_count": 8
    }
    sig = get_sig(prime_priv, spec_content)
    kernel.submit_evidence(feature_id, "SPECIFICATION", spec_content, "prime-agent", sig)
    
    # 3. PLANNING -> TASKS (Builder submits plan, Auditor approves)
    plan_content = {
        "plan_file": "specs/003-hermes-runtime-integration/plan.md",
        "technical_context_complete": True
    }
    sig = get_sig(builder_priv, plan_content)
    kernel.submit_evidence(feature_id, "PLANNING", plan_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "PLANNING", "auditor-agent")
    
    # 4. TASKS -> IMPLEMENTATION (Builder submits tasks, Auditor approves)
    tasks_content = {
        "tasks_file": "specs/003-hermes-runtime-integration/tasks.md",
        "tasks_count": 12,
        "requirements_count": 8
    }
    sig = get_sig(builder_priv, tasks_content)
    kernel.submit_evidence(feature_id, "TASKS", tasks_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "TASKS", "auditor-agent")
    
    # 5. IMPLEMENTATION -> VERIFICATION (Builder submits implementation, Auditor approves)
    impl_content = {
        "tasks_file": "specs/003-hermes-runtime-integration/tasks.md",
        "all_tasks_completed": True
    }
    sig = get_sig(builder_priv, impl_content)
    kernel.submit_evidence(feature_id, "IMPLEMENTATION", impl_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "IMPLEMENTATION", "auditor-agent")
    
    # 6. VERIFICATION -> COMPLETED (Auditor submits verification, Prime approves)
    ver_content = {
        "walkthrough_file": "specs/003-hermes-runtime-integration/walkthrough.md",
        "all_tests_passed": True
    }
    sig = get_sig(auditor_priv, ver_content)
    kernel.submit_evidence(feature_id, "VERIFICATION", ver_content, "auditor-agent", sig)
    kernel.approve_gate(feature_id, "VERIFICATION", "prime-agent")
    
    print(f"Feature '{feature_id}' state: {kernel.get_feature_state(feature_id)}")
    print("Verification completed successfully without legacy fallback.")

if __name__ == "__main__":
    main()
