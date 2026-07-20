import os
import sys
import tempfile
import subprocess
import shutil
import pytest

def test_end_to_end_installation():
    """Verify the end-to-end installation journey: clean workspace -> install -> init -> doctor -> success."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Simulate a clean clone by copying project files (excluding venv, specifying cache, etc.)
        src_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        dest_root = tmpdir
        
        # Copy package code
        shutil.copytree(os.path.join(src_root, "src"), os.path.join(dest_root, "src"))
        shutil.copytree(os.path.join(src_root, "framework"), os.path.join(dest_root, "framework"))
        shutil.copytree(os.path.join(src_root, "integrations"), os.path.join(dest_root, "integrations"))
        shutil.copytree(os.path.join(src_root, "governance"), os.path.join(dest_root, "governance"))
        
        # Copy installer scripts and config files
        shutil.copy(os.path.join(src_root, "pyproject.toml"), os.path.join(dest_root, "pyproject.toml"))
        shutil.copy(os.path.join(src_root, "install.ps1"), os.path.join(dest_root, "install.ps1"))
        shutil.copy(os.path.join(src_root, "install.sh"), os.path.join(dest_root, "install.sh"))
        
        # Verify clean workspace has no .specify folder
        assert not os.path.exists(os.path.join(dest_root, ".specify"))
        
        # 2. Execute the Windows installer script (install.ps1)
        # Note: Since the installer installs the package globally/venv in editable mode,
        # we run it within the current context python setup.
        # To avoid altering the global system environment during tests, we can call the CLI
        # module directly on the temp workspace to simulate the installer's bootstrap step.
        # Isolate the Runtime to a temp dir for this test (ADR-011-01: DIGITAL_STATE_HOME).
        # The Runtime root is provided by the autouse `isolate_runtime_home`
        # fixture (a real Windows path under pytest tmp_path). We let the
        # subprocess inherit that isolated DIGITAL_STATE_HOME rather than
        # overriding it with a git-bash /tmp path, which resolves inconsistently
        # on Windows and breaks the parent/child manifest check below.
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{os.path.join(dest_root, 'src')};{dest_root}"

        result_init = subprocess.run(
            [sys.executable, "-m", "digital_state.cli.cli", "init"],
            cwd=dest_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        assert "FULLY INTEGRATED" in result_init.stdout
        
        # Verify .specify structure was created
        specify_dir = os.path.join(dest_root, ".specify")
        assert os.path.exists(specify_dir)
        assert os.path.exists(os.path.join(specify_dir, "integration.json"))
        assert os.path.exists(os.path.join(specify_dir, "init-options.json"))
        # Per ADR-011-06 the Workspace must NEVER become the authoritative identity
        # store; `init` does NOT create agents.json. Identities live in the Runtime
        # (Digital State Runtime at DIGITAL_STATE_HOME), which `init` bootstraps.
        assert not os.path.exists(os.path.join(specify_dir, "agents.json"))
        assert os.path.exists(os.path.join(specify_dir, "state.json"))
        assert os.path.exists(os.path.join(specify_dir, "memory", "audit_log.jsonl"))
        # Runtime bootstrapped by init (governance state ready). The Runtime root
        # is the isolated DIGITAL_STATE_HOME from the autouse fixture.
        rt_root = os.environ.get("DIGITAL_STATE_HOME")
        if rt_root:
            assert os.path.exists(os.path.join(rt_root, "manifest.json"))
        
        # 3. Execute doctor verification
        # Set PYTHONPATH so that python can import the package in the temporary directory
        env = os.environ.copy()
        env["PYTHONPATH"] = f"{os.path.join(dest_root, 'src')};{dest_root}"
        # Inherit the fixture-isolated DIGITAL_STATE_HOME (do not override with a
        # git-bash /tmp path — see init block above).
        
        result_doctor = subprocess.run(
            [sys.executable, "-m", "digital_state.cli.cli", "doctor"],
            cwd=dest_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        import json
        report = json.loads(result_doctor.stdout)
        
        print("DOCTOR STDOUT:", result_doctor.stdout)
        print("DOCTOR STDERR:", result_doctor.stderr)
        assert report["overall_status"] == "PASS"
        assert report["installation"]["status"] == "PASS"
        assert report["configuration"]["status"] == "PASS"
        assert report["governance"]["status"] == "PASS"
        assert report["hermes"]["is_mock_adapter"] is False  # Verify Hermes boundary is LIVE
