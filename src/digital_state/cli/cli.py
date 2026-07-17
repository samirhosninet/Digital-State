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
    reg_parser.add_argument("--key", help="Deprecated plaintext key option; always rejected.")

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

    # 8. upgrade command
    subparsers.add_parser("upgrade", help="Upgrade the Digital State package inside the Hermes virtualenv.")

    # 9. uninstall command
    subparsers.add_parser("uninstall", help="Uninstall the Digital State plugin and clean profiles from Hermes.")

    # 10. repair command
    subparsers.add_parser("repair", help="Repair or recover workspace files, configs, and venv setup.")

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
        if args.command not in ("init", "doctor", "upgrade", "uninstall", "repair"):
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
                    
            # Per ADR-011-06 the Workspace must NEVER become the authoritative
            # identity store. We no longer write an empty agents.json (the
            # empty-file trap, EV-2). Identities live in the Runtime.
            agents_path = os.path.join(specify_dir, "agents.json")
            if os.path.exists(agents_path):
                # Transparent migration (P7): import any legacy workspace agents
                # into the Runtime once, then leave the file in place (read-only
                # fallback). Do not overwrite.
                try:
                    from digital_state.runtime.store import RuntimeStore
                    from digital_state.runtime.stores import IdentityRecord
                    store = RuntimeStore()
                    if not store.exists():
                        store.provision()
                    import json as _json
                    with open(agents_path, "r", encoding="utf-8") as _f:
                        legacy = _json.load(_f)
                    for aid, ad in (legacy or {}).items():
                        if aid in (store.identity.all() or {}):
                            continue
                        try:
                            store.identity.upsert(
                                IdentityRecord(
                                    identity_id=aid,
                                    role=ad.get("role", "Unknown"),
                                    public_key=ad.get("public_key", {}),
                                )
                            )
                        except Exception:
                            pass
                except Exception:
                    pass

            # First-run Runtime + Governance bootstrap (P7 / ADR-011-01/011-02).
            # Hermes-independent; idempotent; never blocks on external runtimes.
            try:
                from digital_state.runtime.provision import bootstrap_runtime
                bootstrap_runtime()
            except Exception as be:
                print(json.dumps({
                    "status": "Warning",
                    "message": f"Workspace initialized; Runtime bootstrap skipped: {be}"
                }))
                return 0
                    
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

            # Hermes Integration — OPTIONAL mirror of Runtime profiles (ADR-011-05/011-07).
            # Hermes is never the source of truth. If absent, init still succeeds;
            # profiles are already materialized into the Runtime by bootstrap_runtime().
            try:
                if sys.platform == "win32":
                    local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
                    hermes_root = os.path.join(local_appdata if local_appdata else os.path.expanduser(r"~\\AppData\\Local"), "hermes")
                else:
                    hermes_root = os.path.expanduser("~/.hermes")

                # Enable plugin globally in hermes_root/config.yaml if Hermes present
                global_config_path = os.path.join(hermes_root, "config.yaml")
                if os.path.exists(global_config_path):
                    try:
                        import yaml
                        with open(global_config_path, "r", encoding="utf-8") as f:
                            cfg = yaml.safe_load(f) or {}
                        if "plugins" not in cfg or not isinstance(cfg["plugins"], dict):
                            cfg["plugins"] = {"enabled": []}
                        if "enabled" not in cfg["plugins"] or not isinstance(cfg["plugins"]["enabled"], list):
                            cfg["plugins"]["enabled"] = []
                        if "digital_state" not in cfg["plugins"]["enabled"]:
                            cfg["plugins"]["enabled"].append("digital_state")
                        with open(global_config_path, "w", encoding="utf-8") as f:
                            yaml.safe_dump(cfg, f, default_flow_style=False)
                    except Exception as e:
                        print(f"Warning: could not update global config.yaml: {e}", file=sys.stderr)

                # Find hermes executable (best-effort; absence is acceptable)
                import shutil
                import subprocess
                hermes_cmd = shutil.which("hermes")
                python_cmd = None
                if not hermes_cmd and os.path.isdir(hermes_root):
                    if sys.platform == "win32":
                        h_path = os.path.join(hermes_root, "hermes-agent", "venv", "Scripts", "hermes.exe")
                        p_path = os.path.join(hermes_root, "hermes-agent", "venv", "Scripts", "python.exe")
                    else:
                        h_path = os.path.join(hermes_root, "hermes-agent", "venv", "bin", "hermes")
                        p_path = os.path.join(hermes_root, "hermes-agent", "venv", "bin", "python")
                    if os.path.exists(h_path):
                        hermes_cmd = h_path
                    if os.path.exists(p_path):
                        python_cmd = p_path
                elif hermes_cmd:
                    cmd_dir = os.path.dirname(hermes_cmd)
                    p_path = os.path.join(cmd_dir, "python.exe" if sys.platform == "win32" else "python")
                    if os.path.exists(p_path):
                        python_cmd = p_path

                # Optional: install into Hermes venv if present
                if python_cmd:
                    try:
                        subprocess.run(
                            [python_cmd, "-m", "pip", "install", workspace_root],
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                        )
                    except Exception as e:
                        print(f"Warning: could not install digital_state in Hermes venv: {e}", file=sys.stderr)

                # Optional: mirror Runtime profiles into Hermes (source = Runtime templates)
                if hermes_cmd:
                    try:
                        from digital_state.core.assets.profile_templates import PROFILE_TEMPLATES
                    except Exception:
                        PROFILE_TEMPLATES = {}
                    profiles = {
                        "prime": "Digital State Prime Governance profile",
                        "builder": "Digital State Builder implementation profile",
                        "auditor": "Digital State Auditor verification profile",
                    }
                    for name, desc in profiles.items():
                        prof_dir = os.path.join(hermes_root, "profiles", name)
                        try:
                            if not os.path.exists(prof_dir):
                                subprocess.run([
                                    hermes_cmd, "profile", "create", name,
                                    "--no-alias", "--description", desc
                                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            if os.path.exists(prof_dir):
                                template = PROFILE_TEMPLATES.get(name, {})
                                soul_path = os.path.join(prof_dir, "SOUL.md")
                                if "SOUL.md" in template:
                                    with open(soul_path, "w", encoding="utf-8") as f:
                                        f.write(template["SOUL.md"])
                                prof_config_path = os.path.join(prof_dir, "config.yaml")
                                try:
                                    import yaml
                                    cfg = {}
                                    if os.path.exists(prof_config_path):
                                        with open(prof_config_path, "r", encoding="utf-8") as f:
                                            cfg = yaml.safe_load(f) or {}
                                    if "plugins" not in cfg or not isinstance(cfg["plugins"], dict):
                                        cfg["plugins"] = {"enabled": []}
                                    if "enabled" not in cfg["plugins"] or not isinstance(cfg["plugins"]["enabled"], list):
                                        cfg["plugins"]["enabled"] = []
                                    if "digital_state" not in cfg["plugins"]["enabled"]:
                                        cfg["plugins"]["enabled"].append("digital_state")
                                    with open(prof_config_path, "w", encoding="utf-8") as f:
                                        yaml.safe_dump(cfg, f, default_flow_style=False)
                                except Exception as e:
                                    print(f"Warning: could not update config.yaml for profile '{name}': {e}", file=sys.stderr)
                        except Exception as e:
                            print(f"Warning: could not mirror profile '{name}' to Hermes: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Hermes integration skipped (optional): {e}", file=sys.stderr)

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
            if args.key:
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

            if not python_cmd:
                print(json.dumps({"status": "Error", "message": "Hermes virtualenv python not found."}), file=sys.stderr)
                return 1

            try:
                subprocess.run(
                    [python_cmd, "-m", "pip", "install", "--upgrade", workspace_root],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(json.dumps({"status": "Success", "message": "Digital State package successfully upgraded inside Hermes virtualenv."}))
                return 0
            except Exception as e:
                print(json.dumps({"status": "Error", "message": f"Upgrade failed: {e}"}), file=sys.stderr)
                return 1

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

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main entrypoint for console scripts packaging."""
    sys.exit(run_cli(sys.argv[1:]))


if __name__ == "__main__":
    main()

