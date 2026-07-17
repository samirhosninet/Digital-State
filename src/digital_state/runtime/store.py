"""RuntimeStore: the only sanctioned Runtime API (IA-01).

All components interact with the Runtime exclusively through this class and its
sub-store interfaces. The filesystem layout is opaque and replaceable.
"""

import os

from digital_state.runtime.manifest import RuntimeManifest, resolve_runtime_root
from digital_state.runtime.stores import (
    IdentityStore,
    ProfileStore,
    PolicyStore,
    KeyStore,
)


class RuntimeStore:
    """Top-level Runtime API (IA-01). Owns the Runtime tree + manifest (IA-03)."""

    SUBDIRS = [
        "registry",
        "keys",
        "profiles",
        "policy",
        "state",
        "memory",
        "kanban",
        "audit",
        "cache",
    ]

    def __init__(self, root: str = None):
        self.root = root or resolve_runtime_root()
        self.identity = IdentityStore(self.root)
        self.profile = ProfileStore(self.root)
        self.policy = PolicyStore(self.root)
        self.keys = KeyStore(self.root)
        self._manifest_path = os.path.join(self.root, RuntimeManifest.FILENAME)
        self.manifest = RuntimeManifest.load(self._manifest_path)

    def provision(self) -> None:
        """Runtime Provisioning (infra only). No governance semantics (ADR-011-02)."""
        for sub in self.SUBDIRS:
            os.makedirs(os.path.join(self.root, sub), exist_ok=True)
        if self.manifest.data.get("created_at") is None:
            from datetime import datetime, timezone

            self.manifest.data["created_at"] = datetime.now(timezone.utc).isoformat()
        self.manifest.provisioning_state = "ready"
        self.manifest.save(self._manifest_path)

    def exists(self) -> bool:
        return os.path.isdir(self.root) and os.path.exists(self._manifest_path)

    def refresh_manifest(self) -> None:
        self.manifest = RuntimeManifest.load(self._manifest_path)

    def save_manifest(self) -> None:
        self.manifest.save(self._manifest_path)
