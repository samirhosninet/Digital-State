1|# Validation Bug Log
2|
3|**Authority:** PRIME (Governance)
4|**Phase:** Product Validation → Independent User Validation (Technical Proxy)
5|**Date Opened:** 2026-07-17
6|**Date Remediated:** 2026-07-17
7|**Status:** ✅ ALL RESOLVED — Product Validation Remediation Event (bounded, authorized)
8|
9|---
10|
11|## Summary of Resolved Defects
12|
13|| ID | Title | Severity | Status | Fix Location |
14||----|-------|----------|--------|--------------|
15|| BUG-VAL-001 | Runtime-seeded agents have zero permissions (role-case mismatch) | CRITICAL | ✅ RESOLVED | `src/digital_state/core/registry.py` `_permissions_for_role` |
16|| BUG-VAL-002 | `register` rejects re-registration of seeded IDs (no `--force`) | MEDIUM | ✅ RESOLVED | `cli/cli.py` + `core/registry.py` `register_agent` |
17|| BUG-VAL-003 | Release wheel missing `digital_state/core/assets` (roles.json/trust_roots.json) | CRITICAL (release) | ✅ RESOLVED | `pyproject.toml` (removed duplicate `force-up` include) + regenerated wheel |
18|| BUG-VAL-004 | Wheel `entry_points.txt` missing `digital-state` launcher | CRITICAL (release) | ✅ RESOLVED | `pyproject.toml` `[project.scripts]` + regenerated wheel |
19|
20|**Root cause of BUG-VAL-003/004:** the published wheel (`dist/digital_state-0.1.0-*.whl`,
21|timestamped 2026-07-14 23:40) was built *before* the `digital_state/core/assets/` package
22|directory was finalized (2026-07-17 03:xx) and *before* the `digital-state` console-script
23|was added to `pyproject.toml` (2026-07-17 01:38). A fresh `pip install` of that wheel was
24|therefore non-functional (no roles/trust-root assets, only one launcher). The build pipeline
25|itself then failed to re-build because `tool.hatch.build.targets.wheel.force-include` declared
26|`src/digital_state/core/assets` a second time while `packages` already shipped it (asset dir
27|has an `__init__.py`), causing hatchling to abort with "A second file is being added to the
28|wheel archive at the same path". Removing the redundant `force-include` restores a clean,
29|reproducible build that packages the assets and both launchers.
30|
31|---
32|
33|## BUG-VAL-001: Runtime-seeded agents have zero permissions
34|
35|### Severity: CRITICAL — blocks onboarding at step 2 (first `approve`)
36|
37|### Symptom (unchanged from discovery)
38|After `digitalstate init`, a user registers agents and attempts `approve`; the `approve`
39|returns `Error: Agent 'u-auditor' is not authorized to execute transition for action
40|'approve_spec'.`
41|
42|### Root Cause (unchanged)
43|`src/digital_state/core/registry.py`, `get_agent()` resolves Runtime-provisioned identities
44|carrying a **capitalized** role (`"Auditor"`) and calls `_permissions_for_role(rec.role)`.
45|`roles.json` keys are **lowercase** (`"auditor"`), so the lookup missed and returned `[]`.
46|Net effect: every Runtime-provisioned identity resolved to permissions `[]`.
47|
48|### Fix Applied (verified)
49|`_permissions_for_role` now normalizes the lookup key:
50|```python
51|@staticmethod
52|def _permissions_for_role(role: str) -> List[str]:
53|    assets = os.path.join(os.path.dirname(__file__), "assets", "roles.json")
54|    try:
55|        with open(assets, "r", encoding="utf-8") as f:
56|            roles = json.load(f).get("roles", {})
57|        return roles.get(role.strip().lower(), {}).get("permissions", [])
58|    except (OSError, json.JSONDecodeError):
59|        return []
60|```
61|Capitalized, lowercase, and whitespace-padded roles all resolve correctly.
62|
63|### Verification Evidence
64|- Unit regression: `tests/unit/test_bug_val_regressions.py::test_bug_val_001_role_case_normalization`
65|  and `::test_bug_val_001_permissions_drives_policy` — PASS.
66|- End-to-end: `scripts/smoke_e2e.py` drives the full lifecycle
67|  SPECIFICATION → COMPLETED using Runtime-first identities (auditor approval, the original
68|  blocker) — **PASS**.
69|
70|---
71|
72|## BUG-VAL-002: `register` rejects re-registration with no `--force`
73|
73|### Severity: MEDIUM — onboarding friction
74|
75|### Symptom (unchanged)
76|`init` seeds `prime-agent`/`builder-agent`/`auditor-agent` (public-key only, no private key).
77|A user following the README who runs `register --id prime-agent ...` gets
78|`Error: Agent with ID 'prime-agent' is already registered.` — yet cannot sign as the seeded
79|identity (no private key). They are stuck.
80|
81|### Fix Applied (verified)
82|- Added `--force` flag to the `register` CLI subcommand.
82|- `AgentRegistry.register_agent(..., force=False)` now overwrites an existing identity when
82|  `force=True` instead of raising `RegistryError`.
82|- The CLI passes `args.force` through to `register_agent` and to the Runtime IdentityStore
82|  `upsert` (which is already overwrite-by-id).
82|
83|### Verification Evidence
84|- Unit regression: `tests/unit/test_bug_val_regressions.py::test_bug_val_002_force_overwrites_existing`
85|  — without `--force` raises; with `--force` overwrites the seeded ID with a new keypair — PASS.
86|- End-to-end: `scripts/smoke_e2e.py` registers each trust-root ID with `--force` (re-keying the
87|  seeded public-only identity with a real keypair), then completes the full lifecycle — **PASS**.
88|
89|---
90|
91|## BUG-VAL-003: Release wheel missing `digital_state/core/assets`
92|
93|### Severity: CRITICAL (release/packaging) — a fresh `pip install` was non-functional
94|
95|### Symptom
96|The published wheel (`dist/digital_state-0.1.0-*.whl`, 2026-07-14) contained **no**
97|`digital_state/core/assets/` package: no `roles.json`, no `trust_roots.json`. The
98|`AssetBundle`/roles resolution would therefore raise `FileNotFoundError` at runtime for any
99|fresh install. The wheel also failed to rebuild because of a duplicate-include conflict
100|(see Root Cause).
101|
102|### Root Cause
103|The wheel predated the `core/assets/` package (created 2026-07-17). The build config then
104|carried an erroneous `[tool.hatch.build.targets.wheel.force-include]` mapping
105|`"src/digital_state/core/assets" = "digital_state/core/assets"` even though `packages`
106|(`["src/digital_state", ...]`) already ships the asset directory (it has an `__init__.py`).
107|hatchling rejected the duplicate: *"A second file is being added to the wheel archive at the
108|same path: `digital_state/core/assets/__init__.py`."*
109|
110|### Fix Applied (verified)
111|Removed the redundant `force-include` block from `pyproject.toml`. The single `packages`
112|declaration now correctly ships `core/assets` (with `roles.json`, `trust_roots.json`,
113|`profile_templates.json`, and the `profiles/` templates). Regenerated the wheel + sdist from
114|current source.
115|
116|### Verification Evidence
117|- Regenerated `dist/digital_state-0.1.0-py3-none-any.whl` inspected:
118|  `core/assets` present = True; `roles.json` in wheel = True; `trust_roots.json` in wheel = True.
119|- sdist `dist/digital_state-0.1.0.tar.gz` includes `src/digital_state/core/assets/roles.json`
120|  and the new regression test.
121|
122|---
123|
124|## BUG-VAL-004: Wheel `entry_points.txt` missing `digital-state` launcher
125|
126|### Severity: CRITICAL (release/packaging) — second launcher absent from install
127|
128|### Symptom
129|The published wheel's `entry_points.txt` declared only `digitalstate`. A fresh install exposed
130|a single console script; the `digital-state` alias required by the acceptance criteria was
131|absent. This was again a staleness artifact: the `digital-state` console script was added to
132|`pyproject.toml` (2026-07-17 01:38), after the wheel was built (2026-07-14).
133|
134|### Fix Applied (verified)
135|`pyproject.toml` `[project.scripts]` already declares both launchers (no source change needed
136|there):
137|```python
138|digitalstate = "digital_state.cli.cli:main"
139|digital-state = "digital_state.cli.cli:main"
140|```
141|After removing the BUG-VAL-003 build conflict, the wheel regenerated cleanly and now embeds
142|**both** entry points.
143|
144|### Verification Evidence
145|- Regenerated wheel `entry_points.txt`:
146|  ```
147|  [console_scripts]
148|  digital-state = digital_state.cli.cli:main
149|  digitalstate = digital_state.cli.cli:main
150|  ```
151|- Clean install into a fresh venv produced **both** `digital-state.exe` and `digitalstate.exe`,
152|  and **both** execute `--help` and the full workflow correctly.
153|
154|---
155|
156|## Proxy Install Summary (original discovery — now RESOLVED)
157|
158|| Step | Result (pre-fix) | Result (post-fix) |
159||------|------------------|-------------------|
160|| `digitalstate init` (clean temp workspace) | ✅ PASS | ✅ PASS |
161|| `digitalstate register` (distinct id / `--force`) | ✅ (distinct) / ❌ (seeded id) | ✅ both |
162|| `digitalstate submit SPECIFICATION` (correct signature) | ✅ accepted | ✅ accepted |
163|| `digitalstate approve SPECIFICATION` (auditor) | ❌ BUG-VAL-001: permissions=[] | ✅ transitions to PLANNING |
164|| `digital-state doctor` | ✅ PASS | ✅ PASS |
165|| Full lifecycle to COMPLETED | ❌ blocked by BUG-VAL-001 | ✅ PASS (5 transitions) |
166|
167|**Conclusion:** All four validated defects are resolved and independently verified. Release
168|artifacts (wheel + sdist) were regenerated from current source and confirmed to package the
169|assets, both CLI launchers, and matching metadata. Regression suite (58 tests) passes.
170|
171|---
172|
173|## What the Proxy Install CANNOT Validate (unchanged)
174|- Real human comprehension ("what was unclear?")
175|- Willingness to pay
176|- Cross-platform install on macOS/Linux by a non-owner
177|- Time-to-complete by an unfamiliar user
178|- Missing documentation from a user's perspective
These remain REQUIRED and can only come from independent human users. The code/package
defects that blocked a technical proxy from completing the workflow are now closed.
