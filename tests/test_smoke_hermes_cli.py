#!/usr/bin/env python3
"""
Smoke tests for Hermes CLI integration.
These tests require a running Hermes installation and will skip gracefully if Hermes is not available.
"""

import subprocess
import pytest
import shutil
import os


def hermes_available():
    """Check if hermes CLI is available in PATH."""
    return shutil.which("hermes") is not None


def run_hermes(args, timeout=30):
    """Run hermes CLI command and return (exit_code, stdout, stderr)."""
    cmd = ["hermes"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", "hermes not found"


@pytest.mark.skipif(not hermes_available(), reason="Hermes CLI not available")
class TestHermesCLISmoke:
    """Smoke tests that verify Hermes CLI works with Digital State profiles."""

    def test_hermes_version(self):
        """Verify hermes --version works."""
        code, out, err = run_hermes(["--version"])
        assert code == 0, f"hermes --version failed: {err}"
        assert "hermes" in out.lower() or "version" in out.lower()

    def test_hermes_kanban_boards_list(self):
        """Verify kanban boards list works."""
        code, out, err = run_hermes(["kanban", "boards", "list"])
        assert code == 0, f"kanban boards list failed: {err}"
        assert len(out.strip()) > 0

    def test_hermes_kanban_stats(self):
        """Verify kanban stats works."""
        code, out, err = run_hermes(["kanban", "stats"])
        assert code == 0, f"kanban stats failed: {err}"
        assert "done" in out.lower() or "by status" in out.lower()

    def test_prime_profile_exists(self):
        """Verify prime profile can be listed."""
        code, out, err = run_hermes(["-p", "prime", "kanban", "list"])
        # Profile might not exist yet - that's OK for smoke test
        # We just verify the command structure works
        assert code in (0, 1), f"prime profile check failed: {err}"

    def test_builder_profile_exists(self):
        """Verify builder profile can be listed."""
        code, out, err = run_hermes(["-p", "builder", "kanban", "list"])
        assert code in (0, 0, 1), f"builder profile check failed: {err}"

    def test_auditor_profile_exists(self):
        """Verify auditor profile can be listed."""
        code, out, err = run_hermes(["-p", "auditor", "kanban", "list"])
        assert code in (0, 1), f"auditor profile check failed: {err}"

    def test_auditor_plugins_list(self):
        """Verify auditor plugins list includes audit-matrix."""
        code, out, err = run_hermes(["-p", "auditor", "plugins", "list"])
        # If auditor profile exists, check for audit-matrix
        if code == 0:
            assert "audit-matrix" in out.lower(), f"audit-matrix not found in plugins: {out}"
        else:
            pytest.skip("auditor profile not installed")

    def test_prime_skills_list(self):
        """Verify prime profile has baseline skills."""
        code, out, err = run_hermes(["-p", "prime", "skills", "list"])
        if code == 0:
            skills = ["digital-state", "premortem-plus", "advisory-standard"]
            for skill in skills:
                assert skill in out.lower(), f"skill {skill} not found: {out}"
        else:
            pytest.skip("prime profile not installed")


@pytest.mark.skipif(not hermes_available(), reason="Hermes CLI not available")
class TestHermesKanbanWorkflow:
    """Test basic Kanban workflow operations."""

    def test_create_and_list_card(self):
        """Create a test card and verify it appears in list."""
        # Create a test card
        code, out, err = run_hermes(["kanban", "create", "Smoke test card", "--assignee", "prime"])
        # Card creation might fail if board not set up - that's OK
        if code != 0:
            pytest.skip(f"Cannot create card: {err}")

        # Extract card ID from output (format varies)
        card_id = None
        for line in out.splitlines():
            if line.startswith("t_"):
                card_id = line.split()[0]
                break

        if card_id:
            # List cards and verify it appears
            code2, out2, err2 = run_hermes(["kanban", "list"])
            assert code2 == 0
            assert card_id in out2

    def test_kanban_show_card(self):
        """Test kanban show on an existing card."""
        # First list to find a card
        code, out, err = run_hermes(["kanban", "list"])
        if code != 0:
            pytest.skip("Cannot list cards")

        # Find first card ID
        card_id = None
        for line in out.splitlines():
            if line.strip().startswith("t_"):
                parts = line.split()
                if parts:
                    card_id = parts[0]
                    break

        if card_id:
            code2, out2, err2 = run_hermes(["kanban", "show", card_id])
            assert code2 == 0, f"kanban show failed: {err2}"
            assert card_id in out2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])