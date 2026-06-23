"""
Shared test fixtures for Digital State test suite.
"""
import os
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def project_root():
    """Return the absolute path to the Digital State project root."""
    return PROJECT_ROOT


@pytest.fixture
def kanban_db_path():
    """Return the path to the live kanban.db."""
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "kanban.db")
