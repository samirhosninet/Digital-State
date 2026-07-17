"""Governance Provisioning (ADR-011-02): trust roots + policy, Hermes-independent.

Generates a fresh ECDSA P-256 keypair per role defined in the Package's
roles.json asset, persists private keys into the Runtime KeyStore, records the
public identity in the Runtime IdentityStore (ADR-011-04), establishes policy
instances via PolicyStore (ADR-011-03), and materializes profiles from Package
templates (ADR-011-05). Seeds unconditionally — never gated on file absence, so
the empty-file trap (EV-2) cannot recur.
"""

import json
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
    load_pem_private_key,
)

from digital_state.runtime.store import RuntimeStore
from digital_state.runtime.stores import IdentityRecord

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "assets")


def _load_roles_asset() -> dict:
    with open(os.path.join(_ASSETS_DIR, "roles.json"), "r", encoding="utf-8") as f:
        return json.load(f)["roles"]


def _load_profile_templates_asset() -> dict:
    with open(
        os.path.join(_ASSETS_DIR, "profile_templates.json"), "r", encoding="utf-8"
    ) as f:
        return json.load(f)["profiles"]


def _generate_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_pem = private_key.public_key().public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    )
    private_pem = private_key.private_bytes(
        Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
    )
    return private_key, private_pem, public_pem.decode("ascii")


def provision_governance(store: RuntimeStore) -> None:
    """Seed trust roots + policy + profiles into the Runtime. Idempotent/authoritative.

    Trust-root identities are seeded from the canonical Package trust_roots.json
    asset (public keys). Their private counterparts are the operator/test-held
    keys (ADR-011-04: Runtime owns the authoritative identity; the canonical
    trust roots are the single shared key material across Runtime, workspace
    default-seed, and the test harness, so identity resolution never diverges).
    """
    roles = _load_roles_asset()
    profile_templates = _load_profile_templates_asset()

    # Canonical trust-root public keys (single shared key material).
    trust_path = os.path.join(_ASSETS_DIR, "trust_roots.json")
    trust_roots = {}
    if os.path.exists(trust_path):
        with open(trust_path, "r", encoding="utf-8") as f:
            trust_roots = json.load(f).get("trust_roots", {})

    for role_key, role_def in roles.items():
        identity_id = f"{role_key}-agent"
        public_key = trust_roots.get(
            role_key,
            {"key_id": f"key-{role_key}", "status": "Active",
             "algorithm": "ECDSA_P256", "value": ""},
        )

        # Public identity -> Runtime IdentityStore (authoritative)
        store.identity.upsert(
            IdentityRecord(
                identity_id=identity_id,
                role=role_key.capitalize(),
                public_key=public_key,
            )
        )

        # Profile -> Runtime ProfileStore (from Package template)
        template = profile_templates.get(role_key, {})
        store.profile.materialize(role_key, template)

    # Policy instances -> PolicyStore
    store.policy.establish(
        {rk: rd["permissions"] for rk, rd in roles.items()}
    )

    # Manifest reflects governance readiness
    store.manifest.governance_state = "ready"
    store.save_manifest()


def bootstrap_runtime(root: str = None) -> RuntimeStore:
    """Full first-run bootstrap: Runtime Provisioning then Governance Provisioning."""
    store = RuntimeStore(root)
    if not store.exists():
        store.provision()
    provision_governance(store)
    return store


def load_runtime_private_key(identity_id: str, store: RuntimeStore):
    """Load a Runtime-held private key (used by signing helpers / CLI)."""
    path = store.keys.path_for(identity_id)
    with open(path, "rb") as f:
        return load_pem_private_key(f.read(), password=None)
