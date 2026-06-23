"""Structural validation tests for Digital State.

Verifies that the final package contains all required files
and directories defined in distribution.yaml. These tests mirror
the checks in validate-final.ps1 but run as Python so they can be
part of the pytest suite.
"""
import os
import re
import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DISTRIBUTION_YAML = os.path.join(ROOT, "distribution.yaml")


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def get_distribution_owned() -> list[str]:
    """Extract distribution_owned entries from distribution.yaml."""
    content = read_file(DISTRIBUTION_YAML)
    in_owned = False
    entries = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("distribution_owned:"):
            in_owned = True
            continue
        if in_owned:
            if stripped.startswith("- "):
                entries.append(stripped[2:].strip())
            elif stripped and not stripped.startswith("#"):
                break
    return entries


class TestRequiredFiles:
    """All files listed in distribution_owned must exist."""

    def test_distribution_yaml_exists(self):
        assert os.path.exists(DISTRIBUTION_YAML), "distribution.yaml must exist"

    def test_agents_md_exists(self):
        assert os.path.exists(os.path.join(ROOT, "AGENTS.md")), "AGENTS.md must exist"

    def test_changelog_exists(self):
        assert os.path.exists(os.path.join(ROOT, "CHANGELOG.md")), "CHANGELOG.md must exist"

    def test_risk_ledger_exists(self):
        assert os.path.exists(os.path.join(ROOT, "risk-ledger.md")), "risk-ledger.md must exist"

    @pytest.mark.parametrize("profile", ["prime", "builder", "auditor"])
    def test_profile_soul_exists(self, profile):
        path = os.path.join(ROOT, "profiles", profile, "SOUL.md")
        assert os.path.exists(path), f"profiles/{profile}/SOUL.md must exist"

    @pytest.mark.parametrize("profile", ["prime", "builder", "auditor"])
    def test_profile_config_exists(self, profile):
        path = os.path.join(ROOT, "profiles", profile, "config.yaml")
        assert os.path.exists(path), f"profiles/{profile}/config.yaml must exist"

    @pytest.mark.parametrize("skill", ["advisory-standard", "digital-state", "premortem-plus"])
    def test_skill_exists(self, skill):
        path = os.path.join(ROOT, "skills", skill, "SKILL.md")
        assert os.path.exists(path), f"skills/{skill}/SKILL.md must exist"

    def test_install_script_exists(self):
        assert os.path.exists(os.path.join(ROOT, "scripts", "install.ps1")), "scripts/install.ps1 must exist"

    def test_install_simple_exists(self):
        assert os.path.exists(os.path.join(ROOT, "scripts", "install-simple.ps1")), "scripts/install-simple.ps1 must exist"

    def test_validate_script_exists(self):
        assert os.path.exists(os.path.join(ROOT, "scripts", "validate-final.ps1")), "scripts/validate-final.ps1 must exist"

    def test_uninstall_script_exists(self):
        assert os.path.exists(os.path.join(ROOT, "scripts", "uninstall.ps1")), "scripts/uninstall.ps1 must exist"

    def test_promote_to_review_exists(self):
        assert os.path.exists(os.path.join(ROOT, "scripts", "promote-to-review.sh")), "scripts/promote-to-review.sh must exist"

    def test_constitution_exists(self):
        assert os.path.exists(os.path.join(ROOT, "specs", "constitution.md")), "specs/constitution.md must exist"


class TestNoLegacyProfiles:
    """Legacy 5-agent profile directories must not exist."""

    @pytest.mark.parametrize("legacy", ["analyst", "researcher", "coder", "tester"])
    def test_legacy_profile_absent(self, legacy):
        path = os.path.join(ROOT, "profiles", legacy)
        assert not os.path.exists(path), f"Legacy profile '{legacy}' must not exist"


class TestDistributionConsistency:
    """distribution.yaml entries must map to real files or directories."""

    def test_owned_files_exist(self):
        entries = get_distribution_owned()
        assert len(entries) > 0, "distribution_owned must have entries"
        for entry in entries:
            path = os.path.join(ROOT, entry.replace("/", os.sep))
            assert os.path.exists(path), f"distribution_owned entry missing: {entry}"
