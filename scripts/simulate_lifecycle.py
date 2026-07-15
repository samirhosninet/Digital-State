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
    # Initialize kernel (using the actual configuration)
    kernel = GovernanceKernel(root, run_bootstrap=False)
    feature_id = "feat-bootstrap"
    
    # Ensure default agents are registered
    if not kernel.registry.get_agent("prime-agent"):
        kernel.registry._ensure_default_agents()
    
    # 2. SPECIFICATION -> PLANNING
    spec_content = {"spec_file": "specs/001-spec.md", "requirements_count": 3}
    sig = get_sig(spec_content, "key-prime")
    kernel.submit_evidence(feature_id, "SPECIFICATION", spec_content, "prime-agent", sig)
    
    # 3. PLANNING -> TASKS
    plan_content = {"plan_file": "specs/001-plan.md", "technical_context_complete": True}
    sig = get_sig(plan_content, "key-builder")
    kernel.submit_evidence(feature_id, "PLANNING", plan_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "PLANNING", "auditor-agent")
    
    # 4. TASKS -> IMPLEMENTATION
    tasks_content = {"tasks_file": "specs/001-tasks.md", "tasks_count": 21, "requirements_count": 21}
    sig = get_sig(tasks_content, "key-builder")
    kernel.submit_evidence(feature_id, "TASKS", tasks_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "TASKS", "auditor-agent")
    
    # 5. IMPLEMENTATION -> VERIFICATION
    impl_content = {"tasks_file": "specs/001-tasks.md", "all_tasks_completed": True}
    sig = get_sig(impl_content, "key-builder")
    kernel.submit_evidence(feature_id, "IMPLEMENTATION", impl_content, "builder-agent", sig)
    kernel.approve_gate(feature_id, "IMPLEMENTATION", "auditor-agent")
    
    # 6. VERIFICATION -> COMPLETED
    ver_content = {"walkthrough_file": "walkthrough.md", "all_tests_passed": True}
    sig = get_sig(ver_content, "key-auditor")
    kernel.submit_evidence(feature_id, "VERIFICATION", ver_content, "auditor-agent", sig)
    kernel.approve_gate(feature_id, "VERIFICATION", "prime-agent")
    
    print(f"Feature state successfully transitioned: {kernel.get_feature_state(feature_id)}")

if __name__ == "__main__":
    main()
