---
source_url: https://hermes-agent.nousresearch.com/docs/user-guide/profiles
title: Profiles - Running Multiple Agents | Hermes Agent
archived_at: 2026-05-13T02:40:25Z
---

Run multiple independent Hermes agents on the same machine — each with its own config, API keys, memory, sessions, skills, and gateway state.

## What are profiles?[​](index.md#what-are-profiles "Direct link to What are profiles?")

A profile is a separate Hermes home directory. Each profile gets its own directory containing its own `config.yaml`, `.env`, `SOUL.md`, memories, sessions, skills, cron jobs, and state database. Profiles let you run separate agents for different purposes — a coding assistant, a personal bot, a research agent — without mixing up Hermes state.

When you create a profile, it automatically becomes its own command. Create a profile called `coder` and you immediately have `coder chat`, `coder setup`, `coder gateway start`, etc.

## Quick start[​](index.md#quick-start "Direct link to Quick start")

```
hermes profile create coder       # creates profile + "coder" command alias  
coder setup                       # configure API keys and model  
coder chat                        # start chatting
```

That's it. `coder` is now its own Hermes profile with its own config, memory, and state.

## Creating a profile[​](index.md#creating-a-profile "Direct link to Creating a profile")

### Blank profile[​](index.md#blank-profile "Direct link to Blank profile")

```
hermes profile create mybot
```

Creates a fresh profile with bundled skills seeded. Run `mybot setup` to configure API keys, model, and gateway tokens.

### Clone config only (`--clone`)[​](index.md#clone-config-only---clone "Direct link to clone-config-only---clone")

```
hermes profile create work --clone
```

Copies your current profile's `config.yaml`, `.env`, and `SOUL.md` into the new profile. Same API keys and model, but fresh sessions and memory. Edit `~/.hermes/profiles/work/.env` for different API keys, or `~/.hermes/profiles/work/SOUL.md` for a different personality.

### Clone everything (`--clone-all`)[​](index.md#clone-everything---clone-all "Direct link to clone-everything---clone-all")

```
hermes profile create backup --clone-all
```

Copies **everything** — config, API keys, personality, all memories, full session history, skills, cron jobs, plugins. A complete snapshot. Useful for backups or forking an agent that already has context.

### Clone from a specific profile[​](index.md#clone-from-a-specific-profile "Direct link to Clone from a specific profile")

```
hermes profile create work --clone --clone-from coder
```

Honcho memory + profiles

When Honcho is enabled, `--clone` automatically creates a dedicated AI peer for the new profile while sharing the same user workspace. Each profile builds its own observations and identity. See [Honcho -- Multi-agent / Profiles](../features/memory-providers/index.md#honcho) for details.

## Using profiles[​](index.md#using-profiles "Direct link to Using profiles")

### Command aliases[​](index.md#command-aliases "Direct link to Command aliases")

Every profile automatically gets a command alias at `~/.local/bin/<name>`:

```
coder chat                    # chat with the coder agent  
coder setup                   # configure coder's settings  
coder gateway start           # start coder's gateway  
coder doctor                  # check coder's health  
coder skills list             # list coder's skills  
coder config set model.default anthropic/claude-sonnet-4
```

The alias works with every hermes subcommand — it's just `hermes -p <name>` under the hood.

### The `-p` flag[​](index.md#the--p-flag "Direct link to the--p-flag")

You can also target a profile explicitly with any command:

```
hermes -p coder chat  
hermes --profile=coder doctor  
hermes chat -p coder -q "hello"    # works in any position
```

### Sticky default (`hermes profile use`)[​](index.md#sticky-default-hermes-profile-use "Direct link to sticky-default-hermes-profile-use")

```
hermes profile use coder  
hermes chat                   # now targets coder  
hermes tools                  # configures coder's tools  
hermes profile use default    # switch back
```

Sets a default so plain `hermes` commands target that profile. Like `kubectl config use-context`.

### Knowing where you are[​](index.md#knowing-where-you-are "Direct link to Knowing where you are")

The CLI always shows which profile is active:

- **Prompt**: `coder ❯` instead of `❯`
- **Banner**: Shows `Profile: coder` on startup
- **`hermes profile`**: Shows current profile name, path, model, gateway status

## Profiles vs workspaces vs sandboxing[​](index.md#profiles-vs-workspaces-vs-sandboxing "Direct link to Profiles vs workspaces vs sandboxing")

Profiles are often confused with workspaces or sandboxes, but they are different things:

- A **profile** gives Hermes its own state directory: `config.yaml`, `.env`, `SOUL.md`, sessions, memory, logs, cron jobs, and gateway state.
- A **workspace** or **working directory** is where terminal commands start. That is controlled separately by `terminal.cwd`.
- A **sandbox** is what limits filesystem access. Profiles do **not** sandbox the agent.

On the default `local` terminal backend, the agent still has the same filesystem access as your user account. A profile does not stop it from accessing folders outside the profile directory.

If you want a profile to start in a specific project folder, set an explicit absolute `terminal.cwd` in that profile's `config.yaml`:

```
terminal:  
  backend: local  
  cwd: /absolute/path/to/project
```

Using `cwd: "."` on the local backend means "the directory Hermes was launched from", not "the profile directory".

Also note:

- `SOUL.md` can guide the model, but it does not enforce a workspace boundary.
- Changes to `SOUL.md` take effect cleanly on a new session. Existing sessions may still be using the old prompt state.
- Asking the model "what directory are you in?" is not a reliable isolation test. If you need a predictable starting directory for tools, set `terminal.cwd` explicitly.

## Running gateways[​](index.md#running-gateways "Direct link to Running gateways")

Each profile runs its own gateway as a separate process with its own bot token:

```
coder gateway start           # starts coder's gateway  
assistant gateway start       # starts assistant's gateway (separate process)
```

### Different bot tokens[​](index.md#different-bot-tokens "Direct link to Different bot tokens")

Each profile has its own `.env` file. Configure a different Telegram/Discord/Slack bot token in each:

```
# Edit coder's tokens  
nano ~/.hermes/profiles/coder/.env  
  
# Edit assistant's tokens  
nano ~/.hermes/profiles/assistant/.env
```

### Safety: token locks[​](index.md#safety-token-locks "Direct link to Safety: token locks")

If two profiles accidentally use the same bot token, the second gateway will be blocked with a clear error naming the conflicting profile. Supported for Telegram, Discord, Slack, WhatsApp, and Signal.

### Persistent services[​](index.md#persistent-services "Direct link to Persistent services")

```
coder gateway install         # creates hermes-gateway-coder systemd/launchd service  
assistant gateway install     # creates hermes-gateway-assistant service
```

Each profile gets its own service name. They run independently.

## Configuring profiles[​](index.md#configuring-profiles "Direct link to Configuring profiles")

Each profile has its own:

- **`config.yaml`** — model, provider, toolsets, all settings
- **`.env`** — API keys, bot tokens
- **`SOUL.md`** — personality and instructions

```
coder config set model.default anthropic/claude-sonnet-4  
echo "You are a focused coding assistant." > ~/.hermes/profiles/coder/SOUL.md
```

If you want this profile to work in a specific project by default, also set its own `terminal.cwd`:

```
coder config set terminal.cwd /absolute/path/to/project
```

## Updating[​](index.md#updating "Direct link to Updating")

`hermes update` pulls code once (shared) and syncs new bundled skills to **all** profiles automatically:

```
hermes update  
# → Code updated (12 commits)  
# → Skills synced: default (up to date), coder (+2 new), assistant (+2 new)
```

User-modified skills are never overwritten.

## Managing profiles[​](index.md#managing-profiles "Direct link to Managing profiles")

```
hermes profile list           # show all profiles with status  
hermes profile show coder     # detailed info for one profile  
hermes profile rename coder dev-bot   # rename (updates alias + service)  
hermes profile export coder   # export to coder.tar.gz  
hermes profile import coder.tar.gz   # import from archive
```

## Deleting a profile[​](index.md#deleting-a-profile "Direct link to Deleting a profile")

```
hermes profile delete coder
```

This stops the gateway, removes the systemd/launchd service, removes the command alias, and deletes all profile data. You'll be asked to type the profile name to confirm.

Use `--yes` to skip confirmation: `hermes profile delete coder --yes`

note

You cannot delete the default profile (`~/.hermes`). To remove everything, use `hermes uninstall`.

## Tab completion[​](index.md#tab-completion "Direct link to Tab completion")

```
# Bash  
eval "$(hermes completion bash)"  
  
# Zsh  
eval "$(hermes completion zsh)"
```

Add the line to your `~/.bashrc` or `~/.zshrc` for persistent completion. Completes profile names after `-p`, profile subcommands, and top-level commands.

## How it works[​](index.md#how-it-works "Direct link to How it works")

Profiles use the `HERMES_HOME` environment variable. When you run `coder chat`, the wrapper script sets `HERMES_HOME=~/.hermes/profiles/coder` before launching hermes. Since 119+ files in the codebase resolve paths via `get_hermes_home()`, Hermes state automatically scopes to the profile's directory — config, sessions, memory, skills, state database, gateway PID, logs, and cron jobs.

This is separate from terminal working directory. Tool execution starts from `terminal.cwd` (or the launch directory when `cwd: "."` on the local backend), not automatically from `HERMES_HOME`.

The default profile is simply `~/.hermes` itself. No migration needed — existing installs work identically.

## Sharing profiles as distributions[​](index.md#sharing-profiles-as-distributions "Direct link to Sharing profiles as distributions")

A profile you built on one machine can be packaged as a **git repository** and installed with one command on another machine — your own workstation, a teammate's laptop, or a community user's environment. The shared package includes the SOUL, config, skills, cron jobs, and MCP connections. Credentials, memories, and sessions stay per-machine.

```
# Install a whole agent from a git repo  
hermes profile install github.com/you/research-bot --alias  
  
# Update later when the author ships a new version (keeps your memories + .env)  
hermes profile update research-bot
```

See **[Profile Distributions: Share a Whole Agent](../profile-distributions/index.md)** for the full guide — authoring, publishing, update semantics, security model, and use cases.

- [What are profiles?](index.md#what-are-profiles)
- [Quick start](index.md#quick-start)
- [Creating a profile](index.md#creating-a-profile)
  - [Blank profile](index.md#blank-profile)
  - [Clone config only (`--clone`)](index.md#clone-config-only---clone)
  - [Clone everything (`--clone-all`)](index.md#clone-everything---clone-all)
  - [Clone from a specific profile](index.md#clone-from-a-specific-profile)
- [Using profiles](index.md#using-profiles)
  - [Command aliases](index.md#command-aliases)
  - [The `-p` flag](index.md#the--p-flag)
  - [Sticky default (`hermes profile use`)](index.md#sticky-default-hermes-profile-use)
  - [Knowing where you are](index.md#knowing-where-you-are)
- [Profiles vs workspaces vs sandboxing](index.md#profiles-vs-workspaces-vs-sandboxing)
- [Running gateways](index.md#running-gateways)
  - [Different bot tokens](index.md#different-bot-tokens)
  - [Safety: token locks](index.md#safety-token-locks)
  - [Persistent services](index.md#persistent-services)
- [Configuring profiles](index.md#configuring-profiles)
- [Updating](index.md#updating)
- [Managing profiles](index.md#managing-profiles)
- [Deleting a profile](index.md#deleting-a-profile)
- [Tab completion](index.md#tab-completion)
- [How it works](index.md#how-it-works)
- [Sharing profiles as distributions](index.md#sharing-profiles-as-distributions)
