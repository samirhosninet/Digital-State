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
    PrivateFormat,
    NoEncryption,
    load_pem_private_key,
)

from pathlib import Path

# Private keys live under .specify/keys/ which is gitignored (never committed).
# These are used ONLY by the test-suite to produce real ECDSA P-256 signatures
# matching the canonical trust_roots.json public keys.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_KEYS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".specify", "keys")
)

_ROLE_KEY_FILE = {
    "prime": "prime_private.pem",
    "builder": "builder_private.pem",
    "auditor": "auditor_private.pem",
}

_CANONICAL_TEST_KEYS = {
    "prime_private.pem": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgL7UYgf1C0RySM+H2\n"
        "ekgCebGQBKIljdE4u/hKoWlca1WhRANCAATzAfPXLXRbHTwagLFudAgzwBY0oikW\n"
        "OU+kDG35blSgTXCHpjg5PBZwc+w3ERW/lQrKKopA1g1jass7syoHy80J\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "builder_private.pem": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgUU+ZrFzBg+Jjf92g\n"
        "qKpR3QUzFkLsPZ2gLdMmxE57C1qhRANCAARTpjTVtmueucz7Qwgsgd3yVNaLxe3T\n"
        "uGvC2K5Bmd+uCYR4b8UbAunWdumLQmlDO8R3ih7WvP6vdSo1Yxz7ZAd2\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "auditor_private.pem": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgBjk+hArxofND6kD7\n"
        "MmAOvdvA7aANt6QAhVwSTH7d7gShRANCAAQI/F/N1pponSKyvsx+rL8vbPO6fBvi\n"
        "yr7xwD9tsnASjqWPkzaIgBV/LL4Ce1TXx7it8/9CWK8gwH6Uc5FqH6aJ\n"
        "-----END PRIVATE KEY-----\n"
    ),
}


def _ensure_test_keys():
    os.makedirs(_KEYS_DIR, exist_ok=True)
    for filename, pem_content in _CANONICAL_TEST_KEYS.items():
        path = os.path.join(_KEYS_DIR, filename)
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, "wb") as f:
                f.write(pem_content.encode("utf-8"))


@pytest.fixture(scope="session", autouse=True)
def _auto_setup_test_keys():
    _ensure_test_keys()


def _load_private_key(role: str):
    _ensure_test_keys()
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


@pytest.fixture(autouse=True)
def isolate_runtime_home(tmp_path, monkeypatch):
    """Isolate the Digital State Runtime per test (ADR-011-01: DIGITAL_STATE_HOME).

    SPEC-012 FINAL REMEDIATION (test-hygiene, no engine change): the authoritative
    Runtime-first identity resolution in ``AgentRegistry.get_agent`` reads the
    Runtime at ``DIGITAL_STATE_HOME``. The prior remediation never isolated the
    Runtime per test, so the first test that provisioned the *shared* default
    Runtime (LOCALAPPDATA/digital-state) changed identity resolution for every
    later test that relied on the workspace store — producing cross-test
    pollution failures that were NOT regressions of the authority fix.

    This autouse fixture gives every test a private, empty Runtime root (a real
    Windows path via pytest ``tmp_path``), so ``get_agent`` deterministically
    falls back to the workspace registry unless a test provisions its own Runtime.
    It preserves Runtime-first authority (a test that bootstraps the Runtime still
    wins) and makes the full suite reproducibly green.
    """
    rt = tmp_path / "ds-runtime"
    rt.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DIGITAL_STATE_HOME", str(rt))
    yield
