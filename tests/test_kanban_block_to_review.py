import os
import shutil
import sqlite3
import tempfile
import re

def test_kanban_block_to_review_promotion():
    """
    Test that a card blocked with reason 'review-required: ...' can be promoted to review status
    by a Prime-like action (direct database update) and then assigned to auditor.
    This test uses a temporary copy of the kanban database to avoid interfering with the main database.
    """
    # Path to the original kanban database
    original_db_path = r"C:\Users\seo\AppData\Local\hermes\kanban.db"
    # Create a temporary directory and copy the database there
    tmp_dir = tempfile.mkdtemp()
    try:
        tmp_db_path = os.path.join(tmp_dir, "kanban.db")
        shutil.copy2(original_db_path, tmp_db_path)
        
        # Set environment variable to use the temporary database
        env = os.environ.copy()
        env["HERMES_KANBAN_DB"] = tmp_db_path
        
        # We'll use the hermes command line tool. We assume it's in the PATH.
        import subprocess
        def run_hermes(*args):
            cmd = ["hermes"] + list(args)
            result = subprocess.run(cmd, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                raise RuntimeError(f"Command {' '.join(cmd)} failed with stderr: {result.stderr}")
            return result.stdout
        
        # Create a new card assigned to builder
        # Note: title is a positional argument, not a flag
        create_output = run_hermes("kanban", "create", "Test card for review promotion", "--assignee", "builder")
        # Parse the output to get the card ID. The output format is: "Created <card_id>  (status, assignee=builder)"
        # Example: "Created t_e17029a4  (ready, assignee=builder)"
        match = re.search(r"Created\s+(\S+)\s+", create_output)
        assert match, f"Could not parse card ID from output: {create_output}"
        card_id = match.group(1)
        
        # Block the card with reason "review-required: test"
        # The block command: hermes kanban block <task_id> [reason ...]
        run_hermes("kanban", "block", card_id, "review-required: test")
        
        # Verify the card is blocked and assigned to builder
        show_output = run_hermes("kanban", "show", card_id)
        # Check that the status line indicates blocked (allowing leading/trailing whitespace)
        assert re.search(r"^\s*status:\s*blocked\s*$", show_output, re.MULTILINE), f"Expected status blocked, got output: {show_output}"
        # Check that the assignee line indicates builder
        assert re.search(r"^\s*assignee:\s*builder\s*$", show_output, re.MULTILINE), f"Expected assignee builder, got output: {show_output}"
        
        # Now, simulate the Prime action: update the task to status='review', assignee='auditor', and clear the claim.
        # We'll do this by directly updating the SQLite database.
        conn = sqlite3.connect(tmp_db_path)
        try:
            cursor = conn.cursor()
            # Update the task: set status to 'review', assignee to 'auditor', and set claim_lock and claim_expires to NULL.
            cursor.execute("""
                UPDATE tasks 
                SET status = ?, assignee = ?, claim_lock = NULL, claim_expires = NULL
                WHERE id = ?
            """, ("review", "auditor", card_id))
            conn.commit()
            # Check that exactly one row was updated
            assert cursor.rowcount == 1, f"Expected to update 1 row, updated {cursor.rowcount}"
        finally:
            conn.close()
        
        # Now, check the state of the card after the update
        show_output = run_hermes("kanban", "show", card_id)
        # We expect: status=review, assignee=auditor, and claim_lock and claim_expires should be empty (or not present)
        # Check that the status line indicates review (allowing leading/trailing whitespace)
        assert re.search(r"^\s*status:\s*review\s*$", show_output, re.MULTILINE), f"Expected status review, got output: {show_output}"
        # Check that the assignee line indicates auditor
        assert re.search(r"^\s*assignee:\s*auditor\s*$", show_output, re.MULTILINE), f"Expected assignee auditor, got output: {show_output}"
        # Check that claim_lock and claim_expires are not set (they should be empty or not shown)
        # Instead, we can query the database again to be sure.
        conn = sqlite3.connect(tmp_db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT status, assignee, claim_lock, claim_expires FROM tasks WHERE id = ?", (card_id,))
            row = cursor.fetchone()
            assert row is not None, f"No row found for card_id {card_id}"
            status, assignee, claim_lock, claim_expires = row
            assert status == "review", f"Expected status 'review', got '{status}'"
            assert assignee == "auditor", f"Expected assignee 'auditor', got '{assignee}'"
            assert claim_lock is None, f"Expected claim_lock to be NULL, got '{claim_lock}'"
            assert claim_expires is None, f"Expected claim_expires to be NULL, got '{claim_expires}'"
        finally:
            conn.close()
    finally:
        # Clean up the temporary directory
        shutil.rmtree(tmp_dir, ignore_errors=True)