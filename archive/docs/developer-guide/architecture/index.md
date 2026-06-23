---
source_url: https://hermes-agent.nousresearch.com/docs/developer-guide/architecture
title: Architecture | Hermes Agent
archived_at: 2026-05-13T02:40:25Z
---

This page is the top-level map of Hermes Agent internals. Use it to orient yourself in the codebase, then dive into subsystem-specific docs for implementation details.

## System Overview[​](index.md#system-overview "Direct link to System Overview")

```
┌─────────────────────────────────────────────────────────────────────┐  
│                        Entry Points                                  │  
│                                                                      │  
│  CLI (cli.py)    Gateway (gateway/run.py)    ACP (acp_adapter/)     │  
│  Batch Runner    API Server                  Python Library          │  
└──────────┬──────────────┬───────────────────────┬───────────────────┘  
           │              │                       │  
           ▼              ▼                       ▼  
┌─────────────────────────────────────────────────────────────────────┐  
│                     AIAgent (run_agent.py)                          │  
│                                                                     │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  
│  │ Prompt       │  │ Provider     │  │ Tool         │               │  
│  │ Builder      │  │ Resolution   │  │ Dispatch     │               │  
│  │ (prompt_     │  │ (runtime_    │  │ (model_      │               │  
│  │  builder.py) │  │  provider.py)│  │  tools.py)   │               │  
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │  
│         │                 │                 │                       │  
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐               │  
│  │ Compression  │  │ 3 API Modes  │  │ Tool Registry│               │  
│  │ & Caching    │  │ chat_compl.  │  │ (registry.py)│               │  
│  │              │  │ codex_resp.  │  │ 70+ tools    │               │  
│  │              │  │ anthropic    │  │ 28 toolsets  │               │  
│  └──────────────┘  └──────────────┘  └──────────────┘               │  
└─────────┴─────────────────┴─────────────────┴───────────────────────┘  
           │                                    │  
           ▼                                    ▼  
┌───────────────────┐              ┌──────────────────────┐  
│ Session Storage   │              │ Tool Backends         │  
│ (SQLite + FTS5)   │              │ Terminal (7 backends) │  
│ hermes_state.py   │              │ Browser (5 backends)  │  
│ gateway/session.py│              │ Web (4 backends)      │  
└───────────────────┘              │ MCP (dynamic)         │  
                                   │ File, Vision, etc.    │  
                                   └──────────────────────┘
```

## Directory Structure[​](index.md#directory-structure "Direct link to Directory Structure")

```
hermes-agent/  
├── run_agent.py              # AIAgent — core conversation loop (large file)  
├── cli.py                    # HermesCLI — interactive terminal UI (large file)  
├── model_tools.py            # Tool discovery, schema collection, dispatch  
├── toolsets.py               # Tool groupings and platform presets  
├── hermes_state.py           # SQLite session/state database with FTS5  
├── hermes_constants.py       # HERMES_HOME, profile-aware paths  
├── batch_runner.py           # Batch trajectory generation  
│  
├── agent/                    # Agent internals  
│   ├── prompt_builder.py     # System prompt assembly  
│   ├── context_engine.py     # ContextEngine ABC (pluggable)  
│   ├── context_compressor.py # Default engine — lossy summarization  
│   ├── prompt_caching.py     # Anthropic prompt caching  
│   ├── auxiliary_client.py   # Auxiliary LLM for side tasks (vision, summarization)  
│   ├── model_metadata.py     # Model context lengths, token estimation  
│   ├── models_dev.py         # models.dev registry integration  
│   ├── anthropic_adapter.py  # Anthropic Messages API format conversion  
│   ├── display.py            # KawaiiSpinner, tool preview formatting  
│   ├── skill_commands.py     # Skill slash commands  
│   ├── memory_manager.py    # Memory manager orchestration  
│   ├── memory_provider.py   # Memory provider ABC  
│   └── trajectory.py         # Trajectory saving helpers  
│  
├── hermes_cli/               # CLI subcommands and setup  
│   ├── main.py               # Entry point — all `hermes` subcommands (large file)  
│   ├── config.py             # DEFAULT_CONFIG, OPTIONAL_ENV_VARS, migration  
│   ├── commands.py           # COMMAND_REGISTRY — central slash command definitions  
│   ├── auth.py               # PROVIDER_REGISTRY, credential resolution  
│   ├── runtime_provider.py   # Provider → api_mode + credentials  
│   ├── models.py             # Model catalog, provider model lists  
│   ├── model_switch.py       # /model command logic (CLI + gateway shared)  
│   ├── setup.py              # Interactive setup wizard (large file)  
│   ├── skin_engine.py        # CLI theming engine  
│   ├── skills_config.py      # hermes skills — enable/disable per platform  
│   ├── skills_hub.py         # /skills slash command  
│   ├── tools_config.py       # hermes tools — enable/disable per platform  
│   ├── plugins.py            # PluginManager — discovery, loading, hooks  
│   ├── callbacks.py          # Terminal callbacks (clarify, sudo, approval)  
│   └── gateway.py            # hermes gateway start/stop  
│  
├── tools/                    # Tool implementations (one file per tool)  
│   ├── registry.py           # Central tool registry  
│   ├── approval.py           # Dangerous command detection  
│   ├── terminal_tool.py      # Terminal orchestration  
│   ├── process_registry.py   # Background process management  
│   ├── file_tools.py         # read_file, write_file, patch, search_files  
│   ├── web_tools.py          # web_search, web_extract  
│   ├── browser_tool.py       # 10 browser automation tools  
│   ├── code_execution_tool.py # execute_code sandbox  
│   ├── delegate_tool.py      # Subagent delegation  
│   ├── mcp_tool.py           # MCP client (large file)  
│   ├── credential_files.py   # File-based credential passthrough  
│   ├── env_passthrough.py    # Env var passthrough for sandboxes  
│   ├── ansi_strip.py         # ANSI escape stripping  
│   └── environments/         # Terminal backends (local, docker, ssh, modal, daytona, singularity)  
│  
├── gateway/                  # Messaging platform gateway  
│   ├── run.py                # GatewayRunner — message dispatch (large file)  
│   ├── session.py            # SessionStore — conversation persistence  
│   ├── delivery.py           # Outbound message delivery  
│   ├── pairing.py            # DM pairing authorization  
│   ├── hooks.py              # Hook discovery and lifecycle events  
│   ├── mirror.py             # Cross-session message mirroring  
│   ├── status.py             # Token locks, profile-scoped process tracking  
│   ├── builtin_hooks/        # Extension point for always-registered hooks (none shipped)  
│   └── platforms/            # 20 adapters: telegram, discord, slack, whatsapp,  
│                             #   signal, matrix, mattermost, email, sms,  
│                             #   dingtalk, feishu, wecom, wecom_callback, weixin,  
│                             #   bluebubbles, qqbot, homeassistant, webhook, api_server,  
│                             #   yuanbao  
│  
├── acp_adapter/              # ACP server (VS Code / Zed / JetBrains)  
├── cron/                     # Scheduler (jobs.py, scheduler.py)  
├── plugins/memory/           # Memory provider plugins  
├── plugins/context_engine/   # Context engine plugins  
├── environments/             # RL training environments (Atropos)  
├── skills/                   # Bundled skills (always available)  
├── optional-skills/          # Official optional skills (install explicitly)  
├── website/                  # Docusaurus documentation site  
└── tests/                    # Pytest suite (~3,000+ tests)
```

## Data Flow[​](index.md#data-flow "Direct link to Data Flow")

### CLI Session[​](index.md#cli-session "Direct link to CLI Session")

```
User input → HermesCLI.process_input()  
  → AIAgent.run_conversation()  
    → prompt_builder.build_system_prompt()  
    → runtime_provider.resolve_runtime_provider()  
    → API call (chat_completions / codex_responses / anthropic_messages)  
    → tool_calls? → model_tools.handle_function_call() → loop  
    → final response → display → save to SessionDB
```

### Gateway Message[​](index.md#gateway-message "Direct link to Gateway Message")

```
Platform event → Adapter.on_message() → MessageEvent  
  → GatewayRunner._handle_message()  
    → authorize user  
    → resolve session key  
    → create AIAgent with session history  
    → AIAgent.run_conversation()  
    → deliver response back through adapter
```

### Cron Job[​](index.md#cron-job "Direct link to Cron Job")

```
Scheduler tick → load due jobs from jobs.json  
  → create fresh AIAgent (no history)  
  → inject attached skills as context  
  → run job prompt  
  → deliver response to target platform  
  → update job state and next_run
```

## Recommended Reading Order[​](index.md#recommended-reading-order "Direct link to Recommended Reading Order")

If you are new to the codebase:

1. **This page** — orient yourself
2. **[Agent Loop Internals](../agent-loop/index.md)** — how AIAgent works
3. **[Prompt Assembly](../prompt-assembly/index.md)** — system prompt construction
4. **[Provider Runtime Resolution](../provider-runtime/index.md)** — how providers are selected
5. **[Adding Providers](../adding-providers/index.md)** — practical guide to adding a new provider
6. **[Tools Runtime](../tools-runtime/index.md)** — tool registry, dispatch, environments
7. **[Session Storage](../session-storage/index.md)** — SQLite schema, FTS5, session lineage
8. **[Gateway Internals](../gateway-internals/index.md)** — messaging platform gateway
9. **[Context Compression & Prompt Caching](../context-compression-and-caching/index.md)** — compression and caching
10. **[ACP Internals](../acp-internals/index.md)** — IDE integration
11. **[Environments, Benchmarks & Data Generation](../environments/index.md)** — RL training

## Major Subsystems[​](index.md#major-subsystems "Direct link to Major Subsystems")

### Agent Loop[​](index.md#agent-loop "Direct link to Agent Loop")

The synchronous orchestration engine (`AIAgent` in `run_agent.py`). Handles provider selection, prompt construction, tool execution, retries, fallback, callbacks, compression, and persistence. Supports three API modes for different provider backends.

→ [Agent Loop Internals](../agent-loop/index.md)

### Prompt System[​](index.md#prompt-system "Direct link to Prompt System")

Prompt construction and maintenance across the conversation lifecycle:

- **`prompt_builder.py`** — Assembles the system prompt from: personality (SOUL.md), memory (MEMORY.md, USER.md), skills, context files (AGENTS.md, .hermes.md), tool-use guidance, and model-specific instructions
- **`prompt_caching.py`** — Applies Anthropic cache breakpoints for prefix caching
- **`context_compressor.py`** — Summarizes middle conversation turns when context exceeds thresholds

→ [Prompt Assembly](../prompt-assembly/index.md), [Context Compression & Prompt Caching](../context-compression-and-caching/index.md)

### Provider Resolution[​](index.md#provider-resolution "Direct link to Provider Resolution")

A shared runtime resolver used by CLI, gateway, cron, ACP, and auxiliary calls. Maps `(provider, model)` tuples to `(api_mode, api_key, base_url)`. Handles 18+ providers, OAuth flows, credential pools, and alias resolution.

→ [Provider Runtime Resolution](../provider-runtime/index.md)

### Tool System[​](index.md#tool-system "Direct link to Tool System")

Central tool registry (`tools/registry.py`) with 70+ registered tools across ~28 toolsets. Each tool file self-registers at import time. The registry handles schema collection, dispatch, availability checking, and error wrapping. Terminal tools support 7 backends (local, Docker, SSH, Daytona, Modal, Singularity, Vercel Sandbox).

→ [Tools Runtime](../tools-runtime/index.md)

### Session Persistence[​](index.md#session-persistence "Direct link to Session Persistence")

SQLite-based session storage with FTS5 full-text search. Sessions have lineage tracking (parent/child across compressions), per-platform isolation, and atomic writes with contention handling.

→ [Session Storage](../session-storage/index.md)

### Messaging Gateway[​](index.md#messaging-gateway "Direct link to Messaging Gateway")

Long-running process with 20 platform adapters, unified session routing, user authorization (allowlists + DM pairing), slash command dispatch, hook system, cron ticking, and background maintenance.

→ [Gateway Internals](../gateway-internals/index.md)

### Plugin System[​](index.md#plugin-system "Direct link to Plugin System")

Three discovery sources: `~/.hermes/plugins/` (user), `.hermes/plugins/` (project), and pip entry points. Plugins register tools, hooks, and CLI commands through a context API. Two specialized plugin types exist: memory providers (`plugins/memory/`) and context engines (`plugins/context_engine/`). Both are single-select — only one of each can be active at a time, configured via `hermes plugins` or `config.yaml`.

→ [Plugin Guide](../../guides/build-a-hermes-plugin/index.md), [Memory Provider Plugin](../memory-provider-plugin/index.md)

### Cron[​](index.md#cron "Direct link to Cron")

First-class agent tasks (not shell tasks). Jobs store in JSON, support multiple schedule formats, can attach skills and scripts, and deliver to any platform.

→ [Cron Internals](../cron-internals/index.md)

### ACP Integration[​](index.md#acp-integration "Direct link to ACP Integration")

Exposes Hermes as an editor-native agent over stdio/JSON-RPC for VS Code, Zed, and JetBrains.

→ [ACP Internals](../acp-internals/index.md)

### RL / Environments / Trajectories[​](index.md#rl--environments--trajectories "Direct link to RL / Environments / Trajectories")

Full environment framework for evaluation and RL training. Integrates with Atropos, supports multiple tool-call parsers, and generates ShareGPT-format trajectories.

→ [Environments, Benchmarks & Data Generation](../environments/index.md), [Trajectories & Training Format](../trajectory-format/index.md)

## Design Principles[​](index.md#design-principles "Direct link to Design Principles")

| Principle | What it means in practice |
| --- | --- |
| **Prompt stability** | System prompt doesn't change mid-conversation. No cache-breaking mutations except explicit user actions (`/model`). |
| **Observable execution** | Every tool call is visible to the user via callbacks. Progress updates in CLI (spinner) and gateway (chat messages). |
| **Interruptible** | API calls and tool execution can be cancelled mid-flight by user input or signals. |
| **Platform-agnostic core** | One AIAgent class serves CLI, gateway, ACP, batch, and API server. Platform differences live in the entry point, not the agent. |
| **Loose coupling** | Optional subsystems (MCP, plugins, memory providers, RL environments) use registry patterns and check\_fn gating, not hard dependencies. |
| **Profile isolation** | Each profile (`hermes -p <name>`) gets its own HERMES\_HOME, config, memory, sessions, and gateway PID. Multiple profiles run concurrently. |

## File Dependency Chain[​](index.md#file-dependency-chain "Direct link to File Dependency Chain")

```
tools/registry.py  (no deps — imported by all tool files)  
       ↑  
tools/*.py  (each calls registry.register() at import time)  
       ↑  
model_tools.py  (imports tools/registry + triggers tool discovery)  
       ↑  
run_agent.py, cli.py, batch_runner.py, environments/
```

This chain means tool registration happens at import time, before any agent instance is created. Any `tools/*.py` file with a top-level `registry.register()` call is auto-discovered — no manual import list needed.

- [System Overview](index.md#system-overview)
- [Directory Structure](index.md#directory-structure)
- [Data Flow](index.md#data-flow)
  - [CLI Session](index.md#cli-session)
  - [Gateway Message](index.md#gateway-message)
  - [Cron Job](index.md#cron-job)
- [Recommended Reading Order](index.md#recommended-reading-order)
- [Major Subsystems](index.md#major-subsystems)
  - [Agent Loop](index.md#agent-loop)
  - [Prompt System](index.md#prompt-system)
  - [Provider Resolution](index.md#provider-resolution)
  - [Tool System](index.md#tool-system)
  - [Session Persistence](index.md#session-persistence)
  - [Messaging Gateway](index.md#messaging-gateway)
  - [Plugin System](index.md#plugin-system)
  - [Cron](index.md#cron)
  - [ACP Integration](index.md#acp-integration)
  - [RL / Environments / Trajectories](index.md#rl--environments--trajectories)
- [Design Principles](index.md#design-principles)
- [File Dependency Chain](index.md#file-dependency-chain)
