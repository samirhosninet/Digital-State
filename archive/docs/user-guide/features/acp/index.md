---
source_url: https://hermes-agent.nousresearch.com/docs/user-guide/features/acp
title: ACP Editor Integration | Hermes Agent
archived_at: 2026-05-13T02:40:25Z
---

Hermes Agent can run as an ACP server, letting ACP-compatible editors talk to Hermes over stdio and render:

- chat messages
- tool activity
- file diffs
- terminal commands
- approval prompts
- streamed thinking / response chunks

ACP is a good fit when you want Hermes to behave like an editor-native coding agent instead of a standalone CLI or messaging bot.

## What Hermes exposes in ACP mode[​](index.md#what-hermes-exposes-in-acp-mode "Direct link to What Hermes exposes in ACP mode")

Hermes runs with a curated `hermes-acp` toolset designed for editor workflows. It includes:

- file tools: `read_file`, `write_file`, `patch`, `search_files`
- terminal tools: `terminal`, `process`
- web/browser tools
- memory, todo, session search
- skills
- execute\_code and delegate\_task
- vision

It intentionally excludes things that do not fit typical editor UX, such as messaging delivery and cronjob management.

## Installation[​](index.md#installation "Direct link to Installation")

Install Hermes normally, then add the ACP extra:

```
pip install -e '.[acp]'
```

This installs the `agent-client-protocol` dependency and enables:

- `hermes acp`
- `hermes-acp`
- `python -m acp_adapter`

## Launching the ACP server[​](index.md#launching-the-acp-server "Direct link to Launching the ACP server")

Any of the following starts Hermes in ACP mode:

```
hermes acp
```

```
hermes-acp
```

```
python -m acp_adapter
```

Hermes logs to stderr so stdout remains reserved for ACP JSON-RPC traffic.

## Editor setup[​](index.md#editor-setup "Direct link to Editor setup")

### VS Code[​](index.md#vs-code "Direct link to VS Code")

Install the [ACP Client](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client) extension.

To connect:

1. Open the ACP Client panel from the Activity Bar.
2. Select **Hermes Agent** from the built-in agent list.
3. Connect and start chatting.

If you want to define Hermes manually, add it through VS Code settings under `acp.agents`:

```
{  
  "acp.agents": {  
    "Hermes Agent": {  
      "command": "hermes",  
      "args": ["acp"]  
    }  
  }  
}
```

### Zed[​](index.md#zed "Direct link to Zed")

Example settings snippet:

```
{  
  "agent_servers": {  
    "hermes-agent": {  
      "type": "custom",  
      "command": "hermes",  
      "args": ["acp"],  
    },  
  },  
}
```

### JetBrains[​](index.md#jetbrains "Direct link to JetBrains")

Use an ACP-compatible plugin and point it at:

```
/path/to/hermes-agent/acp_registry
```

## Registry manifest[​](index.md#registry-manifest "Direct link to Registry manifest")

The ACP registry manifest lives at:

```
acp_registry/agent.json
```

It advertises a command-based agent whose launch command is:

```
hermes acp
```

## Configuration and credentials[​](index.md#configuration-and-credentials "Direct link to Configuration and credentials")

ACP mode uses the same Hermes configuration as the CLI:

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/skills/`
- `~/.hermes/state.db`

Provider resolution uses Hermes' normal runtime resolver, so ACP inherits the currently configured provider and credentials.

## Session behavior[​](index.md#session-behavior "Direct link to Session behavior")

ACP sessions are tracked by the ACP adapter's in-memory session manager while the server is running.

Each session stores:

- session ID
- working directory
- selected model
- current conversation history
- cancel event

The underlying `AIAgent` still uses Hermes' normal persistence/logging paths, but ACP `list/load/resume/fork` are scoped to the currently running ACP server process.

## Working directory behavior[​](index.md#working-directory-behavior "Direct link to Working directory behavior")

ACP sessions bind the editor's cwd to the Hermes task ID so file and terminal tools run relative to the editor workspace, not the server process cwd.

## Approvals[​](index.md#approvals "Direct link to Approvals")

Dangerous terminal commands can be routed back to the editor as approval prompts. ACP approval options are simpler than the CLI flow:

- allow once
- allow always
- deny

On timeout or error, the approval bridge denies the request.

## Troubleshooting[​](index.md#troubleshooting "Direct link to Troubleshooting")

### ACP agent does not appear in the editor[​](index.md#acp-agent-does-not-appear-in-the-editor "Direct link to ACP agent does not appear in the editor")

Check:

- the editor is pointed at the correct `acp_registry/` path
- Hermes is installed and on your PATH
- the ACP extra is installed (`pip install -e '.[acp]'`)

### ACP starts but immediately errors[​](index.md#acp-starts-but-immediately-errors "Direct link to ACP starts but immediately errors")

Try these checks:

```
hermes doctor  
hermes status  
hermes acp
```

### Missing credentials[​](index.md#missing-credentials "Direct link to Missing credentials")

ACP mode does not have its own login flow. It uses Hermes' existing provider setup. Configure credentials with:

```
hermes model
```

or by editing `~/.hermes/.env`.

## See also[​](index.md#see-also "Direct link to See also")

- [ACP Internals](../../../developer-guide/acp-internals/index.md)
- [Provider Runtime Resolution](../../../developer-guide/provider-runtime/index.md)
- [Tools Runtime](../../../developer-guide/tools-runtime/index.md)

- [What Hermes exposes in ACP mode](index.md#what-hermes-exposes-in-acp-mode)
- [Installation](index.md#installation)
- [Launching the ACP server](index.md#launching-the-acp-server)
- [Editor setup](index.md#editor-setup)
  - [VS Code](index.md#vs-code)
  - [Zed](index.md#zed)
  - [JetBrains](index.md#jetbrains)
- [Registry manifest](index.md#registry-manifest)
- [Configuration and credentials](index.md#configuration-and-credentials)
- [Session behavior](index.md#session-behavior)
- [Working directory behavior](index.md#working-directory-behavior)
- [Approvals](index.md#approvals)
- [Troubleshooting](index.md#troubleshooting)
  - [ACP agent does not appear in the editor](index.md#acp-agent-does-not-appear-in-the-editor)
  - [ACP starts but immediately errors](index.md#acp-starts-but-immediately-errors)
  - [Missing credentials](index.md#missing-credentials)
- [See also](index.md#see-also)
