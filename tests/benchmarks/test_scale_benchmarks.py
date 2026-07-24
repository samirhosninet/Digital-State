"""Scale Benchmark Suite for Digital State Prime Engine (v1.17).

Measures task parsing, scheduling performance, memory footprint, and audit overhead
across 100, 500, 1000, and 5000 cards.
"""

import time
import tracemalloc
from pathlib import Path
import pytest

from digital_state.prime.kanban_engine import KanbanEngine
from digital_state.core.audit import AuditLogger


def generate_large_tasks_md(output_path: Path, count: int) -> None:
    """Generates a tasks.md artifact with `count` dependency-ordered task cards."""
    lines = ["# Large Project Task List\n\n"]
    for i in range(1, count + 1):
        card_id = f"TASK-{i:04d}"
        dep = f" (requires [TASK-{i-1:04d}])" if i > 1 else ""
        lines.append(f"- [ ] [{card_id}] Execute scaled subtask {i}{dep}\n")

    output_path.write_text("".join(lines), encoding="utf-8")


@pytest.mark.parametrize("card_count", [100, 500, 1000, 5000])
def test_kanban_engine_scale_benchmark(tmp_path, card_count):
    """Stress-test KanbanEngine task parsing & compilation under heavy card loads."""
    tasks_md = tmp_path / f"tasks_{card_count}.md"
    generate_large_tasks_md(tasks_md, card_count)

    tracemalloc.start()
    t_start = time.perf_counter()

    engine = KanbanEngine(tmp_path)
    board = engine.compile_board(tasks_md)

    t_elapsed = time.perf_counter() - t_start
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert board["total_cards"] == card_count
    assert len(board["cards"]) == card_count

    print(
        f"\n[BENCHMARK] {card_count} Cards | Time: {t_elapsed*1000:.2f} ms | "
        f"Peak Memory: {peak_mem / 1024 / 1024:.2f} MB"
    )


def test_audit_logger_merkle_snapshot_benchmark(tmp_path):
    """Stress-test AuditLogger log rotation & Merkle root snapshotting."""
    log_path = tmp_path / "audit_log.jsonl"
    logger = AuditLogger(str(log_path))

    t_start = time.perf_counter()
    for i in range(1000):
        logger.append_entry("BENCHMARK_EVENT", "agent-bench", {"index": i})

    t_append = time.perf_counter() - t_start

    t_snap_start = time.perf_counter()
    snapshot = logger.create_merkle_snapshot()
    t_snap = time.perf_counter() - t_snap_start

    assert snapshot["total_entries"] == 1000
    assert len(snapshot["merkle_root"]) == 64

    print(
        f"\n[BENCHMARK] Audit Append (1000 events): {t_append*1000:.2f} ms | "
        f"Merkle Snapshot: {t_snap*1000:.2f} ms | Merkle Root: {snapshot['merkle_root'][:16]}..."
    )
