---
source_url: https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
title: Skills System | Hermes Agent
archived_at: 2026-05-13T02:40:25Z
---

Skills are on-demand knowledge documents the agent can load when needed. They follow a **progressive disclosure** pattern to minimize token usage and are compatible with the [agentskills.io](https://agentskills.io/specification) open standard.

All skills live in **`~/.hermes/skills/`** — the primary directory and source of truth. On fresh install, bundled skills are copied from the repo. Hub-installed and agent-created skills also go here. The agent can modify or delete any skill.

You can also point Hermes at **external skill directories** — additional folders scanned alongside the local one. See [External Skill Directories](index.md#external-skill-directories) below.

See also:

- [Bundled Skills Catalog](../../../reference/skills-catalog/index.md)
- [Official Optional Skills Catalog](../../../reference/optional-skills-catalog/index.md)

## Using Skills[​](index.md#using-skills "Direct link to Using Skills")

Every installed skill is automatically available as a slash command:

```
# In the CLI or any messaging platform:  
/gif-search funny cats  
/axolotl help me fine-tune Llama 3 on my dataset  
/github-pr-workflow create a PR for the auth refactor  
/plan design a rollout for migrating our auth provider  
  
# Just the skill name loads it and lets the agent ask what you need:  
/excalidraw
```

The bundled `plan` skill is a good example. Running `/plan [request]` loads the skill's instructions, telling Hermes to inspect context if needed, write a markdown implementation plan instead of executing the task, and save the result under `.hermes/plans/` relative to the active workspace/backend working directory.

You can also interact with skills through natural conversation:

```
hermes chat --toolsets skills -q "What skills do you have?"  
hermes chat --toolsets skills -q "Show me the axolotl skill"
```

## Progressive Disclosure[​](index.md#progressive-disclosure "Direct link to Progressive Disclosure")

Skills use a token-efficient loading pattern:

```
Level 0: skills_list()           → [{name, description, category}, ...]   (~3k tokens)  
Level 1: skill_view(name)        → Full content + metadata       (varies)  
Level 2: skill_view(name, path)  → Specific reference file       (varies)
```

The agent only loads the full skill content when it actually needs it.

## SKILL.md Format[​](index.md#skillmd-format "Direct link to SKILL.md Format")

```
---  
name: my-skill  
description: Brief description of what this skill does  
version: 1.0.0  
platforms: [macos, linux]     # Optional — restrict to specific OS platforms  
metadata:  
  hermes:  
    tags: [python, automation]  
    category: devops  
    fallback_for_toolsets: [web]    # Optional — conditional activation (see below)  
    requires_toolsets: [terminal]   # Optional — conditional activation (see below)  
    config:                          # Optional — config.yaml settings  
      - key: my.setting  
        description: "What this controls"  
        default: "value"  
        prompt: "Prompt for setup"  
---  
  
# Skill Title  
  
## When to Use  
Trigger conditions for this skill.  
  
## Procedure  
1. Step one  
2. Step two  
  
## Pitfalls  
- Known failure modes and fixes  
  
## Verification  
How to confirm it worked.
```

### Platform-Specific Skills[​](index.md#platform-specific-skills "Direct link to Platform-Specific Skills")

Skills can restrict themselves to specific operating systems using the `platforms` field:

| Value | Matches |
| --- | --- |
| `macos` | macOS (Darwin) |
| `linux` | Linux |
| `windows` | Windows |

```
platforms: [macos]            # macOS only (e.g., iMessage, Apple Reminders, FindMy)  
platforms: [macos, linux]     # macOS and Linux
```

When set, the skill is automatically hidden from the system prompt, `skills_list()`, and slash commands on incompatible platforms. If omitted, the skill loads on all platforms.

### Conditional Activation (Fallback Skills)[​](index.md#conditional-activation-fallback-skills "Direct link to Conditional Activation (Fallback Skills)")

Skills can automatically show or hide themselves based on which tools are available in the current session. This is most useful for **fallback skills** — free or local alternatives that should only appear when a premium tool is unavailable.

```
metadata:  
  hermes:  
    fallback_for_toolsets: [web]      # Show ONLY when these toolsets are unavailable  
    requires_toolsets: [terminal]     # Show ONLY when these toolsets are available  
    fallback_for_tools: [web_search]  # Show ONLY when these specific tools are unavailable  
    requires_tools: [terminal]        # Show ONLY when these specific tools are available
```

| Field | Behavior |
| --- | --- |
| `fallback_for_toolsets` | Skill is **hidden** when the listed toolsets are available. Shown when they're missing. |
| `fallback_for_tools` | Same, but checks individual tools instead of toolsets. |
| `requires_toolsets` | Skill is **hidden** when the listed toolsets are unavailable. Shown when they're present. |
| `requires_tools` | Same, but checks individual tools. |

**Example:** The built-in `duckduckgo-search` skill uses `fallback_for_toolsets: [web]`. When you have `FIRECRAWL_API_KEY` set, the web toolset is available and the agent uses `web_search` — the DuckDuckGo skill stays hidden. If the API key is missing, the web toolset is unavailable and the DuckDuckGo skill automatically appears as a fallback.

Skills without any conditional fields behave exactly as before — they're always shown.

## Secure Setup on Load[​](index.md#secure-setup-on-load "Direct link to Secure Setup on Load")

Skills can declare required environment variables without disappearing from discovery:

```
required_environment_variables:  
  - name: TENOR_API_KEY  
    prompt: Tenor API key  
    help: Get a key from https://developers.google.com/tenor  
    required_for: full functionality
```

When a missing value is encountered, Hermes asks for it securely only when the skill is actually loaded in the local CLI. You can skip setup and keep using the skill. Messaging surfaces never ask for secrets in chat — they tell you to use `hermes setup` or `~/.hermes/.env` locally instead.

Once set, declared env vars are **automatically passed through** to `execute_code` and `terminal` sandboxes — the skill's scripts can use `$TENOR_API_KEY` directly. For non-skill env vars, use the `terminal.env_passthrough` config option. See [Environment Variable Passthrough](../../security/index.md#environment-variable-passthrough) for details.

### Skill Config Settings[​](index.md#skill-config-settings "Direct link to Skill Config Settings")

Skills can also declare non-secret config settings (paths, preferences) stored in `config.yaml`:

```
metadata:  
  hermes:  
    config:  
      - key: myplugin.path  
        description: Path to the plugin data directory  
        default: "~/myplugin-data"  
        prompt: Plugin data directory path
```

Settings are stored under `skills.config` in your config.yaml. `hermes config migrate` prompts for unconfigured settings, and `hermes config show` displays them. When a skill loads, its resolved config values are injected into the context so the agent knows the configured values automatically.

See [Skill Settings](../../configuration/index.md#skill-settings) and [Creating Skills — Config Settings](../../../developer-guide/creating-skills/index.md#config-settings-configyaml) for details.

## Skill Directory Structure[​](index.md#skill-directory-structure "Direct link to Skill Directory Structure")

```
~/.hermes/skills/                  # Single source of truth  
├── mlops/                         # Category directory  
│   ├── axolotl/  
│   │   ├── SKILL.md               # Main instructions (required)  
│   │   ├── references/            # Additional docs  
│   │   ├── templates/             # Output formats  
│   │   ├── scripts/               # Helper scripts callable from the skill  
│   │   └── assets/                # Supplementary files  
│   └── vllm/  
│       └── SKILL.md  
├── devops/  
│   └── deploy-k8s/                # Agent-created skill  
│       ├── SKILL.md  
│       └── references/  
├── .hub/                          # Skills Hub state  
│   ├── lock.json  
│   ├── quarantine/  
│   └── audit.log  
└── .bundled_manifest              # Tracks seeded bundled skills
```

## External Skill Directories[​](index.md#external-skill-directories "Direct link to External Skill Directories")

If you maintain skills outside of Hermes — for example, a shared `~/.agents/skills/` directory used by multiple AI tools — you can tell Hermes to scan those directories too.

Add `external_dirs` under the `skills` section in `~/.hermes/config.yaml`:

```
skills:  
  external_dirs:  
    - ~/.agents/skills  
    - /home/shared/team-skills  
    - ${SKILLS_REPO}/skills
```

Paths support `~` expansion and `${VAR}` environment variable substitution.

### How it works[​](index.md#how-it-works "Direct link to How it works")

- **Read-only**: External dirs are only scanned for skill discovery. When the agent creates or edits a skill, it always writes to `~/.hermes/skills/`.
- **Local precedence**: If the same skill name exists in both the local dir and an external dir, the local version wins.
- **Full integration**: External skills appear in the system prompt index, `skills_list`, `skill_view`, and as `/skill-name` slash commands — no different from local skills.
- **Non-existent paths are silently skipped**: If a configured directory doesn't exist, Hermes ignores it without errors. Useful for optional shared directories that may not be present on every machine.

### Example[​](index.md#example "Direct link to Example")

```
~/.hermes/skills/               # Local (primary, read-write)  
├── devops/deploy-k8s/  
│   └── SKILL.md  
└── mlops/axolotl/  
    └── SKILL.md  
  
~/.agents/skills/               # External (read-only, shared)  
├── my-custom-workflow/  
│   └── SKILL.md  
└── team-conventions/  
    └── SKILL.md
```

All four skills appear in your skill index. If you create a new skill called `my-custom-workflow` locally, it shadows the external version.

## Agent-Managed Skills (skill\_manage tool)[​](index.md#agent-managed-skills-skill_manage-tool "Direct link to Agent-Managed Skills (skill_manage tool)")

The agent can create, update, and delete its own skills via the `skill_manage` tool. This is the agent's **procedural memory** — when it figures out a non-trivial workflow, it saves the approach as a skill for future reuse.

### When the Agent Creates Skills[​](index.md#when-the-agent-creates-skills "Direct link to When the Agent Creates Skills")

- After completing a complex task (5+ tool calls) successfully
- When it hit errors or dead ends and found the working path
- When the user corrected its approach
- When it discovered a non-trivial workflow

### Actions[​](index.md#actions "Direct link to Actions")

| Action | Use for | Key params |
| --- | --- | --- |
| `create` | New skill from scratch | `name`, `content` (full SKILL.md), optional `category` |
| `patch` | Targeted fixes (preferred) | `name`, `old_string`, `new_string` |
| `edit` | Major structural rewrites | `name`, `content` (full SKILL.md replacement) |
| `delete` | Remove a skill entirely | `name` |
| `write_file` | Add/update supporting files | `name`, `file_path`, `file_content` |
| `remove_file` | Remove a supporting file | `name`, `file_path` |

tip

The `patch` action is preferred for updates — it's more token-efficient than `edit` because only the changed text appears in the tool call.

## Skills Hub[​](index.md#skills-hub "Direct link to Skills Hub")

Browse, search, install, and manage skills from online registries, `skills.sh`, direct well-known skill endpoints, and official optional skills.

### Common commands[​](index.md#common-commands "Direct link to Common commands")

```
hermes skills browse                              # Browse all hub skills (official first)  
hermes skills browse --source official            # Browse only official optional skills  
hermes skills search kubernetes                   # Search all sources  
hermes skills search react --source skills-sh     # Search the skills.sh directory  
hermes skills search https://mintlify.com/docs --source well-known  
hermes skills inspect openai/skills/k8s           # Preview before installing  
hermes skills install openai/skills/k8s           # Install with security scan  
hermes skills install official/security/1password  
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force  
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify  
hermes skills install https://sharethis.chat/SKILL.md              # Direct URL (single-file SKILL.md)  
hermes skills install https://example.com/SKILL.md --name my-skill # Override name when frontmatter has none  
hermes skills list --source hub                   # List hub-installed skills  
hermes skills check                               # Check installed hub skills for upstream updates  
hermes skills update                              # Reinstall hub skills with upstream changes when needed  
hermes skills audit                               # Re-scan all hub skills for security  
hermes skills uninstall k8s                       # Remove a hub skill  
hermes skills reset google-workspace              # Un-stick a bundled skill from "user-modified" (see below)  
hermes skills reset google-workspace --restore    # Also restore the bundled version, deleting your local edits  
hermes skills publish skills/my-skill --to github --repo owner/repo  
hermes skills snapshot export setup.json          # Export skill config  
hermes skills tap add myorg/skills-repo           # Add a custom GitHub source
```

### Supported hub sources[​](index.md#supported-hub-sources "Direct link to Supported hub sources")

| Source | Example | Notes |
| --- | --- | --- |
| `official` | `official/security/1password` | Optional skills shipped with Hermes. |
| `skills-sh` | `skills-sh/vercel-labs/agent-skills/vercel-react-best-practices` | Searchable via `hermes skills search <query> --source skills-sh`. Hermes resolves alias-style skills when the skills.sh slug differs from the repo folder. |
| `well-known` | `well-known:https://mintlify.com/docs/.well-known/skills/mintlify` | Skills served directly from `/.well-known/skills/index.json` on a website. Search using the site or docs URL. |
| `url` | `https://sharethis.chat/SKILL.md` | Direct HTTP(S) URL to a single-file `SKILL.md`. Name resolution: frontmatter → URL slug → interactive prompt → `--name` flag. |
| `github` | `openai/skills/k8s` | Direct GitHub repo/path installs and custom taps. |
| `clawhub`, `lobehub`, `claude-marketplace` | Source-specific identifiers | Community or marketplace integrations. |

### Integrated hubs and registries[​](index.md#integrated-hubs-and-registries "Direct link to Integrated hubs and registries")

Hermes currently integrates with these skills ecosystems and discovery sources:

#### 1. Official optional skills (`official`)[​](index.md#1-official-optional-skills-official "Direct link to 1-official-optional-skills-official")

These are maintained in the Hermes repository itself and install with builtin trust.

- Catalog: [Official Optional Skills Catalog](../../../reference/optional-skills-catalog/index.md)
- Source in repo: `optional-skills/`
- Example:

```
hermes skills browse --source official  
hermes skills install official/security/1password
```

#### 2. skills.sh (`skills-sh`)[​](index.md#2-skillssh-skills-sh "Direct link to 2-skillssh-skills-sh")

This is Vercel's public skills directory. Hermes can search it directly, inspect skill detail pages, resolve alias-style slugs, and install from the underlying source repo.

- Directory: [skills.sh](https://skills.sh/)
- CLI/tooling repo: [vercel-labs/skills](https://github.com/vercel-labs/skills)
- Official Vercel skills repo: [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- Example:

```
hermes skills search react --source skills-sh  
hermes skills inspect skills-sh/vercel-labs/json-render/json-render-react  
hermes skills install skills-sh/vercel-labs/json-render/json-render-react --force
```

#### 3. Well-known skill endpoints (`well-known`)[​](index.md#3-well-known-skill-endpoints-well-known "Direct link to 3-well-known-skill-endpoints-well-known")

This is URL-based discovery from sites that publish `/.well-known/skills/index.json`. It is not a single centralized hub — it is a web discovery convention.

- Example live endpoint: [Mintlify docs skills index](https://mintlify.com/docs/.well-known/skills/index.json)
- Reference server implementation: [vercel-labs/skills-handler](https://github.com/vercel-labs/skills-handler)
- Example:

```
hermes skills search https://mintlify.com/docs --source well-known  
hermes skills inspect well-known:https://mintlify.com/docs/.well-known/skills/mintlify  
hermes skills install well-known:https://mintlify.com/docs/.well-known/skills/mintlify
```

#### 4. Direct GitHub skills (`github`)[​](index.md#4-direct-github-skills-github "Direct link to 4-direct-github-skills-github")

Hermes can install directly from GitHub repositories and GitHub-based taps. This is useful when you already know the repo/path or want to add your own custom source repo.

Default taps (browsable without any setup):

- [openai/skills](https://github.com/openai/skills)
- [anthropics/skills](https://github.com/anthropics/skills)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [garrytan/gstack](https://github.com/garrytan/gstack)
- Example:

```
hermes skills install openai/skills/k8s  
hermes skills tap add myorg/skills-repo
```

#### 5. ClawHub (`clawhub`)[​](index.md#5-clawhub-clawhub "Direct link to 5-clawhub-clawhub")

A third-party skills marketplace integrated as a community source.

- Site: [clawhub.ai](https://clawhub.ai/)
- Hermes source id: `clawhub`

#### 6. Claude marketplace-style repos (`claude-marketplace`)[​](index.md#6-claude-marketplace-style-repos-claude-marketplace "Direct link to 6-claude-marketplace-style-repos-claude-marketplace")

Hermes supports marketplace repos that publish Claude-compatible plugin/marketplace manifests.

Known integrated sources include:

- [anthropics/skills](https://github.com/anthropics/skills)
- [aiskillstore/marketplace](https://github.com/aiskillstore/marketplace)

Hermes source id: `claude-marketplace`

#### 7. LobeHub (`lobehub`)[​](index.md#7-lobehub-lobehub "Direct link to 7-lobehub-lobehub")

Hermes can search and convert agent entries from LobeHub's public catalog into installable Hermes skills.

- Site: [LobeHub](https://lobehub.com/)
- Public agents index: [chat-agents.lobehub.com](https://chat-agents.lobehub.com/)
- Backing repo: [lobehub/lobe-chat-agents](https://github.com/lobehub/lobe-chat-agents)
- Hermes source id: `lobehub`

#### 8. Direct URL (`url`)[​](index.md#8-direct-url-url "Direct link to 8-direct-url-url")

Install a single-file `SKILL.md` directly from any HTTP(S) URL — useful when an author hosts a skill on their own site (no hub listing, no GitHub path to type). Hermes fetches the URL, parses the YAML frontmatter, security-scans it, and installs.

- Hermes source id: `url`
- Identifier: the URL itself (no prefix needed)
- Scope: **single-file `SKILL.md`** only. Multi-file skills with `references/` or `scripts/` need a manifest and should be published via one of the other sources above.

```
hermes skills install https://sharethis.chat/SKILL.md  
hermes skills install https://example.com/my-skill/SKILL.md --category productivity
```

Name resolution, in order:

1. `name:` field in the SKILL.md YAML frontmatter (recommended — every well-formed skill has one).
2. Parent directory name from the URL path (e.g. `.../my-skill/SKILL.md` → `my-skill`, or `.../my-skill.md` → `my-skill`), when it's a valid identifier (`^[a-z][a-z0-9_-]*$`).
3. Interactive prompt on a terminal with a TTY.
4. On non-interactive surfaces (the `/skills install` slash command inside the TUI, gateway platforms, scripts), a clean error pointing at the `--name` override.

```
# Frontmatter has no name and the URL slug is unhelpful — supply one:  
hermes skills install https://example.com/SKILL.md --name sharethis-chat  
  
# Or inside a chat session:  
/skills install https://example.com/SKILL.md --name sharethis-chat
```

Trust level is always `community` — the same security scan runs as for every other source. The URL is stored as the install identifier, so `hermes skills update` re-fetches from the same URL automatically when you want to refresh.

### Security scanning and `--force`[​](index.md#security-scanning-and---force "Direct link to security-scanning-and---force")

All hub-installed skills go through a **security scanner** that checks for data exfiltration, prompt injection, destructive commands, supply-chain signals, and other threats.

`hermes skills inspect ...` now also surfaces upstream metadata when available:

- repo URL
- skills.sh detail page URL
- install command
- weekly installs
- upstream security audit statuses
- well-known index/endpoint URLs

Use `--force` when you have reviewed a third-party skill and want to override a non-dangerous policy block:

```
hermes skills install skills-sh/anthropics/skills/pdf --force
```

Important behavior:

- `--force` can override policy blocks for caution/warn-style findings.
- `--force` does **not** override a `dangerous` scan verdict.
- Official optional skills (`official/...`) are treated as builtin trust and do not show the third-party warning panel.

### Trust levels[​](index.md#trust-levels "Direct link to Trust levels")

| Level | Source | Policy |
| --- | --- | --- |
| `builtin` | Ships with Hermes | Always trusted |
| `official` | `optional-skills/` in the repo | Builtin trust, no third-party warning |
| `trusted` | Trusted registries/repos such as `openai/skills`, `anthropics/skills` | More permissive policy than community sources |
| `community` | Everything else (`skills.sh`, well-known endpoints, custom GitHub repos, most marketplaces) | Non-dangerous findings can be overridden with `--force`; `dangerous` verdicts stay blocked |

### Update lifecycle[​](index.md#update-lifecycle "Direct link to Update lifecycle")

The hub now tracks enough provenance to re-check upstream copies of installed skills:

```
hermes skills check          # Report which installed hub skills changed upstream  
hermes skills update         # Reinstall only the skills with updates available  
hermes skills update react   # Update one specific installed hub skill
```

This uses the stored source identifier plus the current upstream bundle content hash to detect drift.

GitHub rate limits

Skills hub operations use the GitHub API, which has a rate limit of 60 requests/hour for unauthenticated users. If you see rate-limit errors during install or search, set `GITHUB_TOKEN` in your `.env` file to increase the limit to 5,000 requests/hour. The error message includes an actionable hint when this happens.

### Publishing a custom skill tap[​](index.md#publishing-a-custom-skill-tap "Direct link to Publishing a custom skill tap")

If you want to share a curated set of skills — for your team, your org, or publicly — you can publish them as a **tap**: a GitHub repository other Hermes users add with `hermes skills tap add <owner/repo>`. No server, no registry sign-up, no release pipeline. Just a directory of `SKILL.md` files.

#### Repo layout[​](index.md#repo-layout "Direct link to Repo layout")

A tap is any GitHub repo (public or private — private needs `GITHUB_TOKEN`) laid out like this:

```
owner/repo  
├── skills/                       # default path; configurable per-tap  
│   ├── my-workflow/  
│   │   ├── SKILL.md              # required  
│   │   ├── references/           # optional supporting files  
│   │   ├── templates/  
│   │   └── scripts/  
│   ├── another-skill/  
│   │   └── SKILL.md  
│   └── third-skill/  
│       └── SKILL.md  
└── README.md                     # optional but helpful
```

Rules:

- Each skill lives in its own directory under the tap's root path (default `skills/`).
- The directory name becomes the skill's install slug.
- Each skill directory must contain a `SKILL.md` with standard [SKILL.md frontmatter](index.md#skillmd-format) (`name`, `description`, plus optional `metadata.hermes.tags`, `version`, `author`, `platforms`, `metadata.hermes.config`).
- Subdirectories like `references/`, `templates/`, `scripts/`, `assets/` are downloaded alongside `SKILL.md` at install time.
- Skills whose directory name starts with `.` or `_` are ignored.

Hermes discovers skills by listing every subdirectory of the tap path and probing each for `SKILL.md`.

#### Minimal tap example[​](index.md#minimal-tap-example "Direct link to Minimal tap example")

```
my-org/hermes-skills  
└── skills/  
    └── deploy-runbook/  
        └── SKILL.md
```

`skills/deploy-runbook/SKILL.md`:

```
---  
name: deploy-runbook  
description: Our deployment runbook — services, rollback, Slack channels  
version: 1.0.0  
author: My Org Platform Team  
metadata:  
  hermes:  
    tags: [deployment, runbook, internal]  
---  
  
# Deploy Runbook  
  
Step 1: ...
```

After pushing that to GitHub, any Hermes user can subscribe and install:

```
hermes skills tap add my-org/hermes-skills  
hermes skills search deploy  
hermes skills install my-org/hermes-skills/deploy-runbook
```

#### Non-default paths[​](index.md#non-default-paths "Direct link to Non-default paths")

If your skills don't live under `skills/` (common when you're adding a `skills/` subtree to an existing project), edit the tap entry in `~/.hermes/.hub/taps.json`:

```
{  
  "taps": [  
    {"repo": "my-org/platform-docs", "path": "internal/skills/"}  
  ]  
}
```

The `hermes skills tap add` CLI defaults new taps to `path: "skills/"`; edit the file directly if you need a different path. `hermes skills tap list` shows the effective path per tap.

#### Installing individual skills directly (without adding a tap)[​](index.md#installing-individual-skills-directly-without-adding-a-tap "Direct link to Installing individual skills directly (without adding a tap)")

Users can also install a single skill from any public GitHub repo without adding the whole repo as a tap:

```
hermes skills install owner/repo/skills/my-workflow
```

Useful when you want to share one skill without asking the user to subscribe to your whole registry.

#### Trust levels for taps[​](index.md#trust-levels-for-taps "Direct link to Trust levels for taps")

New taps are assigned `community` trust by default. Skills installed from them run through the standard security scan and show the third-party warning panel on first install. If your org or a widely-trusted source should get higher trust, add its repo to `TRUSTED_REPOS` in `tools/skills_hub.py` (requires a Hermes core PR).

#### Tap management[​](index.md#tap-management "Direct link to Tap management")

```
hermes skills tap list                                # show all configured taps  
hermes skills tap add myorg/skills-repo               # add (default path: skills/)  
hermes skills tap remove myorg/skills-repo            # remove
```

Inside a running session:

```
/skills tap list  
/skills tap add myorg/skills-repo  
/skills tap remove myorg/skills-repo
```

Taps are stored in `~/.hermes/.hub/taps.json` (created on demand).

## Bundled skill updates (`hermes skills reset`)[​](index.md#bundled-skill-updates-hermes-skills-reset "Direct link to bundled-skill-updates-hermes-skills-reset")

Hermes ships with a set of bundled skills in `skills/` inside the repo. On install and on every `hermes update`, a sync pass copies those into `~/.hermes/skills/` and records a manifest at `~/.hermes/skills/.bundled_manifest` mapping each skill name to the content hash at the time it was synced (the **origin hash**).

On each sync, Hermes recomputes the hash of your local copy and compares it to the origin hash:

- **Unchanged** → safe to pull upstream changes, copy the new bundled version in, record the new origin hash.
- **Changed** → treated as **user-modified** and skipped forever, so your edits never get stomped.

The protection is good, but it has one sharp edge. If you edit a bundled skill and then later want to abandon your changes and go back to the bundled version by just copy-pasting from `~/.hermes/hermes-agent/skills/`, the manifest still holds the *old* origin hash from whenever the last successful sync ran. Your fresh copy-paste contents (current bundled hash) won't match that stale origin hash, so sync keeps flagging it as user-modified.

`hermes skills reset` is the escape hatch:

```
# Safe: clears the manifest entry for this skill. Your current copy is preserved,  
# but the next sync re-baselines against it so future updates work normally.  
hermes skills reset google-workspace  
  
# Full restore: also deletes your local copy and re-copies the current bundled  
# version. Use this when you want the pristine upstream skill back.  
hermes skills reset google-workspace --restore  
  
# Non-interactive (e.g. in scripts or TUI mode) — skip the --restore confirmation.  
hermes skills reset google-workspace --restore --yes
```

The same command works in chat as a slash command:

```
/skills reset google-workspace  
/skills reset google-workspace --restore
```

Profiles

Each profile has its own `.bundled_manifest` under its own `HERMES_HOME`, so `hermes -p coder skills reset <name>` only affects that profile.

### Slash commands (inside chat)[​](index.md#slash-commands-inside-chat "Direct link to Slash commands (inside chat)")

All the same commands work with `/skills`:

```
/skills browse  
/skills search react --source skills-sh  
/skills search https://mintlify.com/docs --source well-known  
/skills inspect skills-sh/vercel-labs/json-render/json-render-react  
/skills install openai/skills/skill-creator --force  
/skills check  
/skills update  
/skills reset google-workspace  
/skills list
```

Official optional skills still use identifiers like `official/security/1password` and `official/migration/openclaw-migration`.

- [Using Skills](index.md#using-skills)
- [Progressive Disclosure](index.md#progressive-disclosure)
- [SKILL.md Format](index.md#skillmd-format)
  - [Platform-Specific Skills](index.md#platform-specific-skills)
  - [Conditional Activation (Fallback Skills)](index.md#conditional-activation-fallback-skills)
- [Secure Setup on Load](index.md#secure-setup-on-load)
  - [Skill Config Settings](index.md#skill-config-settings)
- [Skill Directory Structure](index.md#skill-directory-structure)
- [External Skill Directories](index.md#external-skill-directories)
  - [How it works](index.md#how-it-works)
  - [Example](index.md#example)
- [Agent-Managed Skills (skill\_manage tool)](index.md#agent-managed-skills-skill_manage-tool)
  - [When the Agent Creates Skills](index.md#when-the-agent-creates-skills)
  - [Actions](index.md#actions)
- [Skills Hub](index.md#skills-hub)
  - [Common commands](index.md#common-commands)
  - [Supported hub sources](index.md#supported-hub-sources)
  - [Integrated hubs and registries](index.md#integrated-hubs-and-registries)
  - [Security scanning and `--force`](index.md#security-scanning-and---force)
  - [Trust levels](index.md#trust-levels)
  - [Update lifecycle](index.md#update-lifecycle)
  - [Publishing a custom skill tap](index.md#publishing-a-custom-skill-tap)
- [Bundled skill updates (`hermes skills reset`)](index.md#bundled-skill-updates-hermes-skills-reset)
  - [Slash commands (inside chat)](index.md#slash-commands-inside-chat)
