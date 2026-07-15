import os
import json
import hashlib
from digital_state.core.engine import GovernanceKernel

def get_sig(content, key):
    serialized = json.dumps(content, sort_keys=True)
    h = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"{key}-signed-{h}"

def main():
    root = "."
    kernel = GovernanceKernel(root, run_bootstrap=False)
    feature_id = "feat-003"
    
    # Ensure default agents are registered
    if not kernel.registry.get_agent("prime-agent"):
        kernel.registry._ensure_default_agents()
        
    # 1. SPECIFICATION -> PLANNING (Prime submits spec evidence)
    spec_content = {
        "spec_file": "specs/003-hermes-runtime-integration/spec.md",
        "requirements_count": 8
    }
    sig = get_sig(spec_content, "key-prime")
    kernel.submit_evidence(feature_id, "SPECIFICATION", spec_content, "prime-agent", sig)
    
    # 2. PLANNING -> TASKS (Builder submits plan, Auditor approves)
    plan_content = {
        "plan_file": "specs/003-hermes-runtime-integration/plan.md",
        "technical_context_complete": True
    }
    sig = get_sig(plan_content, "key-builder")
    kernel.submit_evidence(feature_id, "PLANNING", plan_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "PLANNING", "auditor-agent")
    
    # 3. TASKS -> IMPLEMENTATION (Builder submits tasks, Auditor approves)
    tasks_content = {
        "tasks_file": "specs/003-hermes-runtime-integration/tasks.md",
        "tasks_count": 12,
        "requirements_count": 8
    }
    sig = get_sig(tasks_content, "key-builder")
    kernel.submit_evidence(feature_id, "TASKS", tasks_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "TASKS", "auditor-agent")
    
    # 4. IMPLEMENTATION -> VERIFICATION (Builder submits implementation evidence, Auditor approves)
    impl_content = {
        "tasks_file": "specs/003-hermes-runtime-integration/tasks.md",
        "all_tasks_completed": True
    }
    sig = get_sig(impl_content, "key-builder")
    kernel.submit_evidence(feature_id, "IMPLEMENTATION", impl_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "IMPLEMENTATION", "auditor-agent")
    
    # 5. VERIFICATION -> COMPLETED (Auditor submits verification, Prime approves)
    ver_content = {
        "walkthrough_file": "specs/003-hermes-runtime-integration/walkthrough.md",
        "all_tests_passed": True
    }
    sig = get_sig(ver_content, "key-auditor")
    kernel.submit_evidence(feature_id, "VERIFICATION", ver_content, "auditor-agent", sig)
    kernel.approve_gate(feature_id, "VERIFICATION", "prime-agent")
    
    print(f"Feature '{feature_id}' state: {kernel.get_feature_state(feature_id)}")

if __name__ == "__main__":
    main()
