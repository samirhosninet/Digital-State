import base64
import json
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from digital_state.core.exceptions import EvidenceError, IdentityError


class CryptoVerifier:
    """Algorithm-agnostic verification layer for agent digital signatures."""

    @staticmethod
    def verify(key_metadata: Dict[str, Any], payload: Dict[str, Any], signature_b64: str) -> bool:
        """Verifies a signature using the public key metadata and payload.
        
        Raises EvidenceError or IdentityError upon failure.
        """
        # Validate key status
        status = key_metadata.get("status")
        if status != "Active":
            raise IdentityError(
                f"Verification failed: Key '{key_metadata.get('key_id')}' is not active (status: {status})."
            )

        # Resolve algorithm
        algo = key_metadata.get("algorithm")
        if not algo:
            raise IdentityError("Key metadata lacks algorithm specification.")

        key_value = key_metadata.get("value")
        if not key_value:
            raise IdentityError("Key metadata value is missing.")

        # Serialize payload deterministically
        serialized_payload = json.dumps(payload, sort_keys=True).encode("utf-8")

        if algo == "ECDSA_P256":
            try:
                pubkey = load_pem_public_key(key_value.encode("utf-8"))
            except Exception as e:
                raise IdentityError(f"Failed to load public key PEM: {e}")

            if not isinstance(pubkey, ec.EllipticCurvePublicKey):
                raise IdentityError("Key is not an Elliptic Curve public key.")

            try:
                signature_bytes = base64.b64decode(signature_b64)
                pubkey.verify(signature_bytes, serialized_payload, ec.ECDSA(hashes.SHA256()))
                return True
            except Exception as e:
                raise EvidenceError(f"ECDSA signature verification failed: {e}")
        else:
            raise IdentityError(f"Unsupported cryptographic algorithm '{algo}'.")
