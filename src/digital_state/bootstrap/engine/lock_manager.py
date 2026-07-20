"""Cross-Process Concurrency Lock Manager (ECR-BOOTSTRAP-ARCHITECTURE-002).

Prevents race conditions by maintaining installer.lock cross-process locks.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional


class LockManager:
    """Manages installer.lock file lock for concurrency protection."""

    def __init__(self, lock_dir: Optional[Path] = None):
        if lock_dir:
            self.base_dir = Path(lock_dir)
        else:
            if sys.platform == "win32":
                local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
                self.base_dir = Path(local_appdata if local_appdata else os.path.expanduser(r"~\AppData\Local")) / "digital-state"
            else:
                self.base_dir = Path(os.path.expanduser("~/.digital-state"))

        self.lock_file = self.base_dir / "installer.lock"
        self._fd: Optional[int] = None

    def acquire(self, timeout_sec: float = 5.0) -> bool:
        """Acquires exclusive cross-process lock."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        start_time = time.time()
        while True:
            try:
                flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
                self._fd = os.open(str(self.lock_file), flags)
                os.write(self._fd, str(os.getpid()).encode("utf-8"))
                return True
            except OSError:
                if time.time() - start_time >= timeout_sec:
                    return False
                time.sleep(0.1)

    def release(self) -> None:
        """Releases lock file cleanly."""
        if self._fd is not None:
            try:
                os.close(self._fd)
            except Exception:
                pass
            self._fd = None
        if self.lock_file.exists():
            try:
                self.lock_file.unlink(missing_ok=True)
            except Exception:
                pass

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError("Could not acquire installer.lock (another installer process is running).")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
