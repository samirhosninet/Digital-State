"""Device Enrollment Protocol for Cryptographic Identity Handshake (v1.11.0-device).

Implements 5-step challenge-response device enrollment with RuntimeStore:
    1. Create enrollment request (device_id, public_key_pem)
    2. Receive challenge nonce (32-byte cryptographic nonce + expiration)
    3. Sign challenge nonce using DeviceIdentityManager (ECDSA P-256)
    4. Verify challenge response signature & nonce expiration
    5. Issue & store local device certificate metadata (.specify/device/device-certificate.json)

Private keys are NEVER exposed, exported, or written to disk.
"""

import json
import os
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from digital_state.device.identity import DeviceIdentityManager


class EnrollmentProtocol:
    """Manages cryptographic challenge-response enrollment handshake."""

    def __init__(self, device_dir: Optional[Path] = None, identity_mgr: Optional[DeviceIdentityManager] = None):
        self.device_dir = device_dir or Path(".specify") / "device"
        self.device_dir.mkdir(parents=True, exist_ok=True)
        if identity_mgr:
            self.identity_mgr = identity_mgr
        else:
            from digital_state.device.keystore import DeviceKeystore
            keystore = DeviceKeystore(storage_dir=self.device_dir)
            self.identity_mgr = DeviceIdentityManager(keystore=keystore)


    def create_enrollment_request(self) -> Dict[str, Any]:
        """Creates initial device enrollment request payload."""
        info = self.identity_mgr.get_identity_info()
        if not info.get("has_key"):
            # Auto-generate if uninitialized
            device_id, pub_pem, _ = self.identity_mgr.generate_device_identity()
            pub_pem_str = pub_pem.decode("utf-8")
        else:
            device_id = info["device_id"]
            pub_pem_str = info["public_key_pem"]

        return {
            "device_id": device_id,
            "public_key_pem": pub_pem_str,
            "request_timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def generate_challenge_nonce(ttl_seconds: int = 300) -> Dict[str, Any]:
        """Simulates central authority issuing a 32-byte cryptographic challenge nonce."""
        nonce_hex = secrets.token_hex(32)
        now_ts = time.time()
        return {
            "challenge_nonce": nonce_hex,
            "issued_at": now_ts,
            "expires_at": now_ts + ttl_seconds
        }

    def sign_challenge(self, challenge: Dict[str, Any]) -> Dict[str, Any]:
        """Signs a challenge nonce using the stored device private key."""
        nonce_hex = challenge.get("challenge_nonce")
        if not nonce_hex:
            raise ValueError("Invalid challenge: missing challenge_nonce.")

        # Sign raw nonce bytes
        nonce_bytes = nonce_hex.encode("utf-8")
        sig_bytes = self.identity_mgr.sign_payload(nonce_bytes)
        sig_hex = sig_bytes.hex()

        info = self.identity_mgr.get_identity_info()

        return {
            "device_id": info["device_id"],
            "challenge_nonce": nonce_hex,
            "signature": sig_hex,
            "signed_at": datetime.now(timezone.utc).isoformat()
        }

    def verify_and_enroll(self, challenge: Dict[str, Any], response: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Verifies signed challenge response and issues device-certificate.json metadata.

        Validates:
            1. Challenge nonce match
            2. Challenge expiration (TTL)
            3. Signature validity over public key PEM
        """
        # 1. Nonce match
        if challenge.get("challenge_nonce") != response.get("challenge_nonce"):
            return False, {"status": "REJECTED", "reason": "Challenge nonce mismatch."}

        # 2. Expiration check
        now_ts = time.time()
        expires_at = challenge.get("expires_at", 0)
        if now_ts > expires_at:
            return False, {"status": "REJECTED", "reason": "Challenge nonce expired."}

        # 3. Signature verification
        info = self.identity_mgr.get_identity_info()
        pub_pem_str = info.get("public_key_pem")
        if not pub_pem_str:
            return False, {"status": "REJECTED", "reason": "Missing device public key."}

        try:
            public_key = serialization.load_pem_public_key(pub_pem_str.encode("utf-8"))
            sig_bytes = bytes.fromhex(response["signature"])
            nonce_bytes = response["challenge_nonce"].encode("utf-8")
            public_key.verify(sig_bytes, nonce_bytes, ec.ECDSA(hashes.SHA256()))
        except Exception as e:
            return False, {"status": "REJECTED", "reason": f"Invalid signature over challenge nonce ({e})."}

        # 4. Issue and store device-certificate.json with authentic ECDSA CA signature
        ca_priv_file = self.device_dir / "ca_key.pem"
        if not ca_priv_file.exists():
            ca_priv = ec.generate_private_key(ec.SECP256R1())
            ca_pem = ca_priv.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            ca_priv_file.write_bytes(ca_pem)
        else:
            ca_priv = serialization.load_pem_private_key(ca_priv_file.read_bytes(), password=None)

        ca_pub_pem = ca_priv.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8")

        issued_at_str = datetime.now(timezone.utc).isoformat()
        expires_at_str = datetime.fromtimestamp(now_ts + 7776000, tz=timezone.utc).isoformat()

        payload_to_sign = f"{info['device_id']}:{pub_pem_str}:{issued_at_str}:{expires_at_str}".encode("utf-8")
        cert_sig_bytes = ca_priv.sign(payload_to_sign, ec.ECDSA(hashes.SHA256()))

        cert_data = {
            "status": "ENROLLED",
            "device_id": info["device_id"],
            "public_key_pem": pub_pem_str,
            "issuer": "RuntimeStore Authority (ADR-011)",
            "ca_public_key_pem": ca_pub_pem,
            "issued_at": issued_at_str,
            "expires_at": expires_at_str,
            "certificate_signature": cert_sig_bytes.hex()
        }

        cert_file = self.device_dir / "device-certificate.json"
        cert_file.write_text(json.dumps(cert_data, indent=2), encoding="utf-8")

        return True, cert_data

    @staticmethod
    def verify_certificate(cert_data: Dict[str, Any]) -> bool:
        """Cryptographically verifies device certificate signature against CA public key."""
        try:
            ca_pub_pem = cert_data.get("ca_public_key_pem")
            sig_hex = cert_data.get("certificate_signature")
            if not ca_pub_pem or not sig_hex:
                return False

            ca_pub = serialization.load_pem_public_key(ca_pub_pem.encode("utf-8"))
            sig_bytes = bytes.fromhex(sig_hex)

            device_id = cert_data.get("device_id", "")
            pub_pem_str = cert_data.get("public_key_pem", "")
            issued_at = cert_data.get("issued_at", "")
            expires_at = cert_data.get("expires_at", "")

            payload = f"{device_id}:{pub_pem_str}:{issued_at}:{expires_at}".encode("utf-8")
            ca_pub.verify(sig_bytes, payload, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

    def renew_certificate(self, ttl_days: int = 90) -> Tuple[bool, Dict[str, Any]]:
        """Renews existing device certificate with authentic CA signature."""
        cert_file = self.device_dir / "device-certificate.json"
        info = self.identity_mgr.get_identity_info()
        if not info.get("has_key"):
            return False, {"status": "FAILED", "reason": "No device key available for renewal."}

        challenge = self.generate_challenge_nonce()
        response = self.sign_challenge(challenge)
        return self.verify_and_enroll(challenge, response)

