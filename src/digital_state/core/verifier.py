import base64
import hashlib
import json
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from digital_state.core.exceptions import EvidenceError, IdentityError


class CryptoVerifier:
    """Algorithm-agnostic verification layer for agent digital signatures."""

    SUPPORTED_ALGORITHM = "ECDSA_P256"

    @staticmethod
    def validate_key_metadata(key_metadata: Dict[str, Any]) -> str:
        """Validate a production public-key identity and return its fingerprint."""
        if not isinstance(key_metadata, dict):
            raise IdentityError("A cryptographic public-key identity is required.")
        if key_metadata.get("status") != "Active":
            raise IdentityError(
                f"Verification failed: Key '{key_metadata.get('key_id')}' is not active "
                f"(status: {key_metadata.get('status')})."
            )
        if key_metadata.get("algorithm") != CryptoVerifier.SUPPORTED_ALGORITHM:
            raise IdentityError(
                f"Unsupported cryptographic algorithm '{key_metadata.get('algorithm')}'."
            )
        key_value = key_metadata.get("value")
        if not isinstance(key_value, str) or not key_value.strip():
            raise IdentityError("Key metadata value is missing.")
        key_id = key_metadata.get("key_id")
        if not isinstance(key_id, str) or not key_id.strip():
            raise IdentityError("Key metadata lacks a key_id.")
        try:
            public_key = load_pem_public_key(key_value.encode("utf-8"))
        except Exception as exc:
            raise IdentityError(f"Failed to load public key PEM: {exc}") from exc
        if not isinstance(public_key, ec.EllipticCurvePublicKey) or not isinstance(
            public_key.curve, ec.SECP256R1
        ):
            raise IdentityError("Key must be an ECDSA P-256 public key.")
        return hashlib.sha256(key_value.encode("utf-8")).hexdigest()

    @staticmethod
    def verify(key_metadata: Dict[str, Any], payload: Dict[str, Any], signature_b64: str) -> bool:
        """Verifies a signature using the public key metadata and payload.
        
        Raises EvidenceError or IdentityError upon failure.
        """
        CryptoVerifier.validate_key_metadata(key_metadata)
        key_value = key_metadata["value"]

        # Serialize payload deterministically
        serialized_payload = json.dumps(payload, sort_keys=True).encode("utf-8")

        try:
            signature_bytes = base64.b64decode(signature_b64, validate=True)
            pubkey = load_pem_public_key(key_value.encode("utf-8"))
            pubkey.verify(signature_bytes, serialized_payload, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception as exc:
            raise EvidenceError(f"ECDSA signature verification failed: {exc}") from exc
