import os
import pytest


@pytest.fixture
def shared_contracts_dir() -> str:
    """Fixture pointing to the package core contracts directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    contracts_dir = os.path.join(current_dir, "..", "src", "digital_state", "core", "contracts")
    return os.path.abspath(contracts_dir)
