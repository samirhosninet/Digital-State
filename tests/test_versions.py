"""
Version synchronization and concurrency cap tests for Digital State.
"""
import os
import re
import yaml


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPECTED_VERSION = "3.3.0"


def test_version_unity():
    """All 8 core files must share the same version string."""
    files = [
        "distribution.yaml",
        "README.md",
        "PACKAGE.md",
        "CHANGELOG.md",
        "profiles/prime/SOUL.md",
        "profiles/builder/SOUL.md",
        "profiles/auditor/SOUL.md",
    ]
    version_pattern = re.compile(r"version:\s*(\d+\.\d+\.\d+)")
    for rel in files:
        with open(os.path.join(PROJECT_ROOT, rel), "r", encoding="utf-8") as f:
            content = f.read()
        match = version_pattern.search(content)
        assert match is not None, f"Version not found in {rel}"
        assert match.group(1) == EXPECTED_VERSION, \
            f"{rel}: expected version {EXPECTED_VERSION}, got {match.group(1)}"


def test_concurrency_cap():
    """Each profile config.yaml must have kanban.max_in_progress_per_profile: 1."""
    for profile in ["prime", "builder", "auditor"]:
        config_path = os.path.join(PROJECT_ROOT, "profiles", profile, "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        kanban = config.get("kanban", {})
        assert kanban.get("max_in_progress_per_profile") == 1, \
            f"{profile}: kanban.max_in_progress_per_profile must be 1"


def test_digital_state_skill_version():
    """skills/digital-state/SKILL.md version must match package version."""
    skill_path = os.path.join(PROJECT_ROOT, "skills", "digital-state", "SKILL.md")
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"version:\s*(\d+\.\d+\.\d+)", content)
    assert match is not None, "Version not found in digital-state SKILL.md"
    assert match.group(1) == EXPECTED_VERSION, \
        f"digital-state SKILL.md: expected {EXPECTED_VERSION}, got {match.group(1)}"
