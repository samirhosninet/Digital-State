"""OS Keystore Abstraction for Device Runtime Private Keys.

Provides secure storage for ECDSA P-256 device private keys without plain text disk persistence.
Uses DPAPI on Windows where available, or FIPS-compliant AES-256-GCM with PBKDF2 key derivation.
"""

import base64
import os
import platform
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


class DeviceKeystore:
    """Secure OS-level key storage abstraction."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(".specify") / "device"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._key_file = self.storage_dir / "keystore.enc"

    def _get_machine_entropy(self) -> bytes:
        """Derives hardware/OS-bound entropy for local key encryption."""
        machine_info = f"{platform.node()}-{platform.system()}-{platform.machine()}-DS-DEVICE-KEY"
        custom_key = os.environ.get("DS_MASTER_KEY", "")
        if custom_key:
            machine_info += f"-{custom_key}"
        return machine_info.encode("utf-8")

    def _derive_aes_key(self, salt: bytes) -> bytes:
        """Derives a 256-bit key using PBKDF2HMAC-SHA256 (100,000 iterations)."""
        entropy = self._get_machine_entropy()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        return kdf.derive(entropy)

    def _aes_gcm_encrypt(self, data: bytes) -> bytes:
        """Encrypts data using AES-256-GCM with PBKDF2-derived key."""
        salt = os.urandom(16)
        nonce = os.urandom(12)
        key = self._derive_aes_key(salt)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        b64_ct = base64.b64encode(ciphertext).decode("utf-8")
        return f"AESGCM:{salt.hex()}:{nonce.hex()}:{b64_ct}".encode("utf-8")

    def _aes_gcm_decrypt(self, payload_str: str) -> Optional[bytes]:
        """Decrypts AES-256-GCM formatted payload."""
        parts = payload_str.split(":")
        if len(parts) != 4 or parts[0] != "AESGCM":
            return None
        try:
            salt = bytes.fromhex(parts[1])
            nonce = bytes.fromhex(parts[2])
            ciphertext = base64.b64decode(parts[3])
            key = self._derive_aes_key(salt)
            aesgcm = AESGCM(key)
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception:
            return None

    def store_private_key(self, private_key_pem: bytes) -> bool:
        """Encrypts and stores private key without plain text disk persistence."""
        try:
            if platform.system() == "Windows":
                try:
                    import win32crypt
                    encrypted = win32crypt.CryptProtectData(private_key_pem, "DSDeviceKey", None, None, None, 0)
                    self._key_file.write_bytes(b"DPAPI:" + encrypted)
                    return True
                except (ImportError, Exception):
                    pass

            encrypted_payload = self._aes_gcm_encrypt(private_key_pem)
            self._key_file.write_bytes(encrypted_payload)
            return True
        except Exception:
            return False

    def retrieve_private_key(self) -> Optional[bytes]:
        """Retrieves and decrypts device private key."""
        if not self._key_file.exists():
            return None
        try:
            content = self._key_file.read_bytes()
            if content.startswith(b"DPAPI:"):
                try:
                    import win32crypt
                    _, decrypted = win32crypt.CryptUnprotectData(content[6:])
                    return decrypted
                except (ImportError, Exception):
                    pass

            if content.startswith(b"AESGCM:"):
                return self._aes_gcm_decrypt(content.decode("utf-8"))

            return None
        except Exception:
            return None

    def has_stored_key(self) -> bool:
        """Checks if a valid key is present in the keystore."""
        return self.retrieve_private_key() is not None

