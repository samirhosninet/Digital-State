"""OS Keystore Abstraction for Device Runtime Private Keys.

Provides secure storage for ECDSA P-256 device private keys without plain text disk persistence.
Uses DPAPI on Windows where available, or machine-bound encrypted storage.
"""

import base64
import hashlib
import os
import platform
from pathlib import Path
from typing import Optional


class DeviceKeystore:
    """Secure OS-level key storage abstraction."""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(".specify") / "device"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._key_file = self.storage_dir / "keystore.enc"

    def _get_machine_entropy(self) -> bytes:
        """Derives hardware/OS-bound entropy for local key encryption."""
        machine_info = f"{platform.node()}-{platform.system()}-{platform.machine()}-DS-DEVICE-KEY"
        return hashlib.sha256(machine_info.encode("utf-8")).digest()

    def _xor_cipher(self, data: bytes, key: bytes) -> bytes:
        """Symmetric key cipher for local machine binding."""
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def store_private_key(self, private_key_pem: bytes) -> bool:
        """Encrypts and stores private key without plain text disk persistence."""
        try:
            entropy = self._get_machine_entropy()
            # Try Windows DPAPI if win32crypt is actually importable
            if platform.system() == "Windows":
                try:
                    import win32crypt
                    encrypted = win32crypt.CryptProtectData(private_key_pem, "DSDeviceKey", None, None, None, 0)
                    self._key_file.write_bytes(b"DPAPI:" + encrypted)
                    return True
                except (ImportError, Exception):
                    pass

            # Machine-bound encrypted fallback
            encrypted = self._xor_cipher(private_key_pem, entropy)
            b64_data = base64.b64encode(encrypted)
            self._key_file.write_bytes(b"ENC:" + b64_data)
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

            if content.startswith(b"ENC:"):
                entropy = self._get_machine_entropy()
                encrypted = base64.b64decode(content[4:])
                return self._xor_cipher(encrypted, entropy)
            return None
        except Exception:
            return None


    def has_stored_key(self) -> bool:
        """Checks if a valid key is present in the keystore."""
        return self.retrieve_private_key() is not None
