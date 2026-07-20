"""Phase 1 Bootstrap Installer & Orchestrator (v1.14.0-bootstrap).

Provides idempotent bootstrap execution for initializing Digital State workspaces safely.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from digital_state.bootstrap.prereqs import PrerequisiteChecker


class BootstrapInstaller:
    """Idempotent installer orchestrator for Digital State workspace initialization."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path(".")
        self.checker = PrerequisiteChecker()

    def run_bootstrap(self, dry_run: bool = False) -> Dict[str, Any]:
        """Executes idempotent workspace initialization and pre-flight checks."""
        prereqs = self.checker.run_all_checks()
        if not prereqs["is_healthy"]:
            return {
                "status": "FAILED",
                "message": "Prerequisite check failed.",
                "prerequisites": prereqs
            }

        specify_dir = self.workspace_root / ".specify"
        memory_dir = specify_dir / "memory"
        device_dir = specify_dir / "device"

        if dry_run:
            return {
                "status": "DRY_RUN_SUCCESS",
                "message": "Dry-run completed successfully. All prerequisites satisfied.",
                "workspace_root": str(self.workspace_root.resolve()),
                "prerequisites": prereqs,
                "planned_directories": [
                    str(specify_dir),
                    str(memory_dir),
                    str(device_dir)
                ]
            }

        # Idempotent directory creation
        specify_dir.mkdir(parents=True, exist_ok=True)
        memory_dir.mkdir(parents=True, exist_ok=True)
        device_dir.mkdir(parents=True, exist_ok=True)

        # Idempotent state.json initialization
        state_file = specify_dir / "state.json"
        if not state_file.exists() or state_file.stat().st_size == 0:
            state_file.write_text("{}", encoding="utf-8")

        # Idempotent integration.json initialization
        integration_file = specify_dir / "integration.json"
        if not integration_file.exists():
            integration_file.write_text(
                json.dumps({
                    "integration": "hermes",
                    "version": "1.14.0",
                    "bootstrap": "idempotent",
                    "files": {}
                }, indent=2),
                encoding="utf-8"
            )

        return {
            "status": "SUCCESS",
            "message": "Digital State workspace bootstrapped successfully.",
            "workspace_root": str(self.workspace_root.resolve()),
            "prerequisites": prereqs,
            "directories_created": [
                str(specify_dir),
                str(memory_dir),
                str(device_dir)
            ]
        }
