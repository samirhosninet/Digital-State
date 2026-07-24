# Digital State v1.17 — Parallel Concurrency Architecture Model

## 1. Overview
Digital State v1.17 introduces Git worktree-isolated parallel card execution across non-dependent Kanban task cards.

## 2. Worktree Sandboxing Architecture
- **Worktree Base Directory:** `.specify/worktrees/<card_id>/`
- **Isolated Branch Names:** `prime/task-<card_id>`
- **Lifecycle:**
  1. `WorktreeManager.create_worktree(card_id)` creates isolated branch from `HEAD`.
  2. `BuilderDispatcher.execute_card()` runs task within isolated directory.
  3. `AuditorVerifier.verify_card()` audits code changes and evidence bundle.
  4. `WorktreeManager.merge_and_cleanup(card_id)` merges branch back and cleans up worktree.

## 3. Dependency-Aware Scheduling
- Task cards with no mutual dependencies execute concurrently.
- Dependent task cards wait for prior card status `DONE`.
