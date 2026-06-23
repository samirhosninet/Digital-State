"""matrix — core orchestrator for /auditor-matrix.

Three-lens design
-----------------
For each lens in the policy (criteria_auditor, risk_auditor,
constitutional_auditor) this module spawns a fresh ``hermes chat``
process with:

    --profile auditor      # activates the auditor SOUL.md
    -m MODEL               # per-run model override
    --provider PROVIDER    # per-run provider override
    -Q                     # quiet: capture only the final response
    -q "<lens prompt>"     # the one-shot prompt

The discriminator prompt instructs the lens to respond with exactly
one verdict line out of {APPROVE, APPROVE WITH WARNINGS, REJECT,
ESCALATE} followed by reasoning. We post-process stdout to that single
verdict token. This keeps one-shot determination deterministic.

Once all lenses have returned, ``adjudicate`` selects the verdict using
the policy rules. The final output is returned to the user via the
slash-command handler.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .policy import (
    ALLOWED_VERDICTS,
    Policy,
    LensBinding,
    default_policy,
    load_policy,
)

logger = logging.getLogger("audit_matrix.matrix")


# ---------------------------------------------------------------------------
# Data classes for the lens verdict stream.
# ---------------------------------------------------------------------------

@dataclass
class LensVerdict:
    lens: str
    provider: str
    model: str
    raw_text: str = ""
    verbatim: str = ""
    verdict: str = ""
    reasoning: str = ""
    elapsed_seconds: float = 0.0
    exit_code: int = -1
    error: str = ""


# ---------------------------------------------------------------------------
# Verdict extraction.
# ---------------------------------------------------------------------------

VERDICT_LINE_RE = re.compile(
    r"(?im)^\s*(?:verdict|final[_ ]verdict|matrix[_ ]verdict)\s*[:\-]\s*"
    r"(APPROVE(?:\s+WITH\s+WARNINGS)?|REJECT|ESCALATE)\s*$"
)
LEADING_VERDICT_RE = re.compile(
    r"(?i)\b(APPROVE(?:\s+WITH\s+WARNINGS)?|REJECT|ESCALATE)\b"
)


def extract_verdict(text: str) -> Tuple[str, str]:
    """Return (verdict_token, reasoning_text).

    Strategy:
      1. Look for an explicit ``Verdict: <X>`` style header line.
      2. Otherwise take the first allowed-token match anywhere.
    """
    if not text:
        return "", ""
    candidate = ""
    for m in VERDICT_LINE_RE.finditer(text):
        candidate = m.group(1).upper().strip()
        if candidate in ALLOWED_VERDICTS:
            break
    if not candidate:
        for m in LEADING_VERDICT_RE.finditer(text):
            t = m.group(1).upper().strip()
            if t in ALLOWED_VERDICTS:
                candidate = t
                break
    if not candidate or candidate not in ALLOWED_VERDICTS:
        return "", text.strip()
    # Reasoning: everything except the verdict line itself, trimmed.
    reasoning_lines = []
    for line in text.splitlines():
        if VERDICT_LINE_RE.match(line):
            continue
        reasoning_lines.append(line)
    reasoning = "\n".join(reasoning_lines).strip()
    return candidate, reasoning


# ---------------------------------------------------------------------------
# Adjudication.
# ---------------------------------------------------------------------------

def _verdict_counts(verdicts: List[str]) -> Dict[str, int]:
    out = {v: 0 for v in ALLOWED_VERDICTS}
    for v in verdicts:
        if v in out:
            out[v] += 1
    return out


def _total(verdicts: List[str]) -> int:
    return sum(1 for v in verdicts if v in ALLOWED_VERDICTS)


def _rule_matches(rule_when: Dict[str, Any], counts: Dict[str, int], total: int) -> bool:
    """Evaluate a single ``when`` clause match.

    Supported predicates:
      * ``{"any": "<verdict>"}`` -- any lens returned this verdict
      * ``{"all": "<verdict>"}``  -- every lens returned this verdict
      * ``{"count": {"<verdict>": N, ...}}``
            - N is an integer: at least that many lenses returned that verdict.
            - "rest": the remainder of the lenses returned a verdict from the
              sibling set; otherwise the rule fails.
    """
    if not rule_when:
        # Catch-all safety net always matches.
        return True
    if not isinstance(rule_when, dict) or len(rule_when) != 1:
        return False
    key, val = next(iter(rule_when.items()))
    key = str(key).lower()
    if key == "any":
        return counts.get(str(val).upper(), 0) > 0
    if key == "all":
        return counts.get(str(val).upper(), 0) == total and total > 0
    if key == "count":
        if not isinstance(val, dict):
            return False
        # Special "rest" predicate: every verdict not yet accounted for must
        # be among the sibling keys of the rule.
        sibling_verdicts = {k.upper() for k in val.keys()}
        consumed = 0
        for verdict_name, qty in val.items():
            verdict_name = str(verdict_name).upper()
            have = counts.get(verdict_name, 0)
            if str(qty).lower() == "rest":
                if have + consumed < total:
                    return False
                if have + consumed > total:
                    return False
                consumed += have
            else:
                try:
                    qn = int(qty)
                except Exception:
                    return False
                if have < qn:
                    return False
                consumed += have
        # Ensure no logic left over.
        missing = total - consumed
        if missing < 0:
            return False
        if missing > 0:
            # Sibling-compatible rest must come from sibling set.
            return False
        return True
    return False


def adjudicate(policy: Policy, lens_verdicts: List[LensVerdict]) -> Dict[str, Any]:
    """Apply policy rules to lens verdicts and return the matrix verdict record."""
    verdicts = [lv.verdict for lv in lens_verdicts if lv.verdict in ALLOWED_VERDICTS]
    counts = _verdict_counts(verdicts)
    total = _total(verdicts)
    chosen_rule = ""
    chosen_verdict = ""
    for rule in policy.rules:
        if _rule_matches(rule.get("when") or {}, counts, total):
            chosen_rule = str(rule.get("name") or "")
            chosen_verdict = str(rule.get("verdict") or "").upper()
            if chosen_verdict in ALLOWED_VERDICTS:
                break
    if not chosen_verdict or chosen_verdict not in ALLOWED_VERDICTS:
        # Last-resort safety net.
        chosen_rule = "fallback"
        chosen_verdict = "APPROVE WITH WARNINGS"

    return {
        "matrix_verdict": chosen_verdict,
        "rule_applied": chosen_rule,
        "counts": counts,
        "lenses_evaluated": len(lens_verdicts),
        "lenses_complete": sum(1 for v in verdicts if v),
        "per_lens": [
            {
                "lens": lv.lens,
                "provider": lv.provider,
                "model": lv.model,
                "verdict": lv.verdict,
                "elapsed_seconds": round(lv.elapsed_seconds, 2),
                "exit_code": lv.exit_code,
                "error": lv.error,
            }
            for lv in lens_verdicts
        ],
    }


# ---------------------------------------------------------------------------
# Lens prompt builder.
# ---------------------------------------------------------------------------

def build_lens_prompt(
    lens_name: str,
    lens_description: str,
    evidence_pack: str,
    policy_rules_text: str,
) -> str:
    """Compose the one-shot prompt sent to a lens.

    The lens is told its name, given the shared evidence pack, and
    instructed to end with a single-line ``Verdict: <X>`` formatted
    answer.
    """
    return (
        f"You are the {lens_name} of the Auditor Matrix for a Digital State kanban card.\n"
        f"Your lens focus: {lens_description}\n\n"
        "Apply Premortem Plus risk governance. Be concise but show reasoning.\n\n"
        "EVIDENCE PACK (shared across all lenses):\n"
        "-------------------------------------------\n"
        f"{evidence_pack}\n"
        "-------------------------------------------\n\n"
        "RULES TO FOLLOW (from governance/audit-matrix-policy.yaml):\n"
        "----------------------------------------------------------\n"
        f"{policy_rules_text}\n"
        "----------------------------------------------------------\n\n"
        "INSTRUCTIONS:\n"
        "1. Outcome text describing your evaluation.\n"
        "2. End with EXACTLY ONE line: ``Verdict: <X>`` where X is one of:\n"
        "   APPROVE | APPROVE WITH WARNINGS | REJECT | ESCALATE\n"
        "Do not output any other verdict tokens. Do not include any API keys or secrets.\n"
    )


def _policy_rules_text(policy: Policy) -> str:
    lines = []
    for rule in policy.rules:
        name = rule.get("name") or "(unnamed)"
        verdict = rule.get("verdict") or ""
        when = rule.get("when") or {}
        lines.append(f"- rule[{name}] when={json.dumps(when, sort_keys=True)} -> {verdict}")
    return "\n".join(lines)


def _policy_lenses_text(policy: Policy) -> str:
    lines = []
    for lx in policy.lenses:
        lines.append(f"- {lx.name}: provider={lx.provider} model={lx.model} optional={lx.optional}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Evidence pack construction (read-only).
# ---------------------------------------------------------------------------

def build_evidence_pack(card_id: str) -> str:
    """Run ``hermes kanban show <card_id>`` and capture stdout as the shared pack.

    Read-only: this only invokes the show command and formats output. It never
    mutates any state.
    """
    try:
        proc = subprocess.run(
            ["hermes", "kanban", "show", card_id],
            capture_output=True, text=True, check=False, timeout=60,
        )
    except FileNotFoundError:
        return f"[evidence_pack] FAIL: hermes CLI not on PATH for card {card_id}"

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    header = f"=== Evidence Pack for {card_id} ===\n"
    if proc.returncode != 0:
        header += f"[kanban show exit_code={proc.returncode}]\n"
    if stderr:
        header += f"[stderr]\n{stderr}\n"
    header += "[stdout]\n"
    return header + stdout


# ---------------------------------------------------------------------------
# Subprocess invocation (per-run model override).
# ---------------------------------------------------------------------------

def _resolve_hermes_executable() -> List[str]:
    """Return the argv prefix for spawning a hermes chat one-shot."""
    exe = shutil.which("hermes")
    if exe:
        return [exe]
    # Fall back to ``python -m hermes_cli`` so we don't hard-fail in
    # raw source-checkout environments that lack a console script.
    py = shutil.which("python") or shutil.which("python3")
    if py:
        return [py, "-m", "hermes_cli"]
    return ["hermes"]


def run_lens(lens: LensBinding, prompt: str, dry_run: bool, timeout: int = 600) -> LensVerdict:
    """Spawn a single auditor one-shot for ``lens`` with per-run overrides.

    The spawned process is a fresh ``hermes chat`` invocation. The
    --profile auditor flag activates the auditor SOUL.md; ``-m`` and
    ``--provider`` are passed arg-by-arg so no global config is
    mutated.
    """
    argv_prefix = _resolve_hermes_executable()
    # v0.17.0 hermes CLI: ``--profile`` is a TOP-LEVEL global flag that
    # must precede the subcommand, not a flag of ``chat``. The argv
    # below has been order-corrected so ``chat`` is parsed by the
    # auditor profile's CLI bootstrap (auditor SOUL.md + skills).
    argv = argv_prefix + [
        "--profile", "auditor",
        "chat",
        "-m", lens.model,
        "--provider", lens.provider,
        "--source", "plugin:audit-matrix",
        "-Q",  # quiet: emit only the final response + session info
        "-q", prompt,
    ]
    started = time.time()
    if dry_run:
        return LensVerdict(
            lens=lens.name, provider=lens.provider, model=lens.model,
            raw_text="[dry-run: command would be: " + " ".join(argv) + "]",
            verdict="", exit_code=0, error="dry-run",
        )
    try:
        proc = subprocess.run(
            argv, capture_output=True, text=True, check=False, timeout=timeout,
            env={**os.environ, "AUDIT_MATRIX_LENS": lens.name},
        )
    except subprocess.TimeoutExpired as exc:
        return LensVerdict(
            lens=lens.name, provider=lens.provider, model=lens.model,
            raw_text=str(exc.stdout or "") + " [TIMEOUT]",
            verdict="", exit_code=-1,
            error=f"timeout after {timeout}s",
            elapsed_seconds=time.time() - started,
        )
    except FileNotFoundError as exc:
        return LensVerdict(
            lens=lens.name, provider=lens.provider, model=lens.model,
            verdict="",
            exit_code=-1,
            error=f"hermes executable not found: {exc}",
            elapsed_seconds=time.time() - started,
        )
    out = (proc.stdout or "")
    err = (proc.stderr or "")
    combined = out + "\n" + err
    verdict, reasoning = extract_verdict(combined)
    return LensVerdict(
        lens=lens.name, provider=lens.provider, model=lens.model,
        raw_text=out.strip(),
        verbatim=combined.strip(),
        verdict=verdict,
        reasoning=reasoning,
        exit_code=proc.returncode,
        error="",
        elapsed_seconds=time.time() - started,
    )


# ---------------------------------------------------------------------------
# Slash command dispatcher (entry point wired in __init__.register).
# ---------------------------------------------------------------------------

def _parse_slash_args(args_text: str) -> Tuple[Optional[str], argparse.Namespace]:
    """Parse ``<card_id> [--policy PATH] [--lens NAME] [--reserve] [--quiet] [--dry-run]``.

    Returns ``(None, namespace)`` if no card id was supplied; the namespace
    will carry an empty ``card_id`` field.
    """
    parser = argparse.ArgumentParser(prog="auditor-matrix", add_help=False)
    parser.add_argument("card_id", nargs="?", default="")
    parser.add_argument("--policy", default=None)
    parser.add_argument("--lens", default=None,
                        help="Run only a single named lens (e.g. criteria_auditor).")
    parser.add_argument("--reserve", action="store_true",
                        help="Also run the optional reserve lens.")
    parser.add_argument("--quiet", action="store_true",
                        help="Hide per-lens raw output; print only the verdict.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the commands that would run, do nothing.")
    if not args_text or not args_text.strip():
        return None, parser.parse_args([])
    try:
        ns = parser.parse_args(args_text.split())
    except SystemExit:
        # argparse already printed help; return the empty-state namespace.
        return None, parser.parse_args([])
    return (ns.card_id or None), ns


def _summarize_lens(lv: LensVerdict, quiet: bool) -> str:
    if not quiet:
        body = (lv.reasoning or lv.raw_text or lv.error).strip()
        # Trim huge outputs to a manageable slice.
        if len(body) > 1200:
            body = body[:600] + "\n[... truncated ...]\n" + body[-600:]
    else:
        body = ""
    if body:
        return f"--- {lv.lens} ({lv.provider}/{lv.model}) -> {lv.verdict or 'NO_VERDICT'} ({lv.elapsed_seconds:.1f}s) ---\n{body}"
    return f"--- {lv.lens} ({lv.provider}/{lv.model}) -> {lv.verdict or 'NO_VERDICT'} ({lv.elapsed_seconds:.1f}s) ---"


def handle_slash_command(raw_args: str) -> str:
    """Entry point wired to the ``/auditor-matrix`` slash command."""
    card_id, opts = _parse_slash_args(raw_args or "")

    policy = load_policy(opts.policy)
    if not policy.lenses:
        return "[auditor-matrix] FAIL: no lenses resolved from policy."

    if not card_id:
        return (
            "[auditor-matrix] Usage: /auditor-matrix <card_id> "
            "[--policy PATH] [--lens NAME] [--reserve] [--quiet] [--dry-run]\n"
            "Active lens bindings:\n" + _policy_lenses_text(policy)
        )

    evidence_pack = build_evidence_pack(card_id)
    rules_text = _policy_rules_text(policy)

    selected: List[LensBinding] = []
    if opts.lens:
        only_one = policy.lens(opts.lens)
        if not only_one:
            return f"[auditor-matrix] FAIL: unknown lens '{opts.lens}'."
        selected = [only_one]
    else:
        selected = list(policy.required_lenses())
        if opts.reserve:
            selected.extend(policy.optional_lenses())

    summary = [f"# Auditor Matrix for {card_id}"]
    summary.append(
        f"Lenses: {', '.join(l.name for l in selected)}"
    )
    summary.append(f"Policy rules: {len(policy.rules)} loaded")

    if opts.dry_run:
        for lx in selected:
            argv = _resolve_hermes_executable() + [
                "--profile", "auditor",
                "chat",
                "-m", lx.model, "--provider", lx.provider,
                "-Q", "-q", "<lens prompt>",
            ]
            summary.append(f"[dry-run] would run: {' '.join(argv)}")
        return "\n".join(summary)

    lens_results: List[LensVerdict] = []
    for lx in selected:
        prompt = build_lens_prompt(
            lens_name=lx.name,
            lens_description=lx.description,
            evidence_pack=evidence_pack,
            policy_rules_text=rules_text,
        )
        lv = run_lens(lx, prompt, dry_run=False)
        lens_results.append(lv)
        summary.append(_summarize_lens(lv, opts.quiet))

    matrix = adjudicate(policy, lens_results)
    summary.append("")
    summary.append("## Matrix Verdict")
    summary.append(f"FINAL: {matrix['matrix_verdict']}    (rule: {matrix['rule_applied']})")
    summary.append(
        f"Counts: APPROVE={matrix['counts'].get('APPROVE', 0)}, "
        f"APPROVE WITH WARNINGS={matrix['counts'].get('APPROVE WITH WARNINGS', 0)}, "
        f"REJECT={matrix['counts'].get('REJECT', 0)}, "
        f"ESCALATE={matrix['counts'].get('ESCALATE', 0)}"
    )
    return "\n".join(summary)
