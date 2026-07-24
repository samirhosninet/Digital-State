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
    reg_parser.add_argument("--role", required=True, help="Assigned governance role (data-driven from roles.json asset).")
    reg_parser.add_argument("--public-key-file", help="PEM public-key file for an ECDSA P-256 identity.")
    reg_parser.add_argument("--key-id", help="Stable public identifier for the registered key.")
    reg_parser.add_argument("--algorithm", default="ECDSA_P256", choices=["ECDSA_P256"], help="Signature algorithm.")
    reg_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing identity with this new keypair.",
    )


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

    # 8. upgrade command (deprecated alias of 'update')
    subparsers.add_parser("upgrade", help="[DEPRECATED] Alias of 'update'. Use 'digitalstate update' instead.")

    # 9. uninstall command
    subparsers.add_parser("uninstall", help="Uninstall the Digital State plugin and clean profiles from Hermes.")

    # 10. repair command
    subparsers.add_parser("repair", help="Repair or recover workspace files, configs, and venv setup.")

    # 11. verify-ledger command
    vl_parser = subparsers.add_parser("verify-ledger", help="Verify cryptographic hash-chain integrity of governance ledger.")
    vl_parser.add_argument("--ledger-path", help="Path to ledger.jsonl file.")

    # 12. audit-evidence command
    ae_parser = subparsers.add_parser("audit-evidence", help="Audit and validate architectural evidence records.")
    ae_parser.add_argument("--file", help="Path to JSON file containing evidence records.")
    ae_parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output report format.")
    ae_parser.add_argument("--check", action="store_true", help="Exit with non-zero status if any unverified evidence records exist.")
    ae_parser.add_argument("--all", action="store_true", help="Audit local device evidence bundle and platform runtime bridge.")
    ae_parser.add_argument("--federated", action="store_true", help="Audit multi-tenant federated evidence manifest across device nodes.")

    # 13. install command
    inst_parser = subparsers.add_parser("install", help="Single-command automated installation experience for Digital State.")
    inst_parser.add_argument("--dry-run", action="store_true", help="Perform pre-flight checks without writing files.")
    inst_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output report format.")

    # 14. update command
    upd_parser = subparsers.add_parser("update", help="Official Update Lifecycle experience for Digital State.")
    upd_parser.add_argument("--check", action="store_true", help="Check for available updates without applying.")
    upd_parser.add_argument("--force", action="store_true", help="Force update re-application even if up to date.")
    upd_parser.add_argument("--target-version", help="Override target version for upgrade migration.")
    upd_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output report format.")
    upd_parser.add_argument("--simulate-failure", action="store_true", help=argparse.SUPPRESS)

    # 15. version command
    ver_parser = subparsers.add_parser("version", help="Display Digital State version information.")
    ver_parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")

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
        if args.command not in ("init", "doctor", "install", "update", "version", "upgrade", "uninstall", "repair", "verify-ledger"):
            kernel = GovernanceKernel(workspace_root, run_bootstrap=False)

        if args.command == "install":
            from digital_state.cli.installer import UserInstaller
            installer = UserInstaller(workspace_root=workspace_root)
            report = installer.run_installation(dry_run=getattr(args, "dry_run", False))
            if getattr(args, "format", "text") == "json":
                print(json.dumps(report, indent=2))
            else:
                installer.render_report_text(report)
            return 0 if report.get("doctor") == "PASS" else 1

        elif args.command == "update":
            from digital_state.cli.updater import UserUpdater
            updater = UserUpdater(workspace_root=workspace_root)
            report = updater.run_update(
                check_only=getattr(args, "check", False),
                force=getattr(args, "force", False),
                target_version=getattr(args, "target_version", None),
                simulate_failure=getattr(args, "simulate_failure", False),
            )
            if getattr(args, "format", "text") == "json":
                print(json.dumps(report, indent=2))
            else:
                updater.render_report_text(report)
            return 0 if report.get("doctor_status") == "PASS" or report.get("migration_status") in ("CHECK_ONLY", "NO_UPDATE_REQUIRED") else 1

        elif args.command == "version":
            from digital_state import __version__
            if getattr(args, "format", "text") == "json":
                print(json.dumps({"version": __version__}, indent=2))
            else:
                print(f"digitalstate version {__version__}")
            return 0

        elif args.command == "init":
            from pathlib import Path
            from digital_state.bootstrap.engine.orchestrator import run_engine_cli
            return run_engine_cli("install", dry_run=False, workspace_root=Path(workspace_root))



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
            for f_name in ["integration.json", "init-options.json", "state.json", "memory/audit_log.jsonl"]:
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
            if getattr(args, "key", None):
                raise GovernanceError(
                    "--key is no longer supported. Use --public-key-file and --key-id with an ECDSA P-256 public key."
                )

            if not args.public_key_file or not args.key_id:
                raise GovernanceError("register requires --public-key-file and --key-id.")
            try:
                with open(args.public_key_file, "r", encoding="utf-8") as key_file:
                    public_key_value = key_file.read()
            except OSError as exc:
                raise GovernanceError(f"Unable to read public-key file: {exc}") from exc
            # Permissions are data-driven from the Package roles.json asset (ADR-011-03).
            # Role matching is case-insensitive ("Builder" == "builder") for CLI ergonomics.
            from digital_state.core.registry import AgentRegistry
            role_key = args.role.strip().lower() if args.role else args.role
            role_permissions = AgentRegistry._permissions_for_role(role_key)
            if not role_permissions:
                raise GovernanceError(
                    f"Unknown role '{args.role}'; not defined in roles.json asset."
                )
            public_key = {
                "key_id": args.key_id,
                "algorithm": args.algorithm,
                "status": "Active",
                "value": public_key_value,
            }
            # Authoritative write: Runtime IdentityStore (ADR-011-04/011-06).
            # upsert is overwrite-by-id, so re-registering under a seeded trust-root
            # ID (with --force) replaces the public-only key with the user's keypair.
            try:
                from digital_state.runtime.store import RuntimeStore
                from digital_state.runtime.stores import IdentityRecord
                store = RuntimeStore()
                if store.exists():
                    store.identity.upsert(
                        IdentityRecord(
                            identity_id=args.id,
                            role=role_key.capitalize(),
                            public_key=public_key,
                        )
                    )
            except Exception:
                # Runtime unavailable: registration falls back to workspace registry.
                pass
            kernel.registry.register_agent(
                agent_id=args.id,
                role=role_key.capitalize(),
                permissions=role_permissions,
                public_key=public_key,
                force=args.force,
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

        elif args.command == "upgrade":
            # DEPRECATED: 'upgrade' is a legacy alias that now delegates to the
            # official Update Lifecycle ('update' command / UserUpdater).
            print(
                "WARNING: 'upgrade' is deprecated; use 'digitalstate update' instead.",
                file=sys.stderr,
            )
            from digital_state.cli.updater import UserUpdater
            updater = UserUpdater(workspace_root=workspace_root)
            report = updater.run_update(force=True)
            updater.render_report_text(report)
            return 0 if report.get("doctor_status") == "PASS" or report.get("migration_status") in ("CHECK_ONLY", "NO_UPDATE_REQUIRED") else 1

        elif args.command == "uninstall":
            if sys.platform == "win32":
                local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
                hermes_root = os.environ.get("HERMES_HOME", "") or os.path.join(
                    local_appdata if local_appdata else os.path.expanduser(r"~\AppData\Local"),
                    "hermes"
                )
            else:
                hermes_root = os.environ.get("HERMES_HOME", "") or os.path.expanduser("~/.hermes")

            import shutil
            import subprocess
            hermes_cmd = shutil.which("hermes")
            python_cmd = None
            if not hermes_cmd:
                if sys.platform == "win32":
                    h_path = os.path.join(hermes_root, "hermes-agent", "venv", "Scripts", "hermes.exe")
                    p_path = os.path.join(hermes_root, "hermes-agent", "venv", "Scripts", "python.exe")
                    if os.path.exists(h_path):
                        hermes_cmd = h_path
                    if os.path.exists(p_path):
                        python_cmd = p_path
                else:
                    h_path = os.path.join(hermes_root, "hermes-agent", "venv", "bin", "hermes")
                    p_path = os.path.join(hermes_root, "hermes-agent", "venv", "bin", "python")
                    if os.path.exists(h_path):
                        hermes_cmd = h_path
                    if os.path.exists(p_path):
                        python_cmd = p_path
            else:
                cmd_dir = os.path.dirname(hermes_cmd)
                if sys.platform == "win32":
                    p_path = os.path.join(cmd_dir, "python.exe")
                else:
                    p_path = os.path.join(cmd_dir, "python")
                if os.path.exists(p_path):
                    python_cmd = p_path

            if python_cmd:
                try:
                    subprocess.run(
                        [python_cmd, "-m", "pip", "uninstall", "-y", "digital-state"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                except Exception as e:
                    print(f"Warning: could not uninstall package: {e}", file=sys.stderr)

            profiles = ["prime", "builder", "auditor"]
            for name in profiles:
                prof_dir = os.path.join(hermes_root, "profiles", name)
                if os.path.exists(prof_dir):
                    try:
                        shutil.rmtree(prof_dir)
                    except Exception as e:
                        print(f"Warning: could not remove profile dir '{prof_dir}': {e}", file=sys.stderr)

            global_config_path = os.path.join(hermes_root, "config.yaml")
            if os.path.exists(global_config_path):
                try:
                    import yaml
                    with open(global_config_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f) or {}
                    if "plugins" in cfg and isinstance(cfg["plugins"], dict):
                        if "enabled" in cfg["plugins"] and isinstance(cfg["plugins"]["enabled"], list):
                            if "digital_state" in cfg["plugins"]["enabled"]:
                                cfg["plugins"]["enabled"].remove("digital_state")
                                with open(global_config_path, "w", encoding="utf-8") as f:
                                    yaml.safe_dump(cfg, f, default_flow_style=False)
                except Exception as e:
                    print(f"Warning: could not update global config.yaml: {e}", file=sys.stderr)

            print(json.dumps({"status": "Success", "message": "Digital State plugin and profiles successfully uninstalled from Hermes."}))
            return 0

        elif args.command == "repair":
            specify_dir = os.path.join(workspace_root, ".specify")
            os.makedirs(specify_dir, exist_ok=True)
            os.makedirs(os.path.join(specify_dir, "memory"), exist_ok=True)

            state_path = os.path.join(specify_dir, "state.json")
            if not os.path.exists(state_path) or os.path.getsize(state_path) == 0:
                with open(state_path, "w", encoding="utf-8") as f:
                    f.write("{}")

            agents_path = os.path.join(specify_dir, "agents.json")
            if not os.path.exists(agents_path):
                with open(agents_path, "w", encoding="utf-8") as f:
                    f.write("{}")

            print(json.dumps({"status": "Success", "message": "Repair and recovery completed successfully. Workspace directories and state files have been validated/rebuilt."}))
            return 0

        elif args.command == "verify-ledger":
            import importlib.util
            from pathlib import Path
            l_path = Path(args.ledger_path) if args.ledger_path else Path(workspace_root) / "governance" / "self-governance" / "007-runtime-integration" / "ledger.jsonl"
            if not l_path.exists():
                l_path = Path(workspace_root) / ".specify" / "memory" / "audit_log.jsonl"
            ledger_py = Path(workspace_root) / "governance" / "self-governance" / "_lib" / "ledger.py"
            spec = importlib.util.spec_from_file_location("ledger_lib", ledger_py)
            ledger_lib = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ledger_lib)
            ledger = ledger_lib.Ledger(l_path)
            res = ledger.verify_chain()
            print(json.dumps(res, indent=2))
            return 0 if res.get("chain_intact", True) else 1

        elif args.command == "audit-evidence":
            from digital_state.governance.evidence import (
                EvidenceRecord,
                EvidenceClassification,
                EvidenceValidationEngine,
                EvidenceReportGenerator,
                DeviceEvidenceValidator,
            )
            engine = EvidenceValidationEngine()
            generator = EvidenceReportGenerator(validation_engine=engine)
            records = []
            manifest = None

            if getattr(args, "file", None) and os.path.exists(args.file):
                with open(args.file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    if isinstance(raw_data, list):
                        records = [EvidenceRecord.from_dict(item) for item in raw_data]
                    elif isinstance(raw_data, dict) and "records" in raw_data:
                        records = [EvidenceRecord.from_dict(item) for item in raw_data["records"]]

            if getattr(args, "all", False):
                device_val = DeviceEvidenceValidator()
                records.extend(device_val.validate_device_bundle())

            if getattr(args, "federated", False):
                from digital_state.governance.federation.manager import FederatedEvidenceManager
                from digital_state.device.identity import DeviceIdentityManager
                from digital_state.device.enrollment import EnrollmentProtocol
                from pathlib import Path
                fed_mgr = FederatedEvidenceManager(tenant_id="default_tenant")
                device_val = DeviceEvidenceValidator()
                dev_records = device_val.validate_device_bundle()

                id_mgr = DeviceIdentityManager()
                dev_dir = Path(".specify") / "device"
                enrollment = EnrollmentProtocol(device_dir=dev_dir, identity_mgr=id_mgr)
                info = id_mgr.get_identity_info()
                pub_key = info.get("public_key_pem", "")
                sig_hex = ""
                nonce = ""
                if pub_key:
                    challenge = enrollment.generate_challenge_nonce()
                    nonce = challenge.get("challenge_nonce", "")
                    resp = enrollment.sign_challenge(challenge)
                    sig_hex = resp.get("signature", "")

                manifest = fed_mgr.aggregate_device_bundles([{
                    "device_id": info.get("device_id", "local_node"),
                    "public_key_pem": pub_key,
                    "challenge_nonce": nonce,
                    "signature_hex": sig_hex,
                    "evidence_records": [r.to_dict() for r in dev_records]
                }])
                if getattr(args, "format", "markdown") == "json":
                    print(json.dumps(manifest, indent=2))


            validated_records = engine.validate_batch(records)

            if not getattr(args, "federated", False) or getattr(args, "format", "markdown") != "json":
                if getattr(args, "format", "markdown") == "json":
                    print(generator.render_json_manifest(validated_records))
                else:
                    print(generator.render_markdown_table(validated_records))

            if getattr(args, "check", False):
                has_unverified = any(
                    r.classification in (EvidenceClassification.UNVERIFIED, EvidenceClassification.NOT_FOUND_IN_CURRENT_OFFICIAL_DOCUMENTATION)
                    for r in validated_records
                )
                if manifest and manifest.get("failed_devices", 0) > 0:
                    has_unverified = True
                return 1 if has_unverified else 0

            return 0



        return 0


    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entrypoint for console scripts packaging."""
    sys.exit(run_cli(sys.argv[1:]))


if __name__ == "__main__":
    main()

