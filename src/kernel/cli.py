import argparse
import json
import sys
import os
from typing import List

from kernel.engine import GovernanceKernel
from kernel.exceptions import GovernanceError


def create_parser() -> argparse.ArgumentParser:
    """Configures the command line parser mapping the technology-agnostic commands schema."""
    parser = argparse.ArgumentParser(prog="digitalstate", description="Digital State Governance CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. register command
    reg_parser = subparsers.add_parser("register", help="Register a new agent profile.")
    reg_parser.add_argument("--id", required=True, help="Unique identifier for the agent.")
    reg_parser.add_argument("--role", required=True, help="Assigned governance profile (Prime/Builder/Auditor).")
    reg_parser.add_argument("--key", required=True, help="Verification public key credential.")

    # 2. status command
    status_parser = subparsers.add_parser("status", help="Inspect status and transition logs.")
    status_parser.add_argument("--feature", required=True, help="Target feature ID.")

    # 3. submit command
    sub_parser = subparsers.add_parser("submit", help="Submit verifiable gate evidence.")
    sub_parser.add_argument("--feature", required=True, help="Target feature ID.")
    sub_parser.add_argument("--gate", required=True, help="Target checkpoint gate name.")
    sub_parser.add_argument("--evidence", required=True, help="JSON string of evidence context containing 'signature'.")
    sub_parser.add_argument("--agent", required=True, help="Submitting agent ID.")

    # 4. approve command
    app_parser = subparsers.add_parser("approve", help="Approve a gate transition.")
    app_parser.add_argument("--feature", required=True, help="Target feature ID.")
    app_parser.add_argument("--gate", required=True, help="Target gate being approved.")
    app_parser.add_argument("--agent", required=True, help="Approving agent ID.")

    # 5. reject command
    rej_parser = subparsers.add_parser("reject", help="Veto a gate transition.")
    rej_parser.add_argument("--feature", required=True, help="Target feature ID.")
    rej_parser.add_argument("--gate", required=True, help="Target gate being vetoed.")
    rej_parser.add_argument("--reason", required=True, help="Explanation of veto decision.")
    rej_parser.add_argument("--agent", required=True, help="Vetoing agent ID.")

    return parser


def run_cli(args_list: List[str], workspace_root: str = ".") -> int:
    """Executes the CLI commands routing payload inputs to the Governance Kernel."""
    parser = create_parser()
    try:
        args = parser.parse_args(args_list)
    except SystemExit as e:
        return e.code

    try:
        # Initialize the kernel pointing to current workspace
        # Turn off bootstrap verification during standalone command parse checks if requested
        kernel = GovernanceKernel(workspace_root, run_bootstrap=False)

        if args.command == "register":
            kernel.registry.register_agent(
                agent_id=args.id,
                role=args.role,
                permissions=["submit_evidence", "execute_tasks"],  # standard baseline
                public_key=args.key,
            )
            print(json.dumps({"status": "Success", "message": f"Agent '{args.id}' registered successfully."}))

        elif args.command == "status":
            current_state = kernel.get_feature_state(args.feature)
            
            # Fetch log history from audit trail
            history = []
            for entry in kernel.audit_logger.read_entries():
                if (
                    entry.get("event_type") == "STATE_TRANSITION"
                    and entry["details"].get("feature_id") == args.feature
                ):
                    history.append({
                        "timestamp": entry["timestamp"],
                        "from_state": entry["details"]["from_state"],
                        "to_state": entry["details"]["to_state"],
                        "agent_id": entry["agent_id"]
                    })
            
            output = {
                "feature_id": args.feature,
                "current_state": current_state,
                "history": history
            }
            print(json.dumps(output, indent=2))

        elif args.command == "submit":
            try:
                evidence_data = json.loads(args.evidence)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid --evidence JSON payload: {e}", file=sys.stderr)
                return 1

            signature = evidence_data.pop("signature", "")
            kernel.submit_evidence(
                feature_id=args.feature,
                gate=args.gate,
                content=evidence_data,
                agent_id=args.agent,
                signature=signature,
            )
            print(json.dumps({"status": "Success", "message": f"Evidence submitted for gate '{args.gate}'."}))

        elif args.command == "approve":
            kernel.approve_gate(
                feature_id=args.feature,
                gate=args.gate,
                agent_id=args.agent,
            )
            print(json.dumps({"status": "Success", "message": f"Gate '{args.gate}' approved transition."}))

        elif args.command == "reject":
            kernel.reject_gate(
                feature_id=args.feature,
                gate=args.gate,
                reason=args.reason,
                agent_id=args.agent,
            )
            print(json.dumps({"status": "Success", "message": f"Gate '{args.gate}' vetoed."}))

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run_cli(sys.argv[1:]))
