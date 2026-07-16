import os
import tempfile
import json
import pytest
import hashlib

from digital_state.core.engine import GovernanceKernel
from integrations.hermes.client import HermesClient

def test_hermes_client_simulated_lifecycle_success():
    """Verify that a compliant agent session successfully triggers all hooks and completes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Setup workspace options
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))
        
        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)
            
        # Copy standard agents registry and configs
        import shutil
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.copy(
            os.path.join(repo_root, ".specify", "agents.json"),
            os.path.join(specify_dir, "agents.json")
        )
        
        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-integration-test"
        
        # We need the feature to be in SPECIFICATION state
        assert kernel.get_feature_state(feature_id) == "SPECIFICATION"
        
        from tests.conftest import public_key_dict

        # The plugin now requires agent_key to be a real ECDSA P-256 identity dict
        # (not a plaintext string). Provide Prime's validated public-key identity.
        agent_key = public_key_dict("prime")
        
        client = HermesClient()
        client.set_mock_mode(False)
        assert client.is_mock() is False
        
        # Run simulated session loop
        res = client.run_simulated_session(tmpdir, feature_id, agent_key)
        assert res["status"] == "Success"

def test_hermes_client_unauthorized_deny():
    """Verify that an unauthorized agent session triggers a fail-safe deny."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))
        
        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)
            
        shutil_copy = True
        import shutil
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        shutil.copy(
            os.path.join(repo_root, ".specify", "agents.json"),
            os.path.join(specify_dir, "agents.json")
        )
        
        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-integration-test"
        
        # Attempt running with an invalid key / signature
        agent_key = {
            "key_id": "key-builder", # Builder trying to act as Prime / start session
            "role": "Builder",
            "signature": "key-builder-signed-invalid"
        }
        
        client = HermesClient()
        client.set_mock_mode(False)
        
        # The hook should fail-safe deny (SessionStartDenied or similar)
        # because the policy engine will reject Builder acting on Specification phase
        res = client.run_simulated_session(tmpdir, feature_id, agent_key)
        assert res["status"] == "LLMCallDenied" or res["status"] == "ToolCallDenied" or res["status"] == "SessionStartDenied"
