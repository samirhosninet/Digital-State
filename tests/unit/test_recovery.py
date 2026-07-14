import os
import tempfile
import json
import pytest

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import EvidenceError, GovernanceError
from digital_state.core.locking import FileLock


def test_boot_alignment_validation():
    """Verify that the bootstrap validator detects state/audit log drift on startup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        # 1. Start a feature and sign off spec
        kernel = GovernanceKernel(tmpdir, run_bootstrap=False)
        feature_id = "feat-recovery-test"

        spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
        serialized = json.dumps(spec_content, sort_keys=True)
        import hashlib
        spec_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        spec_sig = f"key-prime-signed-{spec_hash}"
        kernel.submit_spec_evidence(feature_id, "prime-agent", "specs/001-spec.md", 3, spec_sig)

        assert kernel.get_feature_state(feature_id) == "PLANNING"

        # 2. Corrupt state.json by setting the state to TASKS (which is out of sync with audit log PLANNING)
        state_path = os.path.join(specify_dir, "state.json")
        with open(state_path, "r", encoding="utf-8") as f:
            state_data = json.load(f)
        state_data["feature_states"][feature_id] = "TASKS"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=2)

        # 3. Booting a new kernel with run_bootstrap=True must fail because of alignment drift!
        with pytest.raises(EvidenceError) as exc:
            GovernanceKernel(tmpdir, run_bootstrap=True)
        assert "Log truncation detected" in str(exc.value) or "out of sync" in str(exc.value)


def test_stale_lock_cleanup_on_boot():
    """Verify that stale lock directories are deleted during startup validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        specify_dir = os.path.join(tmpdir, ".specify")
        os.makedirs(specify_dir)
        os.makedirs(os.path.join(specify_dir, "memory"))

        with open(os.path.join(specify_dir, "integration.json"), "w") as f:
            json.dump({"integration": "hermes"}, f)
        with open(os.path.join(specify_dir, "init-options.json"), "w") as f:
            json.dump({"feature_numbering": "sequential"}, f)

        # Create stale lock directory
        lock_dir = os.path.join(specify_dir, "governance.lock")
        os.makedirs(lock_dir)
        with open(os.path.join(lock_dir, "lock.json"), "w") as f:
            json.dump({"pid": 999999, "timestamp": 0.0}, f)

        assert os.path.exists(lock_dir)

        # Boot kernel (should run stale lock cleanup automatically during bootstrap check)
        kernel = GovernanceKernel(tmpdir, run_bootstrap=True)

        # The lock directory should have been cleaned up
        assert not os.path.exists(lock_dir)
