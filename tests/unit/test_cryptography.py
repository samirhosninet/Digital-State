import base64
import json
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

from digital_state.core.verifier import CryptoVerifier
from digital_state.core.exceptions import EvidenceError, IdentityError


@pytest.fixture
def key_pair():
    """Generates an ECDSA P-256 key pair for test signing."""
    privkey = ec.generate_private_key(ec.SECP256R1())
    pubkey = privkey.public_key()
    pubkey_pem = pubkey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")
    return privkey, pubkey_pem


def test_conforming_ecdsa_signature(key_pair):
    """Verify that a valid ECDSA signature verifies successfully."""
    privkey, pubkey_pem = key_pair
    payload = {"test": "data", "count": 42}
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")

    # Generate signature
    signature_bytes = privkey.sign(serialized, ec.ECDSA(hashes.SHA256()))
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    key_metadata = {
        "key_id": "key-1",
        "algorithm": "ECDSA_P256",
        "status": "Active",
        "value": pubkey_pem
    }

    # Verify must pass
    assert CryptoVerifier.verify(key_metadata, payload, signature_b64) is True


def test_modified_payload_rejection(key_pair):
    """Verify that changing a payload field values fails verification."""
    privkey, pubkey_pem = key_pair
    payload = {"test": "data", "count": 42}
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")

    signature_bytes = privkey.sign(serialized, ec.ECDSA(hashes.SHA256()))
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    key_metadata = {
        "key_id": "key-1",
        "algorithm": "ECDSA_P256",
        "status": "Active",
        "value": pubkey_pem
    }

    # Modify payload
    modified_payload = {"test": "data", "count": 43}
    with pytest.raises(EvidenceError) as exc:
        CryptoVerifier.verify(key_metadata, modified_payload, signature_b64)
    assert "verification failed" in str(exc.value)


def test_wrong_key_verification_failure(key_pair):
    """Verify that a signature signed with a different key is rejected."""
    privkey, pubkey_pem = key_pair
    payload = {"test": "data"}
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")

    # Generate signature with a different private key
    other_privkey = ec.generate_private_key(ec.SECP256R1())
    signature_bytes = other_privkey.sign(serialized, ec.ECDSA(hashes.SHA256()))
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    key_metadata = {
        "key_id": "key-1",
        "algorithm": "ECDSA_P256",
        "status": "Active",
        "value": pubkey_pem
    }

    with pytest.raises(EvidenceError):
        CryptoVerifier.verify(key_metadata, payload, signature_b64)


def test_malformed_pem_handling():
    """Verify that malformed PEM keys trigger IdentityError."""
    payload = {"test": "data"}
    key_metadata = {
        "key_id": "key-1",
        "algorithm": "ECDSA_P256",
        "status": "Active",
        "value": "MALFORMED PUBLIC KEY PEM STRING"
    }

    with pytest.raises(IdentityError) as exc:
        CryptoVerifier.verify(key_metadata, payload, "c2lnbmF0dXJl")
    assert "Key is not an Elliptic Curve public key" in str(exc.value) or "Failed to load public key PEM" in str(exc.value)


def test_disabled_key_handling(key_pair):
    """Verify that disabled keys raise IdentityError."""
    privkey, pubkey_pem = key_pair
    payload = {"test": "data"}
    serialized = json.dumps(payload, sort_keys=True).encode("utf-8")

    signature_bytes = privkey.sign(serialized, ec.ECDSA(hashes.SHA256()))
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    key_metadata = {
        "key_id": "key-1",
        "algorithm": "ECDSA_P256",
        "status": "Disabled",
        "value": pubkey_pem
    }

    with pytest.raises(IdentityError) as exc:
        CryptoVerifier.verify(key_metadata, payload, signature_b64)
    assert "is not active" in str(exc.value)
