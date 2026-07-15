import os
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from digital_state.core.engine import GovernanceKernel
from digital_state.core.registry import Agent

def generate_and_save(agent_id, key_dir):
    privkey = ec.generate_private_key(ec.SECP256R1())
    
    # Save private key PEM
    priv_pem = privkey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(os.path.join(key_dir, f"{agent_id}_private.pem"), "wb") as f:
        f.write(priv_pem)
        
    pubkey = privkey.public_key()
    pubkey_pem = pubkey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    
    return {
        "key_id": f"key-{agent_id}",
        "algorithm": "ECDSA_P256",
        "status": "Active",
        "value": pubkey_pem
    }

def main():
    root = "."
    kernel = GovernanceKernel(root, run_bootstrap=False)
    key_dir = os.path.join(kernel.config.specify_dir, "keys")
    os.makedirs(key_dir, exist_ok=True)
    
    prime_pub = generate_and_save("prime", key_dir)
    builder_pub = generate_and_save("builder", key_dir)
    auditor_pub = generate_and_save("auditor", key_dir)
    
    # Register in agents.json
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
    print("ECDSA P-256 private and public keys generated and registered.")

if __name__ == "__main__":
    main()
