import base64
import hashlib
import json
import os

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_private_key,
)

# Private keys live under .specify/keys/ which is gitignored (never committed).
# These are used ONLY by the test-suite to produce real ECDSA P-256 signatures
# that satisfy the production-grade CryptoVerifier enforced by spec 009.
_KEYS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".specify", "keys")
)

_ROLE_KEY_FILE = {
    "prime": "prime_private.pem",
    "builder": "builder_private.pem",
    "auditor": "auditor_private.pem",
}


def _load_private_key(role: str):
    path = os.path.join(_KEYS_DIR, _ROLE_KEY_FILE[role])
    with open(path, "rb") as f:
        return load_pem_private_key(f.read(), password=None)


def sign_payload(role: str, payload: dict) -> str:
    """Produce a real base64 ECDSA P-256 signature over the deterministically
    serialized payload, matching CryptoVerifier.verify expectations."""
    private_key = _load_private_key(role)
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = private_key.sign(serialized, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature).decode("ascii")


def public_key_dict(role: str) -> dict:
    """Return a valid ECDSA P-256 public-key identity dict for the given role,
    suitable for AgentRegistry registration (matches CryptoVerifier.validate_key_metadata)."""
    private_key = _load_private_key(role)
    public_pem = (
        private_key.public_key()
        .public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)
        .decode("ascii")
    )
    return {
        "key_id": f"key-{role}",
        "status": "Active",
        "algorithm": "ECDSA_P256",
        "value": public_pem,
    }


def content_hash(payload: dict) -> str:
    """SHA-256 of the deterministically serialized payload (matches test idiom)."""
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


@pytest.fixture
def shared_contracts_dir() -> str:
    """Fixture pointing to the package core contracts directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    contracts_dir = os.path.join(current_dir, "..", "src", "digital_state", "core", "contracts")
    return os.path.abspath(contracts_dir)
