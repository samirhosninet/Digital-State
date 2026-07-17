"""Runtime manifest (IA-03) and root resolution (ADR-011-01)."""

import json
import os
from typing import Any, Dict

RUNTIME_VERSION = "0.2.0"
SCHEMA_VERSION = 1

DEFAULT_UNIX = "~/.digital-state"
DEFAULT_WINDOWS = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local")),
    "digital-state",
)


def resolve_runtime_root() -> str:
    """Resolve Runtime root from DIGITAL_STATE_HOME or platform default.

    Per ADR-011-01 the root is configurable (container/CI/multi-user). Default
    follows the existing Hermes-path pattern in cli.py: LOCALAPPDATA on Windows,
    ~/.digital-state on POSIX.
    """
    override = os.environ.get("DIGITAL_STATE_HOME")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    if os.name == "nt":
        return os.path.abspath(DEFAULT_WINDOWS)
    return os.path.abspath(os.path.expanduser(DEFAULT_UNIX))


class RuntimeManifest:
    """Single authoritative Runtime metadata (IA-03). Reads/writes JSON; storage-opaque."""

    FILENAME = "manifest.json"

    def __init__(self, data: Dict[str, Any]):
        self.data = data

    @classmethod
    def defaults(cls) -> "RuntimeManifest":
        return cls(
            {
                "runtime_version": RUNTIME_VERSION,
                "schema_version": SCHEMA_VERSION,
                "provisioning_state": "pending",
                "governance_state": "pending",
                "created_at": None,
                "migrated_from": None,
            }
        )

    @classmethod
    def load(cls, path: str) -> "RuntimeManifest":
        if not os.path.exists(path):
            return cls.defaults()
        try:
            with open(path, "r", encoding="utf-8") as f:
                return cls(json.load(f))
        except (json.JSONDecodeError, OSError):
            return cls.defaults()

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.data.setdefault("runtime_version", RUNTIME_VERSION)
        self.data.setdefault("schema_version", SCHEMA_VERSION)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    @property
    def provisioning_state(self) -> str:
        return self.data.get("provisioning_state", "pending")

    @provisioning_state.setter
    def provisioning_state(self, value: str) -> None:
        self.data["provisioning_state"] = value

    @property
    def governance_state(self) -> str:
        return self.data.get("governance_state", "pending")

    @governance_state.setter
    def governance_state(self, value: str) -> None:
        self.data["governance_state"] = value

    @property
    def schema_version(self) -> int:
        return int(self.data.get("schema_version", SCHEMA_VERSION))
