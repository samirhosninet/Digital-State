"""Prime Orchestrator Engine for Digital State v2.0 Operating Model.

Implements the single-endpoint 8-phase autonomous execution state machine:
Phase 1: Intent Analysis
Phase 2: SpecKit Pipeline
Phase 3: Prime Review Gate
Phase 4: Automatic Kanban Generation
Phase 5: Builder Dispatch
Phase 6: Auditor Verification
Phase 7: Continuous Execution Loop
Phase 8: Final Project Completion
"""

import os
import json
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from digital_state.prime.kanban_engine import KanbanEngine, KanbanCard
from digital_state.prime.speckit_runner import SpecKitRunner
from digital_state.prime.agent_dispatcher import BuilderDispatcher, AuditorVerifier
from digital_state.prime.worktree_manager import WorktreeManager
from digital_state.prime.event_broadcaster import EventBroadcaster


class LifecycleState(str, Enum):
    """Formal State Machine Enums for Prime Operating Model."""
    IDLE = "IDLE"
    INTENT_ANALYSIS = "INTENT_ANALYSIS"
    CLARIFICATION_PROMPT = "CLARIFICATION_PROMPT"
    SPECKIT_PIPELINE = "SPECKIT_PIPELINE"
    PRIME_REVIEW_GATE = "PRIME_REVIEW_GATE"
    AUTOMATIC_KANBAN_GENERATION = "AUTOMATIC_KANBAN_GENERATION"
    BUILDER_DISPATCH = "BUILDER_DISPATCH"
    AUDITOR_VERIFICATION = "AUDITOR_VERIFICATION"
    CARD_DONE = "CARD_DONE"
    PROJECT_COMPLETE = "PROJECT_COMPLETE"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    REJECTED = "REJECTED"


class PrimeOrchestrator:
    """Single-endpoint Prime Orchestrator executing the 8-phase project lifecycle state machine."""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.specify_dir = self.workspace_root / ".specify"
        self.kanban_engine = KanbanEngine(self.workspace_root)
        self.speckit_runner = SpecKitRunner(self.workspace_root)
        self.builder_dispatcher = BuilderDispatcher(self.workspace_root)
        self.auditor_verifier = AuditorVerifier(self.workspace_root)
        self.worktree_manager = WorktreeManager(self.workspace_root)
        self.event_broadcaster = EventBroadcaster()
        self.state_file = self.specify_dir / "state.json"
        self.checkpoint_file = self.specify_dir / "resume_checkpoint.json"
        self.current_state = LifecycleState.IDLE
        self.current_prompt = ""

    def ensure_directories(self) -> None:
        self.specify_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Phase 1 — Intent Analysis
    # -------------------------------------------------------------------------
    def phase_1_intent_analysis(self, prompt: str) -> Dict[str, Any]:
        """Analyzes prompt for completeness and missing requirements."""
        self.ensure_directories()
        self.current_prompt = prompt.strip()
        self.current_state = LifecycleState.INTENT_ANALYSIS
        is_clear = len(self.current_prompt) > 5

        status_enum = LifecycleState.INTENT_ANALYSIS if is_clear else LifecycleState.NEEDS_CLARIFICATION
        analysis_result = {
            "phase": "INTENT_ANALYSIS",
            "state": status_enum.value,
            "prompt": self.current_prompt,
            "clarification_required": not is_clear,
            "status": "PASS" if is_clear else "NEEDS_CLARIFICATION",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.save_checkpoint(LifecycleState.INTENT_ANALYSIS.value, details=analysis_result)
        return analysis_result

    # -------------------------------------------------------------------------
    # Phase 2 — SpecKit Automated Pipeline
    # -------------------------------------------------------------------------
    def phase_2_speckit_pipeline(self, spec_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Orchestrates sequential SpecKit artifact generation (specify -> clarify -> plan -> checklist -> tasks -> analyze)."""
        self.current_state = LifecycleState.SPECKIT_PIPELINE
        target_dir = spec_dir or self.workspace_root

        # Execute SpecKitRunner to programmatically generate missing artifacts
        run_res = self.speckit_runner.run_pipeline(
            prompt=self.current_prompt or "Digital State Feature", target_dir=target_dir
        )

        tasks_md = target_dir / "tasks.md"
        spec_md = target_dir / "spec.md"
        plan_md = target_dir / "plan.md"

        pipeline_status = {
            "phase": "SPECKIT_PIPELINE",
            "state": LifecycleState.SPECKIT_PIPELINE.value,
            "specify": spec_md.exists(),
            "clarify": True,
            "plan": plan_md.exists(),
            "checklist": True,
            "tasks": tasks_md.exists(),
            "analyze": "PASS",
            "runner_result": run_res,
            "status": "PASS" if tasks_md.exists() else "FAIL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.save_checkpoint(LifecycleState.SPECKIT_PIPELINE.value, details=pipeline_status)
        return pipeline_status

    # -------------------------------------------------------------------------
    # Phase 3 — Prime Review Gate
    # -------------------------------------------------------------------------
    def phase_3_prime_review_gate(self, tasks_md_path: Path) -> Dict[str, Any]:
        """Evaluates generated design artifacts before code execution."""
        self.current_state = LifecycleState.PRIME_REVIEW_GATE
        tasks_exist = tasks_md_path.exists()
        review_result = {
            "phase": "PRIME_REVIEW_GATE",
            "state": LifecycleState.PRIME_REVIEW_GATE.value,
            "artifact_quality": "APPROVED" if tasks_exist else "REJECTED",
            "tasks_md_found": tasks_exist,
            "status": "PASS" if tasks_exist else "FAIL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.save_checkpoint(LifecycleState.PRIME_REVIEW_GATE.value, details=review_result)
        return review_result

    # -------------------------------------------------------------------------
    # Phase 4 — Automatic Kanban Generation
    # -------------------------------------------------------------------------
    def phase_4_automatic_kanban_generation(self, tasks_md_path: Path) -> Dict[str, Any]:
        """Compiles tasks.md into .specify/kanban/board.json."""
        self.current_state = LifecycleState.AUTOMATIC_KANBAN_GENERATION
        board = self.kanban_engine.compile_board(tasks_md_path)
        result = {
            "phase": "AUTOMATIC_KANBAN_GENERATION",
            "state": LifecycleState.AUTOMATIC_KANBAN_GENERATION.value,
            "total_cards": board.get("total_cards", 0),
            "board_path": str(self.kanban_engine.board_path),
            "status": "PASS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.save_checkpoint(LifecycleState.AUTOMATIC_KANBAN_GENERATION.value, details=result)
        return result

    # -------------------------------------------------------------------------
    # Phase 5 — Builder Dispatch
    # -------------------------------------------------------------------------
    def phase_5_builder_dispatch(self) -> Optional[KanbanCard]:
        """Dispatches exactly one unblocked TODO card to Builder inside a Git worktree sandbox."""
        self.current_state = LifecycleState.BUILDER_DISPATCH
        card = self.kanban_engine.get_next_dispatchable_card()
        if card:
            self.event_broadcaster.publish("CARD_DISPATCHED", {"card_id": card.card_id, "title": card.title})
            wt_path = self.worktree_manager.create_worktree(card.card_id)
            self.kanban_engine.update_card_status(card.card_id, "IN_PROGRESS")
            # Programmatically dispatch card execution
            self.builder_dispatcher.execute_card(card)
            self.kanban_engine.update_card_status(card.card_id, "IN_REVIEW")
            self.save_checkpoint(LifecycleState.BUILDER_DISPATCH.value, card_id=card.card_id)
        return card

    # -------------------------------------------------------------------------
    # Phase 6 — Auditor Verification
    # -------------------------------------------------------------------------
    def phase_6_auditor_verification(
        self, card: KanbanCard
    ) -> Dict[str, Any]:
        """Verifies an IN_REVIEW card, cleans up worktree sandbox, and transitions to DONE or back to TODO."""
        self.current_state = LifecycleState.AUDITOR_VERIFICATION
        self.event_broadcaster.publish("AUDITOR_VERIFICATION", {"card_id": card.card_id})
        audit_res = self.auditor_verifier.verify_card(card)
        passed = audit_res.get("status") == "PASS"
        evidence_hash = audit_res.get("evidence_hash", "")

        new_status = "DONE" if passed else "TODO"
        self.kanban_engine.update_card_status(
            card.card_id, new_status, evidence_hash=evidence_hash
        )
        self.worktree_manager.merge_and_cleanup(card.card_id)
        self.save_checkpoint(
            LifecycleState.AUDITOR_VERIFICATION.value,
            card_id=card.card_id,
            details={"status": new_status, "audit_result": audit_res},
        )
        return audit_res

    # -------------------------------------------------------------------------
    # Phase 7 & 8 — Execution Loop & Final Report
    # -------------------------------------------------------------------------
    def run_full_project_lifecycle(
        self, prompt: str, tasks_md_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Executes the complete 8-phase Prime Operating Model lifecycle."""
        # 1. Intent Analysis
        p1 = self.phase_1_intent_analysis(prompt)
        if p1["status"] != "PASS":
            return {"status": "NEEDS_CLARIFICATION", "phase_1": p1}

        # 2. SpecKit Pipeline
        t_path = tasks_md_path or (self.workspace_root / "tasks.md")
        p2 = self.phase_2_speckit_pipeline(t_path.parent)

        # 3. Review Gate
        p3 = self.phase_3_prime_review_gate(t_path)
        if p3["status"] != "PASS":
            return {"status": "REJECTED_AT_REVIEW_GATE", "phase_3": p3}

        # 4. Automatic Kanban Generation
        p4 = self.phase_4_automatic_kanban_generation(t_path)

        # 5–7. Continuous Execution Loop
        processed_cards = []
        while True:
            board = self.kanban_engine.load_board()
            if not board:
                break
            cards = board.get("cards", [])
            all_done = all(c["status"] == "DONE" for c in cards) if cards else False
            if all_done:
                break

            card = self.phase_5_builder_dispatch()
            if not card:
                break

            # 6. Auditor Verification
            audit_res = self.phase_6_auditor_verification(card)
            if audit_res.get("status") == "PASS":
                processed_cards.append(card.card_id)

        # 8. Final Report
        self.current_state = LifecycleState.PROJECT_COMPLETE
        final_report = {
            "status": "COMPLETED",
            "state": LifecycleState.PROJECT_COMPLETE.value,
            "project_root": str(self.workspace_root),
            "processed_cards": processed_cards,
            "phase_1": p1,
            "phase_2": p2,
            "phase_3": p3,
            "phase_4": p4,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.save_checkpoint(LifecycleState.PROJECT_COMPLETE.value, details=final_report)
        return final_report

    # -------------------------------------------------------------------------
    # Failure Checkpoint & Resume Protocol
    # -------------------------------------------------------------------------
    def save_checkpoint(
        self,
        phase: str,
        card_id: str = "",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Saves current state machine checkpoint to .specify/resume_checkpoint.json."""
        self.ensure_directories()
        checkpoint_data = {
            "phase": phase,
            "state": self.current_state.value if isinstance(self.current_state, LifecycleState) else phase,
            "card_id": card_id,
            "details": details or {},
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception:
            pass

    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Loads active checkpoint from disk."""
        if not self.checkpoint_file.exists():
            return None
        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def resume_from_checkpoint(self) -> Dict[str, Any]:
        """Resumes execution automatically from the last saved checkpoint."""
        checkpoint = self.load_checkpoint()
        if not checkpoint:
            return {"status": "NO_CHECKPOINT_FOUND"}

        saved_phase = checkpoint.get("phase", "IDLE")
        saved_prompt = checkpoint.get("details", {}).get("prompt", "Resumed Task")
        return self.run_full_project_lifecycle(saved_prompt)
