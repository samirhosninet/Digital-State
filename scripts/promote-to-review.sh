#!/usr/bin/env bash
# promote-to-review.sh — Promote a blocked (review-required) Kanban card to native review status
#
# Usage: bash scripts/promote-to-review.sh <card_id> [kanban_db_path]
#
# This script implements the canonical Phase B handoff (Constitution Article XIV):
#   - Builder blocks with reason="review-required: ..."
#   - Prime (or operator) runs this script to promote the same card to status='review'
#   - Hermes dispatcher auto-spawns auditor on the same card
#
# This is a CLI wrapper for the direct DB write that workers cannot perform
# through the kanban_* tool surface (no kanban_set_status tool exists).
#
# RISK-001 mitigation — replaces raw SQL with a documented CLI command.

set -euo pipefail

CARD_ID="${1:?Usage: promote-to-review.sh <card_id> [kanban_db_path]}"
KANBAN_DB="${2:-}"

# Resolve kanban.db path
if [ -z "$KANBAN_DB" ]; then
    # Try HERMES_HOME first, then common locations
    if [ -n "${HERMES_HOME:-}" ]; then
        KANBAN_DB="$HERMES_HOME/kanban.db"
    elif [ -n "${LOCALAPPDATA:-}" ]; then
        # Windows (MSYS/Git Bash) — convert to Unix path
        KANBAN_DB="$(cygpath -u "$LOCALAPPDATA/hermes/kanban.db" 2>/dev/null || echo "/c/Users/$USER/AppData/Local/hermes/kanban.db")"
    elif [ -d "$HOME/.hermes" ]; then
        KANBAN_DB="$HOME/.hermes/kanban.db"
    else
        echo "ERROR: Cannot locate kanban.db. Pass path as second argument." >&2
        echo "Usage: promote-to-review.sh <card_id> <kanban_db_path>" >&2
        exit 1
    fi
fi

if [ ! -f "$KANBAN_DB" ]; then
    echo "ERROR: kanban.db not found at: $KANBAN_DB" >&2
    exit 1
fi

# Verify card exists and is in a promotable state
CURRENT_STATUS=$(sqlite3 "$KANBAN_DB" "SELECT status FROM tasks WHERE id = '$CARD_ID';" 2>/dev/null || echo "")

if [ -z "$CURRENT_STATUS" ]; then
    echo "ERROR: Card $CARD_ID not found in kanban.db" >&2
    exit 1
fi

if [ "$CURRENT_STATUS" != "blocked" ]; then
    echo "ERROR: Card $CARD_ID is in status='$CURRENT_STATUS', expected 'blocked'. Only blocked cards can be promoted to review." >&2
    exit 1
fi

# Verify the block reason contains "review-required"
BLOCK_REASON=$(sqlite3 "$KANBAN_DB" "SELECT reason FROM task_events WHERE task_id = '$CARD_ID' AND event_type = 'blocked' ORDER BY created_at DESC LIMIT 1;" 2>/dev/null || echo "")

if [ -n "$BLOCK_REASON" ] && echo "$BLOCK_REASON" | grep -qi "review-required"; then
    echo "INFO: Card $CARD_ID blocked with review-required reason: $BLOCK_REASON"
else
    echo "WARNING: Card $CARD_ID is blocked but block reason does not contain 'review-required'." >&2
    echo "Block reason: ${BLOCK_REASON:-<none>}" >&2
    echo "Proceeding with promotion anyway (operator override)..."
fi

# Perform the canonical promotion (Constitution Article XIV):
#   1. Set status='review', assignee='auditor'
#   2. Release any stale claim (claim_lock=NULL, claim_expires=NULL)
#   3. Record transition event
echo "Promoting card $CARD_ID: blocked → review, assignee → auditor"

sqlite3 "$KANBAN_DB" <<SQL
-- Atomic promotion transaction
BEGIN TRANSACTION;

-- Update card status and assignee
UPDATE tasks
SET status = 'review',
    assignee = 'auditor',
    claim_lock = NULL,
    claim_expires = NULL
WHERE id = '$CARD_ID';

-- Record transition event
INSERT INTO task_events (task_id, event_type, old_status, new_status, old_assignee, new_assignee, created_at)
SELECT '$CARD_ID', 'transitioned', 'blocked', 'review',
       (SELECT assignee FROM tasks WHERE id = '$CARD_ID'),
       'auditor',
       datetime('now')
WHERE changes() > 0;

COMMIT;
SQL

PROMOTE_EXIT=$?

if [ $PROMOTE_EXIT -eq 0 ]; then
    NEW_STATUS=$(sqlite3 "$KANBAN_DB" "SELECT status FROM tasks WHERE id = '$CARD_ID';" 2>/dev/null || echo "unknown")
    NEW_ASSIGNEE=$(sqlite3 "$KANBAN_DB" "SELECT assignee FROM tasks WHERE id = '$CARD_ID';" 2>/dev/null || echo "unknown")
    echo "SUCCESS: Card $CARD_ID promoted to status='$NEW_STATUS', assignee='$NEW_ASSIGNEE'"
    echo "The Hermes dispatcher will auto-spawn the auditor profile for this card."
    echo ""
    echo "Next steps:"
    echo "  1. Ensure Hermes gateway is running (for auto-spawn) OR"
    echo "  2. Manually hand off to auditor profile via: hermes -p auditor chat"
    echo ""
    echo "Record this promotion on the card via:"
    echo "  hermes kanban comment $CARD_ID --body 'Promoted from blocked to review by operator via promote-to-review.sh'"
else
    echo "ERROR: DB write failed for card $CARD_ID" >&2
    exit 1
fi
