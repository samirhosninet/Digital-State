import argparse
import json
import sys
import os
from typing import List

from digital_state.core.engine import GovernanceKernel
from digital_state.core.exceptions import GovernanceError


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

    # 6. init command
    subparsers.add_parser("init", help="Initialize the governance workspace.")

    # 7. doctor command
    subparsers.add_parser("doctor", help="Verify the installation and integration state.")

    return parser


def run_cli(args_list: List[str], workspace_root: str = ".") -> int:
    """Executes the CLI commands routing payload inputs to the Governance Kernel."""
    parser = create_parser()
    try:
        args = parser.parse_args(args_list)
    except SystemExit as e:
        return e.code

    try:
        # Only instantiate the kernel if the command requires it
        kernel = None
        if args.command not in ("init", "doctor"):
            kernel = GovernanceKernel(workspace_root, run_bootstrap=False)

        if args.command == "init":
            specify_dir = os.path.join(workspace_root, ".specify")
            os.makedirs(specify_dir, exist_ok=True)
            os.makedirs(os.path.join(specify_dir, "memory"), exist_ok=True)
            
            # Idempotent & non-destructive file initialization
            integration_path = os.path.join(specify_dir, "integration.json")
            if not os.path.exists(integration_path):
                with open(integration_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "integration": "hermes",
                        "version": "0.1.0",
                        "installed_at": "2026-07-14T23:00:00.000000+00:00",
                        "files": {}
                    }, f, indent=2)
                    
            options_path = os.path.join(specify_dir, "init-options.json")
            if not os.path.exists(options_path):
                with open(options_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "ai": "hermes",
                        "ai_skills": True,
                        "feature_numbering": "sequential",
                        "here": True,
                        "integration": "hermes",
                        "script": "ps",
                        "speckit_version": "0.12.15.dev0"
                    }, f, indent=2)
                    
            agents_path = os.path.join(specify_dir, "agents.json")
            if not os.path.exists(agents_path):
                with open(agents_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=2)  # Empty agent registry for users to initialize
                    
            state_path = os.path.join(specify_dir, "state.json")
            if not os.path.exists(state_path):
                with open(state_path, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=2)
                    
            audit_log_path = os.path.join(specify_dir, "memory", "audit_log.jsonl")
            if not os.path.exists(audit_log_path):
                with open(audit_log_path, "w", encoding="utf-8") as f:
                    pass  # Create empty file
                    
            # Setup constitution.md file from standard baseline if it does not exist
            constitution_path = os.path.join(specify_dir, "memory", "constitution.md")
            if not os.path.exists(constitution_path):
                # Copy from template or source if exists, otherwise write minimal
                src_const = os.path.join(workspace_root, "governance", "CONSTITUTION_v1.md")
                if os.path.exists(src_const):
                    try:
                        import shutil
                        shutil.copy(src_const, constitution_path)
                    except Exception:
                        pass
                if not os.path.exists(constitution_path):
                    with open(constitution_path, "w", encoding="utf-8") as f:
                        f.write("# Digital State Constitution\n\n## Core Principles\n\n- Separation of Governance and Execution\n- Role Segregation\n- Immutable Accountability\n")

            print(json.dumps({"status": "Success", "message": "Digital State workspace initialized successfully."}))

        elif args.command == "doctor":
            # 1. Installation status
            python_version = sys.version
            import_ok = False
            crypto_version = "Unknown"
            try:
                import cryptography
                import_ok = True
                crypto_version = cryptography.__version__
            except ImportError:
                pass
                
            installation_status = {
                "python_version": python_version,
                "cryptography_imported": import_ok,
                "cryptography_version": crypto_version,
                "status": "PASS" if import_ok else "FAIL"
            }
            
            # 2. Configuration status
            specify_dir = os.path.join(workspace_root, ".specify")
            specify_exists = os.path.exists(specify_dir)
            files_check = {}
            for f_name in ["integration.json", "init-options.json", "agents.json", "state.json", "memory/audit_log.jsonl"]:
                files_check[f_name] = os.path.exists(os.path.join(specify_dir, f_name))
                
            config_ok = specify_exists and all(files_check.values())
            config_status = {
                "specify_dir_exists": specify_exists,
                "files_present": files_check,
                "status": "PASS" if config_ok else "FAIL"
            }
            
            # 3. Governance state status
            state_data = {}
            state_ok = False
            state_path = os.path.join(specify_dir, "state.json")
            if os.path.exists(state_path):
                try:
                    with open(state_path, "r", encoding="utf-8") as f:
                        state_data = json.load(f)
                    state_ok = True
                except Exception:
                    pass
            governance_status = {
                "state_readable": state_ok,
                "features_tracked": list(state_data.keys()),
                "status": "PASS" if state_ok else "FAIL"
            }
            
            # 4. Hermes integration status
            from integrations.hermes.client import HermesClient
            client = HermesClient()
            is_mock_adapter = client.is_mock()
            self_test_pass = client.self_test()
            try:
                meta = client.metadata()
                adapter_ready = meta.get("status") == "Ready"
            except Exception:
                meta = {}
                adapter_ready = False
                
            hermes_status = {
                "is_mock_adapter": is_mock_adapter,
                "connection_type": "MOCK" if is_mock_adapter else "LIVE",
                "self_test": "PASS" if self_test_pass else "FAIL",
                "adapter_ready": adapter_ready,
                "status": "WARNING" if is_mock_adapter else ("PASS" if self_test_pass and adapter_ready else "FAIL")
            }
            
            doctor_report = {
                "installation": installation_status,
                "configuration": config_status,
                "governance": governance_status,
                "hermes": hermes_status,
                "overall_status": "PASS" if (installation_status["status"] == "PASS" and config_status["status"] == "PASS" and governance_status["status"] == "PASS") else "FAIL"
            }
            print(json.dumps(doctor_report, indent=2))

        elif args.command == "register":
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


def main():
    """Main entrypoint for console scripts packaging."""
    sys.exit(run_cli(sys.argv[1:]))


if __name__ == "__main__":
    main()

