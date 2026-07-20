"""Runtime Context Adapter (ADR-013 / Option E).

Decorates, resolves, and injects runtime governance context (feature_id, agent_key)
using a strict 3-tier resolution pipeline:
Tier 1: Explicit context parameters passed in hook context dictionary.
Tier 2: Process environment variables (DS_FEATURE_ID, DS_AGENT_KEY, HERMES_KANBAN_TASK, HERMES_PROFILE).
Tier 3: RuntimeStore identity authority and workspace state fallback queries.
"""

import json
import os
from typing import Any, Dict, Optional, Tuple


def resolve_governance_context(
    context: Any = None, workspace_root: Optional[str] = None
) -> Tuple[Optional[str], Any]:
    """Resolves (feature_id, agent_key) through a structured 3-tier lookup.

    Returns (None, None) if context cannot be authoritatively resolved through any tier.
    Attaches tenant_id to agent_key context metadata (defaulting to 'default_tenant').
    """
    feature_id: Optional[str] = None
    agent_key: Any = None
    tenant_id: Optional[str] = None

    # Tier 1: Explicit Context Dictionary
    if isinstance(context, dict):
        f_id = context.get("feature_id")
        a_key = context.get("agent_key")
        t_id = context.get("tenant_id")
        if f_id:
            feature_id = str(f_id)
        if a_key:
            agent_key = a_key
        if t_id:
            tenant_id = str(t_id)

    # Tier 2: Process Environment Variables
    if not feature_id:
        env_feature = os.environ.get("DS_FEATURE_ID") or os.environ.get("HERMES_KANBAN_TASK")
        if env_feature:
            feature_id = env_feature

    if not tenant_id:
        tenant_id = os.environ.get("DS_TENANT_ID") or "default_tenant"

    if not agent_key:
        env_key = os.environ.get("DS_AGENT_KEY")
        if env_key:
            if isinstance(env_key, dict):
                agent_key = env_key
            elif isinstance(env_key, str):
                try:
                    agent_key = json.loads(env_key)
                except Exception:
                    agent_key = env_key

    # Tier 3: RuntimeStore Authority & Workspace State Fallback
    ws_root = workspace_root or os.environ.get("HERMES_WORKSPACE") or os.getcwd()

    # Tier 3a: Feature ID from Workspace State
    if not feature_id:
        state_file = os.path.join(ws_root, ".specify", "state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                if isinstance(state_data, dict) and state_data:
                    feature_id = next(iter(state_data.keys()))
            except Exception:
                pass

    # Tier 3b: Agent Key from RuntimeStore Identity Authorities
    if not agent_key:
        profile_candidate = (
            os.environ.get("HERMES_PROFILE")
            or os.environ.get("DS_PROFILE")
            or "builder"
        ).strip().lower()

        try:
            from digital_state.runtime.store import RuntimeStore
            store = RuntimeStore(root=ws_root)
            if store.exists():

                identities = store.identity.all_for_tenant(tenant_id)
                matching_record = None
                for iid, record in identities.items():
                    if (
                        iid.lower() == profile_candidate
                        or record.role.lower() == profile_candidate
                    ):
                        matching_record = record
                        break
                if not matching_record and identities:
                    matching_record = next(iter(identities.values()))

                if matching_record and isinstance(matching_record.public_key, dict):
                    pub = matching_record.public_key
                    agent_key = {
                        "key_id": pub.get("key_id") or matching_record.identity_id,
                        "signature": pub.get("value") or pub.get("key_id") or "verified",
                        "role": matching_record.role,
                        "public_key": pub,
                        "tenant_id": matching_record.tenant_id,
                    }
        except Exception:
            pass

    # Verify signed session token if present
    session_token = None
    if isinstance(context, dict):
        session_token = context.get("session_token") or context.get("signed_token")
    if not session_token:
        session_token = os.environ.get("DS_SESSION_TOKEN")

    if session_token and isinstance(agent_key, dict):
        try:
            from digital_state.core.verifier import CryptoVerifier
            token_data = json.loads(session_token) if isinstance(session_token, str) else session_token
            payload = token_data.get("payload")
            sig = token_data.get("signature")
            if payload and sig:
                valid_token = CryptoVerifier.verify(agent_key, payload, sig)
                if not valid_token:
                    agent_key = None
        except Exception:
            agent_key = None

    if feature_id and agent_key:
        if isinstance(agent_key, dict) and "tenant_id" not in agent_key:
            agent_key["tenant_id"] = tenant_id or "default_tenant"
        return feature_id, agent_key

    return None, None
