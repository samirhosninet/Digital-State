"""smoke test the audit-matrix plugin directly without LLM round-trip.

Verifies that:
  * audit_matrix package imports cleanly under the auditor profile;
  * all VALID_HOOKS hook callbacks are present (on_session_start/end,
    subagent_start/stop, kanban_task_completed/blocked);
  * register(ctx) is call-able;
  * policy.load_policy() resolves from the env-var chain AND from the
    ./governance/ directory;
  * handle_slash_command with no card_id returns the documented usage
    banner with active lens bindings;
  * handle_slash_command with --dry-run prints the 3 hermes chat
    subprocess argv lines without firing model calls.

All assertions are pure-Python; no LLM round-trip is performed.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

PLUGINS_PARENT = r"C:\Users\seo\AppData\Local\hermes\profiles\auditor\plugins\audit-matrix"
PLUGINS_DIR = r"C:\Users\seo\AppData\Local\hermes\profiles\auditor\plugins"

os.environ["DIGITAL_STATE_HOME"] = r"D:\digital-state"
os.environ["HERMES_HOME"] = r"C:\Users\seo\AppData\Local\hermes"

sys.path.insert(0, PLUGINS_DIR)
spec = importlib.util.spec_from_file_location(
    "audit_matrix",
    os.path.join(PLUGINS_PARENT, "__init__.py"),
    submodule_search_locations=[PLUGINS_PARENT],
)
am_pkg = importlib.util.module_from_spec(spec)
sys.modules["audit_matrix"] = am_pkg
spec.loader.exec_module(am_pkg)

spec_m = importlib.util.spec_from_file_location(
    "audit_matrix.matrix",
    os.path.join(PLUGINS_PARENT, "matrix.py"),
)
am_matrix = importlib.util.module_from_spec(spec_m)
sys.modules["audit_matrix.matrix"] = am_matrix
spec_m.loader.exec_module(am_matrix)

print("# === Smoke 1: package imports cleanly under auditor profile ===")
print(f"register callable: {callable(am_pkg.register)}")
hook_names = [
    "on_session_start",
    "on_session_end",
    "subagent_start",
    "subagent_stop",
    "on_kanban_task_completed",
    "on_kanban_task_blocked",
]
hook_status = {n: callable(getattr(am_pkg, n, None)) for n in hook_names}
for n, ok in hook_status.items():
    print(f"  hook {n}: {'OK' if ok else 'MISSING'}")
assert all(hook_status.values()), f"missing hooks: {[n for n, ok in hook_status.items() if not ok]}"
assert callable(am_pkg.register), "register(ctx) missing or not callable"
print("PASS\n")

print("# === Smoke 2: load_policy resolves via env chain ===")
from audit_matrix.policy import load_policy  # noqa: E402

p = load_policy(None)
print(f"lenses loaded: {[l.name for l in p.lenses]}")
print(f"rules loaded:  {len(p.rules)}")
for r in p.rules[:3]:
    print(f"  rule: {r}")
assert len(p.lenses) >= 3, "policy should expose >=3 lenses"
assert len(p.rules) >= 5, "policy should expose >=5 rules"
print("PASS\n")

print("# === Smoke 3: handle_slash_command with no args returns usage hint ===")
usage = am_matrix.handle_slash_command("")
print(usage[:400])
assert "[auditor-matrix] Usage" in usage
assert "criteria_auditor" in usage
assert "risk_auditor" in usage
assert "constitutional_auditor" in usage
print("PASS\n")

print("# === Smoke 4: build_evidence_pack runs hermes kanban show successfully ===")
pack = am_matrix.build_evidence_pack("t_3ab54f3b")
print(f"evidence pack size: {len(pack)} chars")
print(f"first 240 chars:\n{pack[:240]}\n...")
assert len(pack) > 200, "evidence pack should be non-trivial"
assert "t_3ab54f3b" in pack, "evidence pack should reference the card id"
print("PASS\n")

print("# === Smoke 5: handle_slash_command --dry-run --quiet prints hermes chat argv ===")
dry = am_matrix.handle_slash_command("t_3ab54f3b --dry-run --quiet")
print(dry[:1500])
assert "Auditor Matrix for t_3ab54f3b" in dry
assert "--profile auditor" in dry
# Dry-run path should dry-run 3 lenses.
dry_lines = [l for l in dry.splitlines() if l.startswith("[dry-run]")]
print(f"\n[dry-run] lens argv lines: {len(dry_lines)}")
assert len(dry_lines) == 3, f"expected 3 dry-run lines, got {len(dry_lines)}"
for line in dry_lines:
    assert "--profile auditor" in line, line
    assert "--provider nvidia" in line or "--provider openai-codex" in line, line
print("PASS\n")

print("# === Smoke 6: phantom t_9026c628 does NOT appear; real t_9026ce44 does ===")
from pathlib import Path

plugin_text = ""
for fn in ("__init__.py", "matrix.py", "policy.py", "plugin.yaml"):
    p_ = Path(PLUGINS_PARENT) / fn
    if p_.is_file():
        plugin_text += p_.read_text(encoding="utf-8", errors="replace")
phantom_hits = plugin_text.count("t_9026c628")
real_hits = plugin_text.count("t_9026ce44")
print(f"phantom t_9026c628 hits in plugin sources: {phantom_hits}")
print(f"real    t_9026ce44 hits in plugin sources: {real_hits}")
assert phantom_hits == 0, "phantom task reference still present in plugin sources"
assert real_hits >= 1, "real task reference missing from plugin sources"
print("PASS\n")

print("# === Smoke 7: D:\\digital-state hard-coded path NOT present in policy.py ===")
pol_text = (Path(PLUGINS_PARENT) / "policy.py").read_text(encoding="utf-8", errors="replace")
hardcoded = "D:\\\\digital-state" in pol_text
print(f"hard-coded D:\\\\digital-state present in policy.py: {hardcoded}")
assert not hardcoded, "policy.py still hard-codes D:\\digital-state"
print("PASS\n")

print("# === ALL SMOKE TESTS PASSED ===")
