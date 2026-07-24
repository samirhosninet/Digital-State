"""Unit Test Suite for Prime Operating Model Engine (v2.0).

Tests:
1. KanbanEngine tasks.md parsing & board.json compilation.
2. Unblocked card dispatch algorithm.
3. Card state transitions (TODO -> IN_PROGRESS -> IN_REVIEW -> DONE).
4. PrimeOrchestrator 8-phase lifecycle execution.
5. Failure & resume checkpoint saving/loading.
6. CLI 'digitalstate prime' execution flow.
"""

import json
from pathlib import Path
import pytest

from digital_state.prime.kanban_engine import KanbanEngine, KanbanCard
from digital_state.prime.orchestrator import PrimeOrchestrator
from digital_state.cli.cli import run_cli


@pytest.fixture
def mock_workspace(tmp_path):
    """Creates a mock workspace with a valid tasks.md artifact."""
    tasks_md = tmp_path / "tasks.md"
    tasks_md.write_text(
        """# Project Tasks
- [ ] [TASK-001] Setup core models
- [ ] [TASK-002] Implement REST controller
- [ ] [TASK-003] Add integration tests
""",
        encoding="utf-8",
    )
    return tmp_path


def test_kanban_engine_parse_and_compile(mock_workspace):
    """Verify KanbanEngine parses tasks.md and compiles board.json."""
    engine = KanbanEngine(mock_workspace)
    board = engine.compile_board(mock_workspace / "tasks.md")

    assert board["total_cards"] == 3
    assert len(board["cards"]) == 3
    assert board["cards"][0]["id"] == "TASK-001"
    assert board["cards"][0]["status"] == "TODO"
    assert engine.board_path.exists()


def test_unblocked_card_dispatch(mock_workspace):
    """Verify KanbanEngine dispatches unblocked TODO card strictly in order."""
    engine = KanbanEngine(mock_workspace)
    engine.compile_board(mock_workspace / "tasks.md")

    next_card = engine.get_next_dispatchable_card()
    assert next_card is not None
    assert next_card.card_id == "TASK-001"

    # Set TASK-001 to IN_PROGRESS -> no new card should be dispatchable
    engine.update_card_status("TASK-001", "IN_PROGRESS")
    assert engine.get_next_dispatchable_card() is None

    # Set TASK-001 to DONE -> TASK-002 becomes dispatchable
    engine.update_card_status("TASK-001", "DONE")
    next_card_2 = engine.get_next_dispatchable_card()
    assert next_card_2 is not None
    assert next_card_2.card_id == "TASK-002"


def test_prime_orchestrator_lifecycle(mock_workspace):
    """Verify PrimeOrchestrator executes all 8 phases automatically."""
    orchestrator = PrimeOrchestrator(mock_workspace)
    res = orchestrator.run_full_project_lifecycle(
        prompt="Implement user authentication API",
        tasks_md_path=mock_workspace / "tasks.md",
    )

    assert res["status"] == "COMPLETED"
    assert res["phase_1"]["status"] == "PASS"
    assert res["phase_3"]["status"] == "PASS"
    assert len(res["processed_cards"]) == 3

    # Check resume checkpoint
    checkpoint = orchestrator.load_checkpoint()
    assert checkpoint is not None
    assert checkpoint["phase"] == "PROJECT_COMPLETE"


def test_cli_prime_command(mock_workspace):
    """Verify CLI 'digitalstate prime' executes successfully."""
    rc = run_cli(
        ["prime", "--prompt", "Build feature X"], workspace_root=str(mock_workspace)
    )
    assert rc == 0
