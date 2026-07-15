"""
Trace script demonstrating the full Digital State hook interception path
inside a Hermes-compatible plugin context.

Produces two scenarios:
  A) Authorized tool call  -> pre_tool_call approves -> post_tool_call records
  B) Unauthorized tool call -> pre_tool_call blocks   -> tool never executes
"""
import os, json, logging, sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="%(levelname)s: %(message)s")

from digital_state.hermes.plugin import DigitalStatePlugin
from digital_state.core.engine import GovernanceKernel


class MockPluginContext:
    """Mirrors the surface Hermes exposes to plugins via ctx."""
    def __init__(self):
        self.workspace_root = os.getcwd()
        self.hooks = {}
        self.commands = {}
        self.skills = {}

    def register_hook(self, name, cb):
        self.hooks[name] = cb

    def register_command(self, name, cb):
        self.commands[name] = cb

    def register_skill(self, name, path):
        self.skills[name] = path


def main():
    # -- bootstrap ---------------------------------------------------
    print("=" * 70)
    print("DIGITAL STATE -- HOOK INTERCEPTION TRACE")
    print("=" * 70)

    ctx = MockPluginContext()
    plugin = DigitalStatePlugin(ctx)
    plugin.initialize()

    registered = sorted(ctx.hooks.keys())
    print(f"\nRegistered hooks: {registered}")

    kernel = GovernanceKernel(os.getcwd(), run_bootstrap=False)

    # -- Scenario A: AUTHORIZED tool call ----------------------------
    print("\n" + "-" * 70)
    print("SCENARIO A -- AUTHORIZED TOOL CALL")
    print("-" * 70)

    # Put feature in SPECIFICATION so Prime can write spec files
    kernel.lifecycle_engine.feature_states["feat-009"] = "SPECIFICATION"
    kernel.lifecycle_engine._save_state()

    session = {
        "feature_id": "feat-009",
        "agent_key": {"key_id": "key-prime", "role": "Prime",
                      "public_key": "key-prime"},
    }

    print("\n[A-1] on_session_start")
    r = ctx.hooks["on_session_start"](session)
    print(f"       returned: {r}")

    print("\n[A-2] pre_tool_call  tool='write_file'")
    r = ctx.hooks["pre_tool_call"](
        "write_file",
        {"path": "specs/003-hermes-runtime-integration/spec.md"},
        session,
    )
    print(f"       returned: {r}")

    print("\n[A-3] << tool executes >>")

    print("\n[A-4] post_tool_call  tool='write_file'")
    outcome = {"success": True, "written_bytes": 142}
    ctx.hooks["post_tool_call"]("write_file", outcome, session)
    print(f"       outcome submitted: {outcome}")

    print("\n[A-5] on_session_end")
    ctx.hooks["on_session_end"](session)
    print("       session closed")

    # -- Scenario B: UNAUTHORIZED tool call --------------------------
    print("\n" + "-" * 70)
    print("SCENARIO B -- UNAUTHORIZED TOOL CALL (FAIL-CLOSED)")
    print("-" * 70)

    # Feature is COMPLETED -- no writes should be allowed
    kernel.lifecycle_engine.feature_states["feat-009"] = "COMPLETED"
    kernel.lifecycle_engine._save_state()

    print("\n[B-1] on_session_start")
    r = ctx.hooks["on_session_start"](session)
    print(f"       returned: {r}")

    print("\n[B-2] pre_tool_call  tool='write_file'  (should BLOCK)")
    r = ctx.hooks["pre_tool_call"](
        "write_file",
        {"path": "src/main.py"},
        session,
    )
    print(f"       returned: {r}")

    print("\n[B-3] << tool NOT executed -- blocked by governance >>")

    print("\n[B-4] on_session_end")
    ctx.hooks["on_session_end"](session)
    print("       session closed")

    # -- Audit log tail ----------------------------------------------
    print("\n" + "-" * 70)
    print("AUDIT LOG -- LAST 3 ENTRIES")
    print("-" * 70)
    log_path = os.path.join(".specify", "memory", "audit_log.jsonl")
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[-3:]:
            print(line.strip())

    print("\n" + "=" * 70)
    print("TRACE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
