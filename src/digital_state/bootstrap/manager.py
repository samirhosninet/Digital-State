"""Runtime Bootstrap Manager (BOOTSTRAP-001 Revision 3).

Decoupled Application/Session Lifecycle Bootstrap Orchestrator.
Performs idempotent RuntimeStore provisioning, agent identity seeding,
and workspace kernel initialization at the Application Startup entry point.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

from digital_state.runtime.store import RuntimeStore
from digital_state.runtime.provision import bootstrap_runtime


class RuntimeBootstrapManager:
    """Application/Session Lifecycle Bootstrap Orchestrator.
    
    Ensures that the runtime identity store and workspace governance files are
    fully initialized before plugin activation and tool resolution.
    """

    def __init__(self, workspace_root: Optional[Path] = None, tenant_id: str = "default_tenant"):
        self.workspace_root = Path(workspace_root or os.environ.get("HERMES_WORKSPACE") or ".").resolve()
        self.tenant_id = tenant_id

    def ensure_runtime_provisioned(self) -> Dict[str, Any]:
        """Idempotently provisions RuntimeStore and seeds default agent identities."""
        store = RuntimeStore()
        already_provisioned = store.exists()
        identities = {}
        if already_provisioned:
            try:
                identities = store.identity.all_for_tenant(self.tenant_id)
            except Exception:
                identities = {}

        if not already_provisioned or not identities:
            store = bootstrap_runtime()
            identities = store.identity.all_for_tenant(self.tenant_id)
            return {
                "provisioned": True,
                "status": "SEEDED",
                "identities": list(identities.keys())
            }

        return {
            "provisioned": True,
            "status": "ALREADY_PROVISIONED",
            "identities": list(identities.keys())
        }

    def ensure_workspace_initialized(self) -> Dict[str, Any]:
        """Idempotently initializes workspace kernel state if missing."""
        specify_dir = self.workspace_root / ".specify"
        state_file = specify_dir / "state.json"

        needs_init = not state_file.exists()
        if state_file.exists():
            try:
                content = json.loads(state_file.read_text(encoding="utf-8"))
                feature_states = content.get("feature_states", {}) if isinstance(content, dict) else {}
                if not feature_states:
                    needs_init = True
            except Exception:
                needs_init = True

        if needs_init:
            specify_dir.mkdir(parents=True, exist_ok=True)
            if not state_file.exists() or state_file.stat().st_size == 0:
                state_file.write_text(
                    json.dumps({
                        "feature_states": {
                            "014-adapter-fix-verification": "IN_PROGRESS"
                        }
                    }, indent=2),
                    encoding="utf-8"
                )
            from digital_state.bootstrap.installer import BootstrapInstaller
            installer = BootstrapInstaller(workspace_root=self.workspace_root)
            res = installer.auto_initialize_workspace()
            return {
                "workspace_initialized": True,
                "status": "INITIALIZED",
                "result": res
            }

        return {
            "workspace_initialized": True,
            "status": "ALREADY_INITIALIZED"
        }

    def ensure_bootstrapped(self) -> Dict[str, Any]:
        """Orchestrates end-to-end Application Lifecycle Bootstrap."""
        runtime_res = self.ensure_runtime_provisioned()
        workspace_res = self.ensure_workspace_initialized()
        return {
            "status": "SUCCESS",
            "runtime_store": runtime_res,
            "workspace": workspace_res
        }


def ensure_runtime_bootstrapped(workspace_root: Optional[Path] = None) -> Dict[str, Any]:
    """Helper function to execute application lifecycle bootstrap."""
    manager = RuntimeBootstrapManager(workspace_root=workspace_root)
    return manager.ensure_bootstrapped()
