"""Importable profile templates (ADR-011-05).

Mirrors the data in profile_templates.json so the CLI can source Hermes-mirror
content from the same Package asset that Runtime Provisioning uses. Single source
of truth = assets/profile_templates.json; this module loads it once.
"""

import json
import os

_ASSET_PATH = os.path.join(os.path.dirname(__file__), "profile_templates.json")

try:
    with open(_ASSET_PATH, "r", encoding="utf-8") as _f:
        PROFILE_TEMPLATES = json.load(_f).get("profiles", {})
except (OSError, json.JSONDecodeError):
    PROFILE_TEMPLATES = {}

__all__ = ["PROFILE_TEMPLATES"]
