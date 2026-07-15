"""Runtime verification of the Digital State Hermes plugin hook contract (Spec 005).

Audits whether each plugin hook returns the structured Hermes block payload
(dict with an 'action'/'decision' key) rather than a bare boolean, which the
legacy implementation used and which a real Hermes runtime will not parse as a
veto. Exits non-zero if any blocking path returns a non-dict value.
"""
import datetime
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from digital_state.hermes.plugin import DigitalStatePlugin  # noqa: E402


class MockHermesContext:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.skills = {}
        self.hooks = {}
        self.commands = {}

    def register_skill(self, name, path):
        self.skills[name] = path

    def register_hook(self, name, callback):
        self.hooks[name] = callback

    def register_command(self, name, callback):
        self.commands[name] = callback


# A dict is a valid Hermes block payload iff it carries a veto/block signal.
def is_block_dict(value):
    if not isinstance(value, dict):
        return False
    action = value.get("action") or value.get("decision")
    return action in ("block", "deny", "reject")


results = []
failures = []


def check(name, value, expect_block):
    ok = is_block_dict(value) if expect_block else True
    shape = f"{type(value).__name__}"
    # Preserve the real value for JSON (None stays None, not the string "None").
    detail = value if isinstance(value, (dict, type(None))) else str(value)
    ok = is_block_dict(value) if expect_block else True
    results.append({"check": name, "type": shape, "value": detail, "ok": ok})
    if not ok:
        failures.append(f"{name}: expected block-dict, got {shape} -> {detail!r}")


def main():
    tmp = tempfile.mkdtemp(prefix="ds_hook_verify_")
    # Provision a minimal .specify workspace so the SDK does not blow up.
    spec_dir = os.path.join(tmp, ".specify")
    os.makedirs(os.path.join(spec_dir, "memory"), exist_ok=True)
    with open(os.path.join(spec_dir, "agents.json"), "w") as f:
        json.dump({}, f)
    with open(os.path.join(spec_dir, "state.json"), "w") as f:
        json.dump({}, f)
    with open(os.path.join(spec_dir, "memory", "audit_log.jsonl"), "w") as f:
        pass

    ctx = MockHermesContext(workspace_root=tmp)
    plugin = DigitalStatePlugin(ctx)
    assert plugin.initialize() is True, "plugin failed to initialize"

    deny_ctx = {}  # missing agent_key / feature_id -> fail-safe deny

    # pre_tool_call is the critical enforcement hook per Spec 005.
    check("pre_tool_call: missing context -> block dict",
          plugin.pre_tool_call_handler("run_command", {}, deny_ctx), expect_block=True)
    check("pre_tool_call: missing agent_key -> block dict",
          plugin.pre_tool_call_handler("run_command", {}, {"feature_id": "FEAT-1"}), expect_block=True)
    check("pre_tool_call: missing feature_id -> block dict",
          plugin.pre_tool_call_handler("run_command", {}, {"agent_key": "k"}), expect_block=True)

    # on_session_start must return a bool (status gate), but NOT a silent pass on missing ID.
    r = plugin.on_session_start_handler({})
    results.append({"check": "on_session_start: missing feature_id -> False",
                    "type": type(r).__name__, "value": r, "ok": (r is False)})
    if r is not False:
        failures.append(f"on_session_start returned {r!r} instead of False")

    # pre_llm_call contributes context; on missing feature_id it returns None (allowed).
    check("pre_llm_call: missing feature_id -> None (non-blocking)",
          plugin.pre_llm_call_handler("prompt", {}), expect_block=False)
    results[-1]["ok"] = results[-1]["value"] is None
    if results[-1]["value"] is not None:
        failures.append(f"pre_llm_call returned {results[-1]['value']!r}")

    report = {
        "spec": "005-hermes-hard-enforcement",
        "evaluated_on": datetime.datetime.now().isoformat(timespec="seconds"),
        "commit_baseline": "working-tree (uncommitted)",
        "checks": results,
        "outcome": "HOOK_ENFORCEMENT_VERIFIED" if not failures else "HOOK_ENFORCEMENT_NOT_VERIFIED",
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
