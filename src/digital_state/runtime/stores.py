"""Identity model (IA-02) and sub-stores. Backed by the Runtime only (ADR-011-04)."""

import json
import os
from typing import Any, Dict, Optional


class IdentityRecord:
    """Cryptographic identity: ownership, not authorization, not behavior (IA-02).

    Distinct from Role (authorization), Profile (behavior), Agent (runtime
    execution instance). The engine never equates Identity == Agent.
    """

    def __init__(
        self,
        identity_id: str,
        role: str,
        public_key: Dict[str, Any],
        private_key_path: Optional[str] = None,
        status: str = "Active",
        tenant_id: str = "default_tenant",
    ):
        self.identity_id = identity_id
        self.role = role
        self.public_key = public_key
        self.private_key_path = private_key_path
        self.status = status
        self.tenant_id = tenant_id or "default_tenant"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity_id": self.identity_id,
            "role": self.role,
            "public_key": self.public_key,
            "private_key_path": self.private_key_path,
            "status": self.status,
            "tenant_id": self.tenant_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IdentityRecord":
        return cls(
            identity_id=data["identity_id"],
            role=data["role"],
            public_key=data["public_key"],
            private_key_path=data.get("private_key_path"),
            status=data.get("status", "Active"),
            tenant_id=data.get("tenant_id", "default_tenant"),
        )


class IdentityStore:
    """Authoritative identity store. Backed by Runtime only; opaque filename."""

    FILENAME = "registry/agents.json"

    def __init__(self, runtime_root: str):
        self._root = runtime_root
        self._path = os.path.join(runtime_root, self.FILENAME)

    def _read_all(self) -> Dict[str, Any]:
        if not os.path.exists(self._path):
            return {}
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all(self, data: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def upsert(self, identity: IdentityRecord) -> None:
        data = self._read_all()
        data[identity.identity_id] = identity.to_dict()
        self._write_all(data)

    def get(self, identity_id: str) -> Optional[IdentityRecord]:
        rec = self._read_all().get(identity_id)
        return IdentityRecord.from_dict(rec) if rec else None

    def get_for_tenant(self, identity_id: str, tenant_id: str = "default_tenant") -> Optional[IdentityRecord]:
        rec = self.get(identity_id)
        if rec and (rec.tenant_id == tenant_id or tenant_id == "default_tenant"):
            return rec
        return None

    def all(self) -> Dict[str, IdentityRecord]:
        return {
            iid: IdentityRecord.from_dict(rec) for iid, rec in self._read_all().items()
        }

    def all_for_tenant(self, tenant_id: str = "default_tenant") -> Dict[str, IdentityRecord]:
        all_recs = self.all()
        if not tenant_id or tenant_id == "default_tenant":
            return all_recs
        return {
            iid: rec for iid, rec in all_recs.items() if rec.tenant_id == tenant_id
        }

    def exists(self) -> bool:
        return os.path.exists(self._path)



class ProfileStore:
    """Materialized profiles (IA-02), generated from Package templates at provisioning."""

    DIR = "profiles"

    def __init__(self, runtime_root: str):
        self._root = runtime_root
        self._dir = os.path.join(runtime_root, self.DIR)

    def materialize(self, role_key: str, files: Dict[str, str]) -> str:
        prof_dir = os.path.join(self._dir, role_key)
        os.makedirs(prof_dir, exist_ok=True)
        for name, content in files.items():
            with open(os.path.join(prof_dir, name), "w", encoding="utf-8") as f:
                f.write(content)
        return prof_dir

    def path_for(self, role_key: str) -> str:
        return os.path.join(self._dir, role_key)


class PolicyStore:
    """Governance policy instances established at provisioning (ADR-011-03)."""

    FILENAME = "policy/governance.json"

    def __init__(self, runtime_root: str):
        self._root = runtime_root
        self._path = os.path.join(runtime_root, self.FILENAME)

    def establish(self, roles: Dict[str, Any]) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({"roles": roles}, f, indent=2)

    def load_roles(self) -> Dict[str, Any]:
        if not os.path.exists(self._path):
            return {}
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f).get("roles", {})


class KeyStore:
    """Per-install private keys. Gitignored; Runtime-owned (ADR-011-04)."""

    DIR = "keys"

    def __init__(self, runtime_root: str):
        self._root = runtime_root
        self._dir = os.path.join(runtime_root, self.DIR)

    def write_private_key(self, identity_id: str, pem: bytes) -> str:
        os.makedirs(self._dir, exist_ok=True)
        path = os.path.join(self._dir, f"{identity_id}_private.pem")
        with open(path, "wb") as f:
            f.write(pem)
        return path

    def path_for(self, identity_id: str) -> str:
        return os.path.join(self._dir, f"{identity_id}_private.pem")
