# Audit Matrix — multi-lens auditor orchestrator

A Hermes plugin that provides the `/auditor-matrix <card_id>` slash
command inside Prime / Hermes chat. Spawns three independent
auditor one-shots (criteria, risk, constitutional) each with a
**per-run** `--provider` and `-m` model override, then adjudicates
their individual verdicts into one of:

    APPROVE | APPROVE WITH WARNINGS | REJECT | ESCALATE

The plugin resides at `~/.hermes/plugins/audit-matrix/` and never
mutates any profile's `config.yaml` or `SOUL.md`.

---

## Install

The plugin is auto-discovered when it lives at:

    %LOCALAPPDATA%\hermes\plugins\audit-matrix\     (Windows)
    ~/.hermes/plugins/audit-matrix/                 (macOS/Linux)

…with a `plugin.yaml` and an `__init__.py`. Restart Hermes Desktop
or `hermes` so the plugin manager rescans, then run `/help` to see
the new `/auditor-matrix` command.

If you only need the CLI entry point, you do not need this plugin —
the matrix engine is importable directly from
`hermes chat --profile auditor -q "..."`:

```text
hermes --profile auditor -m moonshotai/kimi-k2.6 \
    --provider nvidia -Q \
    -q "Assess this card..."
```

---

## Usage

Within a Prime / Hermes chat session:

    /auditor-matrix <card_id>

Optional flags after the card id:

    --policy PATH       Path to a governance/audit-matrix-policy.yaml
                        (overrides auto-discovery).
    --lens NAME         Run only a single named lens.
    --reserve           Also run the optional reserve_auditor lens.
    --quiet             Hide per-lens raw output; print only the verdict.
    --dry-run           Print the commands that would run, do nothing.

Examples:

    /auditor-matrix t_9026ce44
    /auditor-matrix t_be52701b --quiet
    /auditor-matrix t_efcf78d7 --reserve --lens criteria_auditor

---

## How it works

1. The slash-command handler parses the args and resolves the policy
   from `$DIGITAL_STATE_HOME/governance/audit-matrix-policy.yaml`
   (with fallbacks through `$HERMES_DIGITAL_STATE_HOME`,
   `$HERMES_HOME`, and the current working directory's
   `governance/` dir — or `--policy PATH` for an explicit override).
2. It builds an "evidence pack" by running `hermes kanban show
   <card_id>` and captures the canonical card body, comments, and
   recent events.
3. For each (required, or `--reserve`-enabled) lens binding, it
   spawns one `hermes chat --profile auditor -m MODEL --provider
   PROVIDER -Q -q "<lens prompt>"` subprocess. The per-run argv
   overrides the model and provider **for that subprocess only** —
   no global config is mutated.
4. Each subprocess stdout is post-processed to extract the single
   verdict token (`APPROVE`, `APPROVE WITH WARNINGS`, `REJECT`, or
   `ESCALATE`) declared by the auditor agent.
5. The matrix applies the policy `rules` to the verdict set and
   returns the final matrix verdict.

---

## Files

    audit-matrix/
      plugin.yaml
      __init__.py
      matrix.py
      policy.py
      README.md

Policy file (Digital State governance) — discoverable at any of:

    $DIGITAL_STATE_HOME/governance/audit-matrix-policy.yaml   # set this env to override
    $HERMES_DIGITAL_STATE_HOME/governance/audit-matrix-policy.yaml
    $HERMES_HOME/governance/audit-matrix-policy.yaml
    ./governance/audit-matrix-policy.yaml                     # relative to cwd

Operators may keep a policy tree at any fixed absolute path; the
plugin honours the env-var override chain above AND a per-call
`--policy PATH` argument.

Sample per-operator tuning file (DO NOT commit your copy):

    <DIGITAL_STATE_HOME>/.digital-state.local.example.yaml
    <DIGITAL_STATE_HOME>/.digital-state.local.yaml   # gitignored

---

## Lens bindings (defaults)

| Lens                     | Provider       | Model                          |
|--------------------------|----------------|--------------------------------|
| criteria_auditor         | nvidia         | moonshotai/kimi-k2.6           |
| risk_auditor             | nvidia         | deepseek-ai/deepseek-v4-pro    |
| constitutional_auditor   | nvidia         | z-ai/glm-5.1                   |
| reserve_auditor (opt.)   | openai-codex   | gpt-5.5                        |

Edit the resolved policy file (or your own `--policy PATH` copy) to
override per run.

---

## Non-mutation contract

- No profile's `config.yaml` is modified.
- No profile's `SOUL.md` is modified.
- All provider/model overrides are passed **per subprocess** via
  `hermes chat -m MODEL --provider PROVIDER`. There is no
  `audit-matrix` entry in any profile config that changes the
  default.
- The plugin does **not** print API keys, session tokens, or any
  credentials. Provider auth is read from the existing host auth
  store.
- All Digital State governance file changes are limited to the
  policy file under whichever of the env-driven paths above
  resolves first; per-operator overrides live under
  `<DIGITAL_STATE_HOME>/.digital-state.local.yaml` (gitignored).
