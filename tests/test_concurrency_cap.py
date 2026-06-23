"""Concurrency cap tests for Digital State.

Verifies that every profile config.yaml contains the mandatory
kanban.max_in_progress_per_profile: 1 setting (Constitution Article XIII).
"""
import os
import yaml
import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PROFILES = ["prime", "builder", "auditor"]


def load_config(profile: str) -> dict:
    path = os.path.join(ROOT, "profiles", profile, "config.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestConcurrencyCap:
    """Every Digital State profile must have kanban.max_in_progress_per_profile = 1."""

    @pytest.mark.parametrize("profile", PROFILES)
    def test_cap_present(self, profile):
        config = load_config(profile)
        assert "kanban" in config, f"{profile} config.yaml missing 'kanban' section"
        kanban = config["kanban"]
        assert "max_in_progress_per_profile" in kanban, (
            f"{profile} config.yaml missing 'kanban.max_in_progress_per_profile'"
        )

    @pytest.mark.parametrize("profile", PROFILES)
    def test_cap_value_is_one(self, profile):
        config = load_config(profile)
        cap = config["kanban"]["max_in_progress_per_profile"]
        assert cap == 1, (
            f"{profile} kanban.max_in_progress_per_profile = {cap}, expected 1"
        )

    @pytest.mark.parametrize("profile", PROFILES)
    def test_no_model_in_portable_config(self, profile):
        """Portable config.yaml must NOT contain model/provider (RISK-006, Article XI)."""
        config = load_config(profile)
        assert "model" not in config, (
            f"{profile} config.yaml contains 'model' section — violates overlay portability (RISK-006). "
            f"Model config should be set by the installer, not the portable package."
        )

    @pytest.mark.parametrize("profile", PROFILES)
    def test_toolsets_present(self, profile):
        config = load_config(profile)
        assert "toolsets" in config, f"{profile} config.yaml missing 'toolsets'"
        toolsets = config["toolsets"]
        assert "kanban" in toolsets, f"{profile} toolsets must include 'kanban'"
