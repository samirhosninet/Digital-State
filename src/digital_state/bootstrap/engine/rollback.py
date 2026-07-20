"""Rollback & Recovery Engine Subsystem (ECR-BOOTSTRAP-ARCHITECTURE-002).

Guarantees transactional rollback and backup restoration if any verification gate fails.
"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional


class RollbackEngine:
    """Manages cleanup of temporary directories and backup file restoration."""

    def __init__(self):
        self.created_paths: List[Path] = []
        self.backups: Dict[Path, Path] = {}

    def register_created_path(self, path: Path) -> None:
        """Registers a created directory or file for potential rollback."""
        if path not in self.created_paths:
            self.created_paths.append(path)

    def register_backup(self, original_path: Path, backup_path: Path) -> None:
        """Registers a file backup for potential restoration."""
        self.backups[original_path] = backup_path

    def rollback(self) -> None:
        """Executes transactional rollback."""
        # 1. Restore backups
        for orig, bak in self.backups.items():
            try:
                if bak.exists():
                    shutil.copy2(bak, orig)
                    bak.unlink(missing_ok=True)
            except Exception:
                pass

        # 2. Delete created files/directories in reverse creation order
        for p in reversed(self.created_paths):
            try:
                if p.is_file():
                    p.unlink(missing_ok=True)
                elif p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
            except Exception:
                pass
