import json
import os
from typing import Dict, Any

from digital_state.core.exceptions import GovernanceError


class ConfigManager:
    """Manages paths, option configurations, and settings for the SpecKit workspace integration."""

    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)
        self.specify_dir = os.path.join(self.workspace_root, ".specify")
        self._ensure_specify_dir()

    def _ensure_specify_dir(self) -> None:
        """Verify the core SpecKit directory exists in the workspace."""
        if not os.path.exists(self.specify_dir):
            raise GovernanceError(
                f"Workspace not initialized: SpecKit configuration folder not found at '{self.specify_dir}'."
            )

    def load_integration_settings(self) -> Dict[str, Any]:
        """Loads integration.json settings."""
        settings_path = os.path.join(self.specify_dir, "integration.json")
        if not os.path.exists(settings_path):
            raise GovernanceError(f"Integration configuration file not found at '{settings_path}'.")
        
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise GovernanceError(f"Malformed integration JSON at '{settings_path}': {e}") from e

    def load_init_options(self) -> Dict[str, Any]:
        """Loads init-options.json settings."""
        options_path = os.path.join(self.specify_dir, "init-options.json")
        if not os.path.exists(options_path):
            raise GovernanceError(f"Initialization options file not found at '{options_path}'.")
        
        try:
            with open(options_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise GovernanceError(f"Malformed init-options JSON at '{options_path}': {e}") from e

    def get_feature_directory(self) -> str:
        """Loads the active feature directory from feature.json."""
        feature_path = os.path.join(self.specify_dir, "feature.json")
        if not os.path.exists(feature_path):
            raise GovernanceError("No active feature found. Run specify-specify first.")
        
        try:
            with open(feature_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                feat_dir = data.get("feature_directory")
                if not feat_dir:
                    raise GovernanceError("feature.json does not define 'feature_directory'.")
                return os.path.join(self.workspace_root, feat_dir)
        except json.JSONDecodeError as e:
            raise GovernanceError(f"Malformed feature JSON at '{feature_path}': {e}") from e

    def get_audit_log_path(self) -> str:
        """Determines the standard storage path for the permanent audit trail."""
        return os.path.join(self.specify_dir, "memory", "audit_log.jsonl")
