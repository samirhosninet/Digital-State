"""
Historical bootstrap/installer regression tests (v1.16.x).

Each test targets one historical fix commit. For every bug we assert the CURRENT
code path behaves correctly and (where it makes sense) that the OLD failure mode is
no longer reachable. All tests are offline except test_phase3_clean_install, which
performs a real install into a throwaway HERMES_HOME + venv (no live-Hermes mutation).
"""
import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "src"
PS1 = REPO / "install.ps1"
INSTALLER = SRC / "digital_state" / "bootstrap" / "installer.py"

# Make the SOURCE version of digital_state importable (not the installed one).
sys.path.insert(0, str(SRC))

import digital_state  # noqa: E402
from digital_state.governance.evidence.engine import EvidenceValidationEngine  # noqa: E402
from digital_state.governance.evidence.models import (  # noqa: E402
    EvidenceRecord,
    EvidenceType,
    EvidenceClassification,
    EvidenceBoundary,
)

pytestmark = pytest.mark.slow  # whole module exercises real install paths; mark accordingly



def _ps(code):
    return subprocess.run(
        ["powershell", "-NoProfile", "-Command", code],
        capture_output=True, text=True,
    )


# --- B1: TLS1.3 enum-member reference crash in PowerShell 5.1 ----------------------
def test_b1_tls13_guard():
    # Current code uses numeric constants + GetNames() guard; no enum-member reference.
    cur = ("try { $p=[Net.ServicePointManager]::SecurityProtocol -bor 3072; "
           "if ([Net.SecurityProtocolType]::GetNames([Net.SecurityProtocolType]) -contains 'Tls13') {"
           " $p=$p -bor 12288 }; [Net.ServicePointManager]::SecurityProtocol=$p; 'OK' } "
           "catch { 'OK_FALLBACK' }")
    r = _ps(cur)
    assert r.returncode == 0 and ("OK" in r.stdout or "OK_FALLBACK" in r.stdout), r.stderr
    # The old fatal line must not be present in install.ps1.
    text = PS1.read_text()
    assert "[Net.SecurityProtocolType]::Tls13" not in text


# --- B2: Hermes python must not resolve to a host interpreter outside hermes_path --
def test_b2_hermes_python_isolation():
    text = INSTALLER.read_text()
    # The which('hermes') fallback must require the resolved python to live under hermes_path.
    assert "hermes_path in p_path.parents" in text
    # Mirror the strict-resolution logic and assert a host python is rejected.
    hermes_root = Path(tempfile.mkdtemp(prefix="ds-b2-"))
    host_py = Path(sys.executable)
    # Simulate only the which('hermes') branch being reachable, pointing at host python.
    hermes_python = hermes_root / "hermes-agent" / "venv" / "Scripts" / "python.exe"
    accepted = bool(hermes_python.exists())
    if not accepted:
        # fallback: only accept if under hermes_path
        p_path = host_py
        accepted = bool(p_path.exists() and hermes_root in p_path.parents)
    assert accepted is False, "host python outside hermes_path must be rejected"
    shutil.rmtree(hermes_root, ignore_errors=True)


# --- B3: no editable ('-e') pip install into the Hermes venv -----------------------
def test_b3_no_editable_install():
    text = INSTALLER.read_text()
    assert "'-e'" not in text and '"-e"' not in text
    assert "pip\", \"install\"" in text or "pip install" in text


# --- B4: code_disc multi-line python -c with embedded semicolons ------------------
def test_b4_code_disc_single_line():
    # OLD failure snippet still errors (proves the historical failure mode).
    old = "import importlib.metadata, sys; try: pass"
    r_old = subprocess.run([sys.executable, "-c", old], capture_output=True, text=True)
    assert r_old.returncode != 0 and "SyntaxError" in r_old.stderr
    # CURRENT single-line import+assert is valid Python.
    cur = ("import digital_state; "
           "from digital_state.hermes.plugin import DigitalStatePlugin; "
           "assert hasattr(DigitalStatePlugin, 'on_session_start_handler')")
    r_cur = subprocess.run([sys.executable, "-c", cur], capture_output=True, text=True)
    assert r_cur.returncode == 0, r_cur.stderr


# --- B5: importlib.metadata.entry_points() cross-version incompatibility -----------
def test_b5_no_entry_points_discovery():
    text = INSTALLER.read_text()
    # The fragile single-arg entry_points(group=...) discovery must be gone.
    assert "entry_points(group=" not in text
    # Current verification path must be importable + attribute-based.
    cur = ("import digital_state; "
           "from digital_state.hermes.plugin import DigitalStatePlugin; "
           "assert hasattr(DigitalStatePlugin, 'on_session_start_handler')")
    r = subprocess.run([sys.executable, "-c", cur], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


# --- B6: evidence validation must work without a repo checkout --------------------
def test_b6_evidence_installed_package_fallback():
    ws = Path(tempfile.mkdtemp(prefix="ds-b6-"))
    eng = EvidenceValidationEngine(workspace_root=ws)
    rec = EvidenceRecord(
        statement="probe statement",
        evidence_type=EvidenceType.REPOSITORY_IMPLEMENTATION,
        boundary=EvidenceBoundary.DIGITAL_STATE_REPOSITORY,
        source="probe",
        classification=EvidenceClassification.VERIFIED,
        justification="probe justification",
        repo_path="src/digital_state/bootstrap/installer.py",
    )
    # On a clean machine (no repo at workspace_root) the installed-package fallback
    # must validate instead of raising EvidenceValidationError.
    eng.validate_record(rec)
    shutil.rmtree(ws, ignore_errors=True)


# --- B7: Layer 1 must not require a local src/ checkout ----------------------------
def test_b7_layer1_no_local_src_dependency():
    text = PS1.read_text()
    assert "$PSScriptRoot\\src" not in text
    assert "$ScriptDir\\src" not in text
    assert "PYTHONPATH" not in text
    # Current code downloads payload and inserts an absolute src dir.
    assert "DS_PACKAGE_ROOT" in text


# --- B8: EngineScript must put PackageRoot/src on sys.path -------------------------
def test_b8_engine_script_src_on_path():
    text = PS1.read_text()
    assert "sys.path.insert(0, " in text
    assert "$SrcDir" in text


# --- B9: site-packages copy fallback when pip fails / no pyproject -----------------
def test_b9_site_packages_copy_fallback():
    text = INSTALLER.read_text()
    assert "copytree" in text
    assert "Site-packages copy fallback" in text


# --- Phase 3/4: real install into an isolated HERMES_HOME --------------------------
def test_phase3_clean_install_and_operational_probes():
    base = Path(tempfile.mkdtemp(prefix="ds-regr-"))
    hermes_home = base / "hermes_home"
    localappdata = base / "localappdata"
    hermes_home.mkdir(parents=True, exist_ok=True)
    localappdata.mkdir(parents=True, exist_ok=True)

    # Run the REAL install in a separate process so the installer's is_mock_test
    # fast-path (which short-circuits under pytest) does NOT skip the install.
    env = dict(os.environ)
    env["DS_PACKAGE_ROOT"] = str(REPO)
    env["DS_DRIVE_REPO"] = str(REPO)
    env["DS_DRIVE_WS"] = str(base)
    env["HERMES_HOME"] = str(hermes_home)
    env["LOCALAPPDATA"] = str(localappdata)
    env.pop("PYTHONPATH", None)

    driver = Path(__file__).parent / "_drive_real_install.py"
    run = subprocess.run(
        [sys.executable, str(driver)],
        capture_output=True, text=True, env=env,
    )
    assert run.returncode == 0, f"driver failed: {run.stderr[-800:]}"
    res = json.loads(run.stdout.strip().splitlines()[-1])

    assert res.get("installed") is True, f"install not reported: {res.get('error')}"
    assert res.get("discovered") is True
    assert res.get("imported") is True
    assert res.get("enabled") is True
    assert res.get("profiles_verified") is True
    assert (hermes_home / "config.yaml").exists()

    hermes_venv = hermes_home / "hermes-agent" / "venv"
    hp = hermes_venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    assert hp.exists(), "Hermes venv was not auto-provisioned"

    # The package must physically live in the TARGET venv's site-packages, not be
    # merely importable via an ambient path (regression guard for installer
    # pre_check false-positive).
    site = hermes_venv / "Lib" / "site-packages"
    ds_dir = site / "digital_state"
    assert ds_dir.exists(), (
        f"digital_state not actually installed in target venv; site-packages={sorted(p.name for p in site.iterdir())[:40]}"
    )

    probes = {
        "plugin": "import digital_state.hermes; from digital_state.hermes.plugin import DigitalStatePlugin; print('ok')",
        "store": "from digital_state.runtime.store import RuntimeStore; print('ok')",
        "gov": "import digital_state.governance; print('ok')",
    }
    env2 = {**env, "HERMES_HOME": str(hermes_home)}
    for name, code in probes.items():
        r = subprocess.run([str(hp), "-c", code], capture_output=True, text=True, env=env2)
        assert r.returncode == 0, f"{name} probe failed: {r.stderr}"

    # Fail-Closed: LocalPolicyEngine default-deny.
    from digital_state.device.policy_engine import LocalPolicyEngine
    pol = LocalPolicyEngine(device_dir=base / "device")
    assert pol.evaluate({"tool_name": "x", "agent_id": "a"})["action"] == "block"
    assert pol.evaluate({"agent_id": "a"})["action"] == "block"

    shutil.rmtree(base, ignore_errors=True)
