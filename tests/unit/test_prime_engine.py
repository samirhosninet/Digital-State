"""Unit Test Suite for Prime Operating Model Engine & Subsystems (v2.0).

Tests:
1. KanbanEngine tasks.md parsing & board.json compilation.
2. Unblocked card dispatch algorithm.
3. Card state transitions (TODO -> IN_PROGRESS -> IN_REVIEW -> DONE).
4. SpecKitRunner programmatically generating artifacts.
5. BuilderDispatcher & AuditorVerifier execution and hash-chain audit logging.
6. PrimeOrchestrator 8-phase lifecycle execution & resume_from_checkpoint().
7. CLI 'digitalstate prime' execution flow.
"""

import json
from pathlib import Path
import pytest

from digital_state.prime.kanban_engine import KanbanEngine, KanbanCard
from digital_state.prime.orchestrator import PrimeOrchestrator, LifecycleState
from digital_state.prime.speckit_runner import SpecKitRunner
from digital_state.prime.agent_dispatcher import BuilderDispatcher, AuditorVerifier
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


def test_speckit_runner_generation(tmp_path):
    """Verify SpecKitRunner generates spec.md, plan.md, checklist.md, tasks.md."""
    runner = SpecKitRunner(tmp_path)
    res = runner.run_pipeline("Build user auth service")

    assert res["status"] == "PASS"
    assert (tmp_path / "spec.md").exists()
    assert (tmp_path / "plan.md").exists()
    assert (tmp_path / "checklist.md").exists()
    assert (tmp_path / "tasks.md").exists()


def test_builder_and_auditor_dispatchers(tmp_path):
    """Verify BuilderDispatcher executes card and AuditorVerifier audits card."""
    card = KanbanCard(card_id="TASK-999", title="Refactor logger module")

    b_disp = BuilderDispatcher(tmp_path)
    exec_res = b_disp.execute_card(card)
    assert exec_res["status"] == "IN_REVIEW"
    assert Path(exec_res["execution_file"]).exists()

    a_ver = AuditorVerifier(tmp_path)
    audit_res = a_ver.verify_card(card)
    assert audit_res["status"] == "PASS"
    assert audit_res["evidence_hash"].startswith("sha256_")
    assert Path(audit_res["audit_file"]).exists()


def test_prime_orchestrator_lifecycle_and_resume(tmp_path):
    """Verify PrimeOrchestrator executes all 8 phases automatically from prompt."""
    orchestrator = PrimeOrchestrator(tmp_path)
    res = orchestrator.run_full_project_lifecycle(
        prompt="Implement user authentication API"
    )

    assert res["status"] == "COMPLETED"
    assert res["state"] == LifecycleState.PROJECT_COMPLETE.value
    assert res["phase_1"]["status"] == "PASS"
    assert res["phase_3"]["status"] == "PASS"
    assert len(res["processed_cards"]) > 0

    # Test resume_from_checkpoint
    resume_res = orchestrator.resume_from_checkpoint()
    assert resume_res["status"] == "COMPLETED"


def test_cli_prime_command(tmp_path):
    """Verify CLI 'digitalstate prime' executes successfully."""
    rc = run_cli(
        ["prime", "--prompt", "Build feature X"], workspace_root=str(tmp_path)
    )
    assert rc == 0
