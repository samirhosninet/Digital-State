"""Driver invoked as a SEPARATE process (so 'pytest' is NOT in sys.modules and the
installer's is_mock_test fast-path is not triggered). Performs a REAL install into
the HERMES_HOME passed via env and prints a JSON result to stdout."""
import os
import sys
import json
from pathlib import Path

REPO = Path(os.environ["DS_DRIVE_REPO"]).resolve()
sys.path.insert(0, str(REPO / "src"))

from digital_state.bootstrap.installer import BootstrapInstaller

ws = Path(os.environ["DS_DRIVE_WS"])
inst = BootstrapInstaller(workspace_root=ws)
res = inst.auto_configure_hermes()
print(json.dumps(res, default=str))
