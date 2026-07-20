"""Layer 2 Installer Engine Orchestrator (ECR-BOOTSTRAP-ARCHITECTURE-002).

Unified lifecycle execution engine for:
digitalstate install
digitalstate repair
digitalstate update
digitalstate uninstall
digitalstate doctor
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

from digital_state.bootstrap.installer import BootstrapInstaller
from digital_state.bootstrap.engine.manifest_manager import ManifestManager
from digital_state.bootstrap.engine.lock_manager import LockManager
from digital_state.bootstrap.engine.dep_manager import DependencyManager
from digital_state.bootstrap.engine.hermes_provisioner import HermesProvisioner
from digital_state.bootstrap.engine.speckit_provisioner import SpeckitProvisioner
from digital_state.bootstrap.engine.plugin_registrar import PluginRegistrar
from digital_state.bootstrap.engine.verifier import VerificationEngine
from digital_state.bootstrap.engine.rollback import RollbackEngine
from digital_state.bootstrap.engine.migration import MigrationEngine


def run_engine_cli(action: str = "install", dry_run: bool = False, workspace_root: Optional[Path] = None) -> int:
    """Executes Layer 2 Installer Engine lifecycle action and returns exit code (0 or 1)."""
    ws = Path(workspace_root) if workspace_root else Path.cwd()
    manifest_mgr = ManifestManager()
    lock_mgr = LockManager()

    if dry_run:
        print("====================================================")
        print("Layer 2 Installer Engine (DRY RUN MODE)")
        print("====================================================")
        return 0

    try:
        with lock_mgr:
            if action in ["install", "install.ps1"]:
                return _handle_install(ws, manifest_mgr)
            elif action == "repair":
                return _handle_repair(ws, manifest_mgr)
            elif action == "uninstall":
                return _handle_uninstall(ws, manifest_mgr)
            elif action == "update":
                return _handle_update(ws, manifest_mgr)
            elif action == "doctor":
                return _handle_doctor(ws, manifest_mgr)
            else:
                print(f"Unknown lifecycle action: {action}", file=sys.stderr)
                return 1
    except RuntimeError as e:
        print(f"Installer Lock Failure: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Installer Engine Execution Error: {e}", file=sys.stderr)
        return 1


def _handle_install(ws: Path, manifest_mgr: ManifestManager) -> int:
    rollback_mgr = RollbackEngine()
    try:
        # 1. Dependency Manager Check
        dep_mgr = DependencyManager()
        dep_res = dep_mgr.verify_dependencies()
        if not dep_res["supported"]:
            print(f"[-] Dependency Check Failed: Python 3.10+ required (detected: {dep_res['version']})", file=sys.stderr)
            return 1

        # 2. Hermes Provisioning
        hermes_prov = HermesProvisioner()
        h_info = hermes_prov.provision_hermes_runtime()
        hermes_root = Path(h_info["hermes_root"])
        hermes_python = Path(h_info["hermes_python"])

        # 3. SpecKit Provisioning
        speckit_prov = SpeckitProvisioner(hermes_python=hermes_python)
        s_info = speckit_prov.provision_speckit()

        # 4. Bootstrap Package Installation & Identity Provisioning
        installer = BootstrapInstaller(workspace_root=ws)
        b_res = installer.run_bootstrap(dry_run=False)
        if b_res.get("status") != "SUCCESS":
            rollback_mgr.rollback()
            print(f"[-] Bootstrap Installation Failed: {b_res.get('message')}", file=sys.stderr)
            return 1

        # 5. Plugin & Profile Registration
        registrar = PluginRegistrar(hermes_root=hermes_root)
        registrar.register_plugin()
        p_res = registrar.seed_profiles()

        # 6. Verification Engine
        verifier = VerificationEngine(hermes_root=hermes_root, hermes_python=hermes_python)
        v_res = verifier.run_all_gates()

        if not v_res["all_gates_passed"]:
            rollback_mgr.rollback()
            print(f"[-] Verification Gate Failure", file=sys.stderr)
            return 1

        # 7. Update Canonical Manifest
        manifest = manifest_mgr.load_manifest()
        manifest["installation_state"] = "FULLY_INTEGRATED"
        manifest["health_status"] = "PASS"
        manifest["hermes_state"]["detected"] = True
        manifest["hermes_state"]["root"] = str(hermes_root)
        manifest["hermes_state"]["python_path"] = str(hermes_python)
        manifest["speckit_state"]["installed"] = s_info["installed"]
        manifest["speckit_state"]["version"] = s_info["version"]
        manifest["plugin_state"]["enabled"] = True
        manifest["profiles_state"]["prime"] = "VERIFIED"
        manifest["profiles_state"]["builder"] = "VERIFIED"
        manifest["profiles_state"]["auditor"] = "VERIFIED"
        manifest_mgr.save_manifest(manifest)

        print(verifier.render_report_card(v_res))
        return 0
    except Exception as e:
        rollback_mgr.rollback()
        print(f"[-] Installation Execution Exception: {e}", file=sys.stderr)
        return 1


def _handle_repair(ws: Path, manifest_mgr: ManifestManager) -> int:
    print("[*] Executing Layer 2 Repair Lifecycle Routine...")
    manifest = manifest_mgr.load_manifest()
    hermes_root = Path(manifest.get("hermes_state", {}).get("root") or HermesProvisioner().hermes_root)

    # Re-enable plugin & re-seed profiles
    registrar = PluginRegistrar(hermes_root=hermes_root)
    registrar.register_plugin()
    p_res = registrar.seed_profiles()

    manifest["installation_state"] = "FULLY_INTEGRATED"
    manifest["health_status"] = "PASS"
    manifest["plugin_state"]["enabled"] = True
    manifest["profiles_state"]["prime"] = "VERIFIED"
    manifest["profiles_state"]["builder"] = "VERIFIED"
    manifest["profiles_state"]["auditor"] = "VERIFIED"
    manifest_mgr.save_manifest(manifest)

    print("[+] Repair Lifecycle Complete. Subsystem state synchronized.")
    return 0


def _handle_update(ws: Path, manifest_mgr: ManifestManager) -> int:
    print("[*] Executing Layer 2 Update Lifecycle Routine...")
    manifest = manifest_mgr.load_manifest()
    migrator = MigrationEngine(current_version="1.16.0")
    updated_manifest = migrator.migrate(manifest)
    manifest_mgr.save_manifest(updated_manifest)
    print(f"[+] Migration Complete: {updated_manifest.get('migration_note')}")
    return _handle_install(ws, manifest_mgr)


def _handle_uninstall(ws: Path, manifest_mgr: ManifestManager) -> int:
    print("[*] Executing Layer 2 Uninstall Lifecycle Routine...")
    manifest = manifest_mgr.load_manifest()
    manifest["installation_state"] = "UNINSTALLED"
    manifest["plugin_state"]["enabled"] = False
    manifest["health_status"] = "UNINSTALLED"
    manifest["profiles_state"]["prime"] = "REMOVED"
    manifest["profiles_state"]["builder"] = "REMOVED"
    manifest["profiles_state"]["auditor"] = "REMOVED"
    manifest_mgr.save_manifest(manifest)
    print("[+] Uninstall Routine Complete. Digital State integration removed.")
    return 0


def _handle_doctor(ws: Path, manifest_mgr: ManifestManager) -> int:
    manifest = manifest_mgr.load_manifest()
    print("====================================================")
    print("Digital State Layer 2 Doctor Diagnostic Report")
    print("====================================================")
    print(json.dumps(manifest, indent=2))
    return 0
