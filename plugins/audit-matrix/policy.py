"""Policy loader for the auditor matrix.

The adjudication rules live in
``$DIGITAL_STATE_HOME/governance/audit-matrix-policy.yaml`` by default
(fallback chain: ``HERMES_DIGITAL_STATE_HOME`` → ``HERMES_HOME`` → cwd).
Operators may pass any YAML file via the ``--policy`` flag of the
slash command.

If no policy file is found, the matrix falls back to ``DEFAULT_RULES``,
which is intentionally hard-coded here so the plugin can never silently
choose a verdict against the operator's intent.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("audit_matrix.policy")


ALLOWED_VERDICTS = (
    "APPROVE",
    "APPROVE WITH WARNINGS",
    "REJECT",
    "ESCALATE",
)


@dataclass(frozen=True)
class LensBinding:
    """Per-run provider + model binding for one audit lens."""

    name: str
    provider: str
    model: str
    description: str = ""
    optional: bool = False


@dataclass
class Policy:
    """Parsed adjudication policy."""

    lenses: List[LensBinding] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)

    def lens(self, name: str) -> Optional[LensBinding]:
        for lx in self.lenses:
            if lx.name == name:
                return lx
        return None

    def required_lenses(self) -> List[LensBinding]:
        return [lx for lx in self.lenses if not lx.optional]

    def optional_lenses(self) -> List[LensBinding]:
        return [lx for lx in self.lenses if lx.optional]


DEFAULT_LENSES = [
    LensBinding(
        name="criteria_auditor",
        provider="nvidia",
        model="moonshotai/kimi-k2.6",
        description="Acceptance-criteria validation against the kanban card body.",
    ),
    LensBinding(
        name="risk_auditor",
        provider="nvidia",
        model="deepseek-ai/deepseek-v4-pro",
        description="Risk and security review using FMEA + threat prompts.",
    ),
    LensBinding(
        name="constitutional_auditor",
        provider="nvidia",
        model="z-ai/glm-5.1",
        description="Constitutional/Digital State governance compliance review.",
    ),
    LensBinding(
        name="reserve_auditor",
        provider="openai-codex",
        model="gpt-5.5",
        description="Optional tie-breaker / future-use auditor.",
        optional=True,
    ),
]


DEFAULT_RULES = [
    {"name": "any-ESCALATE", "when": {"any": "ESCALATE"}, "verdict": "ESCALATE"},
    {"name": "any-REJECT",   "when": {"any": "REJECT"},   "verdict": "REJECT"},
    {"name": "two-or-more-APPROVE-WITH-WARNINGS",
     "when": {"count": {"APPROVE WITH WARNINGS": 2}},
     "verdict": "APPROVE WITH WARNINGS"},
    {"name": "mixed-approve-and-warnings",
     "when": {"count": {"APPROVE": 1, "APPROVE WITH WARNINGS": 1}},
     "verdict": "APPROVE WITH WARNINGS"},
    {"name": "one-warning-rest-approve",
     "when": {"count": {"APPROVE WITH WARNINGS": 1, "APPROVE": "rest"}},
     "verdict": "APPROVE WITH WARNINGS"},
    {"name": "unanimous-approve",
     "when": {"all": "APPROVE"},
     "verdict": "APPROVE"},
    # Catch-all safety net: never return None.
    {"name": "fallback", "when": {}, "verdict": "APPROVE WITH WARNINGS"},
]


def default_policy() -> Policy:
    return Policy(lenses=list(DEFAULT_LENSES), rules=list(DEFAULT_RULES))


def _try_parse_yaml(text: str) -> Optional[Dict[str, Any]]:
    try:
        import yaml
    except Exception:
        logger.warning("audit-matrix: PyYAML not installed; using default policy")
        return None
    try:
        return yaml.safe_load(text) or {}
    except Exception as exc:
        logger.warning("audit-matrix: malformed policy YAML (%s); using defaults", exc)
        return None


def _coerce_lenses(raw: Any) -> List[LensBinding]:
    out = []
    for item in raw or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        out.append(
            LensBinding(
                name=name,
                provider=str(item.get("provider") or "").strip(),
                model=str(item.get("model") or "").strip(),
                description=str(item.get("description") or "").strip(),
                optional=bool(item.get("optional") or False),
            )
        )
    return out


def _policy_from_dict(parsed: Dict[str, Any]) -> Policy:
    lenses = _coerce_lenses(parsed.get("lenses"))
    rules = parsed.get("rules") or []
    if not lenses:
        lenses = list(DEFAULT_LENSES)
    if not isinstance(rules, list) or not rules:
        rules = list(DEFAULT_RULES)
    return Policy(lenses=lenses, rules=[r for r in rules if isinstance(r, dict)])


def load_policy(path: Optional[str]) -> Policy:
    """Load Policy from path. On failure, use defaults.

    Auto-discovery order (first hit wins):

      1. Operator-supplied ``--policy PATH`` (handled by the caller).
      2. ``$DIGITAL_STATE_HOME/governance/audit-matrix-policy.yaml``
      3. ``$HERMES_DIGITAL_STATE_HOME/governance/audit-matrix-policy.yaml``
      4. ``$HERMES_HOME/governance/audit-matrix-policy.yaml`` (the
         profile-scoped governance dir when running under a non-default
         Hermes profile).
      5. ``./governance/audit-matrix-policy.yaml`` (relative to cwd).
      6. Built-in ``DEFAULT_LENSES`` / ``DEFAULT_RULES`` fallback so the
         plugin never silently picks a verdict against the operator's
         intent.

    Hard-coded Windows paths such as ``D:\\digital-state`` have been
    intentionally removed; operators who keep their governance tree on
    a fixed drive should set ``DIGITAL_STATE_HOME`` (or override
    ``--policy``) rather than rely on a Windows-specific absolute path.
    """
    if path:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    parsed = _try_parse_yaml(f.read())
                if parsed:
                    return _policy_from_dict(parsed)
            except OSError as exc:
                logger.warning("audit-matrix: cannot read policy file %s (%s)", path, exc)
        else:
            logger.warning("audit-matrix: --policy %s not found; using defaults", path)

    # Return operator defaults if no policy file was found.
    candidates = []
    for env_var in (
        "DIGITAL_STATE_HOME",
        "HERMES_DIGITAL_STATE_HOME",
        "HERMES_HOME",
    ):
        env_p = os.environ.get(env_var)
        if env_p:
            candidates.append(os.path.join(env_p, "governance", "audit-matrix-policy.yaml"))
    candidates.append(os.path.join(os.getcwd(), "governance", "audit-matrix-policy.yaml"))
    # History note: prior revisions of this module hard-coded Windows-
    # style absolute install paths for the Digital State governance tree.
    # Those literals were removed in the 2026-06-23 portability fix
    # (task ``t_c6e0a8b8``) in favour of the env-var chain above plus
    # ``./governance/`` for cwd-relative resolution. Use ``DIGITAL_STATE_HOME``
    # or pass ``--policy PATH`` to point at a fixed location across machines.

    for cand in candidates:
        if cand and os.path.isfile(cand):
            try:
                with open(cand, "r", encoding="utf-8") as f:
                    parsed = _try_parse_yaml(f.read())
                if parsed:
                    logger.info("audit-matrix: loaded policy from %s", cand)
                    return _policy_from_dict(parsed)
            except OSError:
                continue

    return default_policy()
