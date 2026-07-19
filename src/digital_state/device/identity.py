"""Device Identity Management for Digital State (v1.11.0-device).

Handles ECDSA P-256 device keypair generation and device_id derivation:
    device_id = SHA256(public_key_pem)

Separates Device Identity (cryptographic keys & certificates) from Runtime Integrity.
"""

import hashlib
from typing import Dict, Any, Tuple, Optional
from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.asymmetric import ec
from digital_state.device.keystore import DeviceKeystore


class DeviceIdentityManager:
    """Manages local device identity generation and cryptographic derivation."""

    def __init__(self, keystore: Optional[DeviceKeystore] = None):
        self.keystore = keystore or DeviceKeystore()

    def generate_device_identity(self) -> Tuple[str, bytes, bytes]:
        """Generates ECDSA P-256 keypair, derives device_id, and stores private key securely.

        Returns:
            Tuple of (device_id, public_key_pem, private_key_pem)
        """
        # 1. Generate ECDSA P-256 keypair
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()

        # 2. Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # 3. Derive device_id = SHA256(public_key_pem)
        device_id = f"dev_sha256_{hashlib.sha256(public_pem).hexdigest()}"

        # 4. Store private key securely in keystore
        self.keystore.store_private_key(private_pem)

        return device_id, public_pem, private_pem

    def get_device_id(self, public_key_pem: bytes) -> str:
        """Derives device_id from public key PEM."""
        return f"dev_sha256_{hashlib.sha256(public_key_pem).hexdigest()}"

    def sign_payload(self, payload_bytes: bytes) -> bytes:
        """Signs a payload byte string using the stored device private key."""
        private_pem = self.keystore.retrieve_private_key()
        if not private_pem:
            raise ValueError("No device private key stored in OS keystore.")
        private_key = serialization.load_pem_private_key(private_pem, password=None)
        return private_key.sign(payload_bytes, ec.ECDSA(hashes.SHA256()))

    def get_identity_info(self) -> Dict[str, Any]:

        """Returns non-sensitive identity metadata for local diagnostics."""
        private_pem = self.keystore.retrieve_private_key()
        if not private_pem:
            return {"status": "UNINITIALIZED", "has_key": False}
        private_key = serialization.load_pem_private_key(private_pem, password=None)
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        device_id = f"dev_sha256_{hashlib.sha256(public_pem).hexdigest()}"
        return {
            "status": "ACTIVE",
            "has_key": True,
            "device_id": device_id,
            "public_key_pem": public_pem.decode("utf-8")
        }
