"""Version synchronization tests for Digital State.

Verifies that the version string is consistent across all governance files,
matching the canonical version in distribution.yaml.
"""
import re
import os
import pytest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
DISTRIBUTION_YAML = os.path.join(ROOT, "distribution.yaml")


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def get_distribution_version() -> str:
    """Extract version from distribution.yaml (the canonical source)."""
    content = read_file(DISTRIBUTION_YAML)
    match = re.search(r"^version:\s*['\"]?([\d.]+)['\"]?", content, re.MULTILINE)
    if not match:
        pytest.fail(f"Cannot extract version from {DISTRIBUTION_YAML}")
    return match.group(1)


@pytest.fixture
def dist_version():
    return get_distribution_version()


# --- Files that carry the version in YAML frontmatter ---
FRONTMATTER_FILES = [
    "CHANGELOG.md",
    "PACKAGE.md",
    "profiles/prime/SOUL.md",
    "profiles/builder/SOUL.md",
    "profiles/auditor/SOUL.md",
]

# --- Files that carry the version in body text ---
BODY_VERSION_FILES = [
    "README.md",  # version mentioned in body / quick-start
]


class TestVersionSync:
    """All version strings across the package must match distribution.yaml."""

    def test_distribution_yaml_has_version(self, dist_version):
        assert dist_version, "distribution.yaml must define a version"
        # Must be a valid semver-like string
        assert re.match(r"\d+\.\d+\.\d+", dist_version), f"Invalid version format: {dist_version}"

    @pytest.mark.parametrize("relpath", FRONTMATTER_FILES)
    def test_frontmatter_version_matches(self, dist_version, relpath):
        path = os.path.join(ROOT, relpath)
        if not os.path.exists(path):
            pytest.skip(f"{relpath} not found")
        content = read_file(path)
        match = re.search(r"^version:\s*['\"]?([\d.]+)['\"]?", content, re.MULTILINE)
        assert match, f"No version in frontmatter of {relpath}"
        assert match.group(1) == dist_version, (
            f"{relpath} version={match.group(1)} != distribution.yaml version={dist_version}"
        )

    @pytest.mark.parametrize("relpath", BODY_VERSION_FILES)
    def test_body_version_matches(self, dist_version, relpath):
        """README.md and similar files should reference the current version."""
        path = os.path.join(ROOT, relpath)
        if not os.path.exists(path):
            pytest.skip(f"{relpath} not found")
        content = read_file(path)
        # Look for version string in body
        assert dist_version in content, (
            f"{relpath} does not reference version {dist_version}"
        )
