import json
import os
from typing import Dict, Any, Optional, List

from digital_state.core.exceptions import RegistryError


class Agent:
    """Represents a registered Agent profile in the Digital State."""

    def __init__(
        self,
        agent_id: str,
        role: str,
        permissions: List[str],
        status: str = "Active",
        public_key: Any = "",
    ):
        self.agent_id = agent_id
        self.role = role
        self.permissions = permissions
        self.status = status
        self.public_key = public_key

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "permissions": self.permissions,
            "status": self.status,
            "public_key": self.public_key,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        return cls(
            agent_id=data["agent_id"],
            role=data["role"],
            permissions=data["permissions"],
            status=data.get("status", "Active"),
            public_key=data.get("public_key", ""),
        )


class AgentRegistry:
    """First-class Agent Registry managing profiles, statuses, and permissions."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.agents: Dict[str, Agent] = {}
        self._load_agents()

    def _load_agents(self) -> None:
        """Load registered agents from registry file."""
        if not os.path.exists(self.storage_path):
            self._ensure_default_agents()
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for agent_id, agent_data in data.items():
                    self.agents[agent_id] = Agent.from_dict(agent_data)
        except (json.JSONDecodeError, KeyError) as e:
            raise RegistryError(f"Failed to parse agent registry file: {e}") from e

    def _save_agents(self) -> None:
        """Persist agents to registry file."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()}
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _ensure_default_agents(self) -> None:
        """Initialize the baseline defaults for the Prime, Builder, and Auditor profiles."""
        self.register_agent(
            agent_id="prime-agent",
            role="Prime",
            permissions=["define_goals", "sign_off_spec", "approve_completed"],
            public_key="key-prime",
        )
        self.register_agent(
            agent_id="builder-agent",
            role="Builder",
            permissions=["submit_plan", "submit_evidence", "execute_tasks"],
            public_key="key-builder",
        )
        self.register_agent(
            agent_id="auditor-agent",
            role="Auditor",
            permissions=["approve_plan", "approve_tasks", "veto_gate", "verify_evidence"],
            public_key="key-auditor",
        )

    def register_agent(
        self, agent_id: str, role: str, permissions: List[str], public_key: Any = ""
    ) -> Agent:
        """Register a new agent in the registry."""
        if agent_id in self.agents:
            raise RegistryError(f"Agent with ID '{agent_id}' is already registered.")

        agent = Agent(agent_id=agent_id, role=role, permissions=permissions, public_key=public_key)
        self.agents[agent_id] = agent
        self._save_agents()
        return agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Retrieve an agent profile by identity."""
        return self.agents.get(agent_id)

    def update_agent_status(self, agent_id: str, status: str) -> None:
        """Update status of a registered agent profile (e.g. Active or Suspended)."""
        agent = self.get_agent(agent_id)
        if not agent:
            raise RegistryError(f"Agent with ID '{agent_id}' not found in registry.")

        agent.status = status
        self._save_agents()
