import os
import time
import json

from kernel.exceptions import GovernanceError


class LockTimeoutError(GovernanceError):
    """Raised when process fails to acquire the transactional lock before timeout."""
    pass


class FileLock:
    """Exclusive directory-based lock supporting cross-platform PID checks and retries."""

    def __init__(self, lock_dir: str, timeout: float = 5.0, retry_delay: float = 0.1):
        self.lock_dir = lock_dir
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.is_locked = False

    def acquire(self) -> None:
        """Acquires lock atomically. Retries until timeout, recovering from stale processes."""
        start_time = time.time()
        while True:
            try:
                # Atomically create directory
                os.makedirs(self.lock_dir)

                # Write PID ownership metadata
                metadata_path = os.path.join(self.lock_dir, "lock.json")
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "pid": os.getpid(),
                        "timestamp": time.time()
                    }, f)

                self.is_locked = True
                return
            except FileExistsError:
                # Check lock metadata for stale lock
                metadata_path = os.path.join(self.lock_dir, "lock.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        pid = data.get("pid")
                        if pid and not self._is_pid_active(pid):
                            # Stale lock recovery
                            self.release()
                            continue
                    except Exception:
                        pass

                if time.time() - start_time >= self.timeout:
                    raise LockTimeoutError(
                        f"Failed to acquire lock on '{self.lock_dir}' within {self.timeout}s."
                    )

                time.sleep(self.retry_delay)

    def release(self) -> None:
        """Releases the lock, removing metadata file and directory."""
        try:
            metadata_path = os.path.join(self.lock_dir, "lock.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            if os.path.exists(self.lock_dir):
                os.rmdir(self.lock_dir)
        except Exception:
            pass
        self.is_locked = False

    def _is_pid_active(self, pid: int) -> bool:
        """Verify if process PID is active on the host."""
        if pid == os.getpid():
            return True
        try:
            if os.name != "nt":
                import signal
                os.kill(pid, 0)
                return True
            else:
                import ctypes
                PROCESS_QUERY_INFORMATION = 0x0400
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, False, pid)
                if handle == 0:
                    return False
                kernel32.CloseHandle(handle)
                return True
        except OSError:
            return False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
