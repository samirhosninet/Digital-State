import os
import shutil
import subprocess

from digital_state.core.exceptions import GovernanceError
from integrations.hermes.client import HermesClient
from digital_state.core.config import ConfigManager


class BootstrapValidator:
    """Validates the environment and workspace capabilities prior to execution."""

    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.hermes_client = HermesClient()

    def verify_hermes_availability(self) -> bool:
        """Verify that the Hermes Agent execution environment is available."""
        # Check via the client adapter self test
        return self.hermes_client.self_test()

    def verify_speckit_availability(self) -> bool:
        """Verify SpecKit CLI is installed and available in the environment."""
        # Find 'specify' in PATH or local local-bin
        if shutil.which("specify"):
            return True
        
        # Check standard user local bin (Windows default setup)
        local_bin = os.path.expanduser(r"~\.local\bin\specify")
        if os.path.exists(local_bin) or os.path.exists(local_bin + ".exe"):
            return True

        # Check if specify runs via python module or shell fallback
        try:
            result = subprocess.run(
                ["specify", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def verify_runtime_adapter_readiness(self) -> bool:
        """Verify the runtime adapter can retrieve version metadata."""
        meta = self.hermes_client.metadata()
        return meta.get("status") == "Ready"

    def verify_workspace_readiness(self) -> bool:
        """Verify the workspace has the standard SpecKit setup (.specify directory)."""
        try:
            config = ConfigManager(self.workspace_root)
            # Try loading init options
            config.load_init_options()
            return True
        except Exception:
            return False

    def run_bootstrap(self) -> None:
        """Runs all checks sequentially, failing early with GovernanceError if check fails."""
        if not self.verify_workspace_readiness():
            raise GovernanceError("Bootstrap Failure: Workspace not initialized with .specify structure.")

        if not self.verify_hermes_availability():
            raise GovernanceError("Bootstrap Failure: Hermes Agent runtime is unavailable or failing self-test.")

        if not self.verify_speckit_availability():
            raise GovernanceError("Bootstrap Failure: SpecKit CLI execution path not found.")

        if not self.verify_runtime_adapter_readiness():
            raise GovernanceError("Bootstrap Failure: Hermes runtime adapter initialization failed.")
