"""Remote Attestation Verifier (v1.15.0).

Verifies ECDSA P-256 cryptographic challenge-response attestations across remote devices.
"""

import hashlib
import time
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature


class RemoteAttestationVerifier:
    """Verifies cryptographic attestation signatures from host devices."""

    @staticmethod
    def verify_device_attestation(
        public_key_pem: str,
        challenge_nonce: str,
        signature_hex: str
    ) -> Tuple[bool, str]:
        """Validates device signature over challenge_nonce string.

        Args:
            public_key_pem: ECDSA P-256 public key in PEM format.
            challenge_nonce: Cryptographic challenge string.
            signature_hex: Hex-encoded DER signature.

        Returns:
            Tuple of (is_valid, message).
        """
        try:
            pub_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            if not isinstance(pub_key, ec.EllipticCurvePublicKey):
                return False, "Invalid key type: Expected ECDSA public key."

            sig_bytes = bytes.fromhex(signature_hex)
            nonce_bytes = challenge_nonce.encode("utf-8")

            pub_key.verify(
                sig_bytes,
                nonce_bytes,
                ec.ECDSA(hashes.SHA256())
            )
            return True, "Attestation signature valid."
        except InvalidSignature:
            return False, "Signature verification failed."
        except Exception as e:
            return False, f"Attestation verification error: {e}"
