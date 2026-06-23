---
source_url: https://hermes-agent.nousresearch.com/docs/reference/mcp-config-reference
title: MCP Config Reference | Hermes Agent
archived_at: 2026-05-13T02:40:25Z
---

This page is the compact reference companion to the main MCP docs.

For conceptual guidance, see:

- [MCP (Model Context Protocol)](../../user-guide/features/mcp/index.md)
- [Use MCP with Hermes](../../guides/use-mcp-with-hermes/index.md)

## Root config shape[​](index.md#root-config-shape "Direct link to Root config shape")

```
mcp_servers:  
  <server_name>:  
    command: "..."      # stdio servers  
    args: []  
    env: {}  
  
    # OR  
    url: "..."          # HTTP servers  
    headers: {}  
  
    enabled: true  
    timeout: 120  
    connect_timeout: 60  
    tools:  
      include: []  
      exclude: []  
      resources: true  
      prompts: true
```

## Server keys[​](index.md#server-keys "Direct link to Server keys")

| Key | Type | Applies to | Meaning |
| --- | --- | --- | --- |
| `command` | string | stdio | Executable to launch |
| `args` | list | stdio | Arguments for the subprocess |
| `env` | mapping | stdio | Environment passed to the subprocess |
| `url` | string | HTTP | Remote MCP endpoint |
| `headers` | mapping | HTTP | Headers for remote server requests |
| `enabled` | bool | both | Skip the server entirely when false |
| `timeout` | number | both | Tool call timeout |
| `connect_timeout` | number | both | Initial connection timeout |
| `tools` | mapping | both | Filtering and utility-tool policy |
| `auth` | string | HTTP | Authentication method. Set to `oauth` to enable OAuth 2.1 with PKCE |
| `sampling` | mapping | both | Server-initiated LLM request policy (see MCP guide) |

## `tools` policy keys[​](index.md#tools-policy-keys "Direct link to tools-policy-keys")

| Key | Type | Meaning |
| --- | --- | --- |
| `include` | string or list | Whitelist server-native MCP tools |
| `exclude` | string or list | Blacklist server-native MCP tools |
| `resources` | bool-like | Enable/disable `list_resources` + `read_resource` |
| `prompts` | bool-like | Enable/disable `list_prompts` + `get_prompt` |

## Filtering semantics[​](index.md#filtering-semantics "Direct link to Filtering semantics")

### `include`[​](index.md#include "Direct link to include")

If `include` is set, only those server-native MCP tools are registered.

```
tools:  
  include: [create_issue, list_issues]
```

### `exclude`[​](index.md#exclude "Direct link to exclude")

If `exclude` is set and `include` is not, every server-native MCP tool except those names is registered.

```
tools:  
  exclude: [delete_customer]
```

### Precedence[​](index.md#precedence "Direct link to Precedence")

If both are set, `include` wins.

```
tools:  
  include: [create_issue]  
  exclude: [create_issue, delete_issue]
```

Result:

- `create_issue` is still allowed
- `delete_issue` is ignored because `include` takes precedence

## Utility-tool policy[​](index.md#utility-tool-policy "Direct link to Utility-tool policy")

Hermes may register these utility wrappers per MCP server:

Resources:

- `list_resources`
- `read_resource`

Prompts:

- `list_prompts`
- `get_prompt`

### Disable resources[​](index.md#disable-resources "Direct link to Disable resources")

```
tools:  
  resources: false
```

### Disable prompts[​](index.md#disable-prompts "Direct link to Disable prompts")

```
tools:  
  prompts: false
```

### Capability-aware registration[​](index.md#capability-aware-registration "Direct link to Capability-aware registration")

Even when `resources: true` or `prompts: true`, Hermes only registers those utility tools if the MCP session actually exposes the corresponding capability.

So this is normal:

- you enable prompts
- but no prompt utilities appear
- because the server does not support prompts

## `enabled: false`[​](index.md#enabled-false "Direct link to enabled-false")

```
mcp_servers:  
  legacy:  
    url: "https://mcp.legacy.internal"  
    enabled: false
```

Behavior:

- no connection attempt
- no discovery
- no tool registration
- config remains in place for later reuse

## Empty result behavior[​](index.md#empty-result-behavior "Direct link to Empty result behavior")

If filtering removes all server-native tools and no utility tools are registered, Hermes does not create an empty MCP runtime toolset for that server.

## Example configs[​](index.md#example-configs "Direct link to Example configs")

### Safe GitHub allowlist[​](index.md#safe-github-allowlist "Direct link to Safe GitHub allowlist")

```
mcp_servers:  
  github:  
    command: "npx"  
    args: ["-y", "@modelcontextprotocol/server-github"]  
    env:  
      GITHUB_PERSONAL_ACCESS_TOKEN: "***"  
    tools:  
      include: [list_issues, create_issue, update_issue, search_code]  
      resources: false  
      prompts: false
```

### Stripe blacklist[​](index.md#stripe-blacklist "Direct link to Stripe blacklist")

```
mcp_servers:  
  stripe:  
    url: "https://mcp.stripe.com"  
    headers:  
      Authorization: "Bearer ***"  
    tools:  
      exclude: [delete_customer, refund_payment]
```

### Resource-only docs server[​](index.md#resource-only-docs-server "Direct link to Resource-only docs server")

```
mcp_servers:  
  docs:  
    url: "https://mcp.docs.example.com"  
    tools:  
      include: []  
      resources: true  
      prompts: false
```

## Reloading config[​](index.md#reloading-config "Direct link to Reloading config")

After changing MCP config, reload servers with:

```
/reload-mcp
```

## Tool naming[​](index.md#tool-naming "Direct link to Tool naming")

Server-native MCP tools become:

```
mcp_<server>_<tool>
```

Examples:

- `mcp_github_create_issue`
- `mcp_filesystem_read_file`
- `mcp_my_api_query_data`

Utility tools follow the same prefixing pattern:

- `mcp_<server>_list_resources`
- `mcp_<server>_read_resource`
- `mcp_<server>_list_prompts`
- `mcp_<server>_get_prompt`

### Name sanitization[​](index.md#name-sanitization "Direct link to Name sanitization")

Hyphens (`-`) and dots (`.`) in both server names and tool names are replaced with underscores before registration. This ensures tool names are valid identifiers for LLM function-calling APIs.

For example, a server named `my-api` exposing a tool called `list-items.v2` becomes:

```
mcp_my_api_list_items_v2
```

Keep this in mind when writing `include` / `exclude` filters — use the **original** MCP tool name (with hyphens/dots), not the sanitized version.

## OAuth 2.1 authentication[​](index.md#oauth-21-authentication "Direct link to OAuth 2.1 authentication")

For HTTP servers that require OAuth, set `auth: oauth` on the server entry:

```
mcp_servers:  
  protected_api:  
    url: "https://mcp.example.com/mcp"  
    auth: oauth
```

Behavior:

- Hermes uses the MCP SDK's OAuth 2.1 PKCE flow (metadata discovery, dynamic client registration, token exchange, and refresh)
- On first connect, a browser window opens for authorization
- Tokens are persisted to `~/.hermes/mcp-tokens/<server>.json` and reused across sessions
- Token refresh is automatic; re-authorization only happens when refresh fails
- Only applies to HTTP/StreamableHTTP transport (`url`-based servers)

- [Root config shape](index.md#root-config-shape)
- [Server keys](index.md#server-keys)
- [`tools` policy keys](index.md#tools-policy-keys)
- [Filtering semantics](index.md#filtering-semantics)
  - [`include`](index.md#include)
  - [`exclude`](index.md#exclude)
  - [Precedence](index.md#precedence)
- [Utility-tool policy](index.md#utility-tool-policy)
  - [Disable resources](index.md#disable-resources)
  - [Disable prompts](index.md#disable-prompts)
  - [Capability-aware registration](index.md#capability-aware-registration)
- [`enabled: false`](index.md#enabled-false)
- [Empty result behavior](index.md#empty-result-behavior)
- [Example configs](index.md#example-configs)
  - [Safe GitHub allowlist](index.md#safe-github-allowlist)
  - [Stripe blacklist](index.md#stripe-blacklist)
  - [Resource-only docs server](index.md#resource-only-docs-server)
- [Reloading config](index.md#reloading-config)
- [Tool naming](index.md#tool-naming)
  - [Name sanitization](index.md#name-sanitization)
- [OAuth 2.1 authentication](index.md#oauth-21-authentication)
