import os
import sys
import json
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

def main():
    if len(sys.argv) < 3:
        print("Usage: python sign_payload.py <agent_id> '<json_payload>'")
        sys.exit(1)
        
    agent_id = sys.argv[1]
    payload_str = sys.argv[2]
    
    # Load private key
    key_path = f".specify/keys/{agent_id}_private.pem"
    if not os.path.exists(key_path):
        print(f"Error: private key not found at {key_path}")
        sys.exit(1)
        
    with open(key_path, "rb") as f:
        privkey = serialization.load_pem_private_key(f.read(), password=None)
        
    payload = json.loads(payload_str)
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
    
    # Sign
    signature_bytes = privkey.sign(serialized, ec.ECDSA(hashes.SHA256()))
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")
    
    # Output the final CLI argument value
    evidence_obj = payload.copy()
    evidence_obj["signature"] = signature_b64
    print(json.dumps(evidence_obj))

if __name__ == "__main__":
    main()
