import os
import tempfile
import time
import pytest
import multiprocessing
import json

from digital_state.core.locking import FileLock, LockTimeoutError
from digital_state.core.exceptions import GovernanceError


def acquire_and_hold(lock_dir, duration, success_flag):
    """Worker function that acquires lock and holds it for a duration."""
    try:
        with FileLock(lock_dir, timeout=2.0) as lock:
            if lock.is_locked:
                success_flag.value = 1
                time.sleep(duration)
    except Exception:
        success_flag.value = -1


def test_lock_exclusivity():
    """Verify that only one process can hold the lock at a time."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_dir = os.path.join(tmpdir, "test.lock")
        success_a = multiprocessing.Value('i', 0)
        success_b = multiprocessing.Value('i', 0)

        # Process A holds the lock for 1 second
        proc_a = multiprocessing.Process(target=acquire_and_hold, args=(lock_dir, 1.0, success_a))
        proc_a.start()

        # Wait to ensure A has acquired the lock
        start = time.time()
        while success_a.value == 0 and time.time() - start < 5.0:
            time.sleep(0.05)

        # Process B attempts to acquire the lock (should fail/timeout since A holds it)
        proc_b = multiprocessing.Process(target=acquire_and_hold, args=(lock_dir, 0.5, success_b))
        proc_b.start()

        proc_a.join()
        proc_b.join()

        assert success_a.value == 1
        assert success_b.value == 1


def test_lock_timeout():
    """Verify that a process raises LockTimeoutError if the lock is held beyond timeout."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_dir = os.path.join(tmpdir, "test.lock")
        success_a = multiprocessing.Value('i', 0)

        # A holds lock for 3.0 seconds
        proc_a = multiprocessing.Process(target=acquire_and_hold, args=(lock_dir, 3.0, success_a))
        proc_a.start()

        # Wait to ensure A has acquired the lock
        start = time.time()
        while success_a.value == 0 and time.time() - start < 5.0:
            time.sleep(0.05)

        # Attempt to acquire with a timeout shorter than 3 seconds (must fail)
        lock = FileLock(lock_dir, timeout=1.0)
        with pytest.raises(LockTimeoutError):
            lock.acquire()

        proc_a.join()


def test_stale_lock_recovery():
    """Verify that stale locks left by inactive processes are recovered."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_dir = os.path.join(tmpdir, "test_stale.lock")

        # Manually create a stale lock with a dead PID (e.g. 999999)
        os.makedirs(lock_dir)
        metadata_path = os.path.join(lock_dir, "lock.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "pid": 999999,  # Non-existent/dead PID
                "timestamp": time.time()
            }, f)

        # A new FileLock must recover from this stale lock and acquire successfully
        lock = FileLock(lock_dir, timeout=2.0)
        lock.acquire()
        assert lock.is_locked is True
        lock.release()
