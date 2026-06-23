---
source_url: https://hermes-agent.nousresearch.com/docs/getting-started/updating
title: Updating & Uninstalling | Hermes Agent
archived_at: 2026-05-13T02:40:25Z
---

## Updating[​](index.md#updating "Direct link to Updating")

Update to the latest version with a single command:

```
hermes update
```

This pulls the latest code, updates dependencies, and prompts you to configure any new options that were added since your last update.

tip

`hermes update` automatically detects new configuration options and prompts you to add them. If you skipped that prompt, you can manually run `hermes config check` to see missing options, then `hermes config migrate` to interactively add them.

### What happens during an update[​](index.md#what-happens-during-an-update "Direct link to What happens during an update")

When you run `hermes update`, the following steps occur:

1. **Pairing-data snapshot** — a lightweight pre-update state snapshot is saved (covers `~/.hermes/pairing/`, Feishu comment rules, and other state files that get modified at runtime). Recoverable via the snapshot restore flow described under [Snapshots and rollback](../../user-guide/checkpoints-and-rollback/index.md), or by extracting the most recent quick-snapshot zip Hermes wrote next to your `~/.hermes/` directory.
2. **Git pull** — pulls the latest code from the `main` branch and updates submodules
3. **Dependency install** — runs `uv pip install -e ".[all]"` to pick up new or changed dependencies
4. **Config migration** — detects new config options added since your version and prompts you to set them
5. **Gateway auto-restart** — running gateways are refreshed after the update completes so the new code takes effect immediately. Service-managed gateways (systemd on Linux, launchd on macOS) are restarted through the service manager. Manual gateways are relaunched automatically when Hermes can map the running PID back to a profile.

### Preview-only: `hermes update --check`[​](index.md#preview-only-hermes-update---check "Direct link to preview-only-hermes-update---check")

Want to know if you're behind `origin/main` before actually pulling? Run `hermes update --check` — it fetches, prints your local commit and the latest remote commit side-by-side, and exits `0` if in sync or `1` if behind. No files are modified, no gateway is restarted. Useful in scripts and cron jobs that gate on "is there an update".

### Full pre-update backup: `--backup`[​](index.md#full-pre-update-backup---backup "Direct link to full-pre-update-backup---backup")

For high-value profiles (production gateways, shared team installs) you can opt into a full pre-pull backup of `HERMES_HOME` (config, auth, sessions, skills, pairing):

```
hermes update --backup
```

Or make it the default for every run:

```
# ~/.hermes/config.yaml  
updates:  
  pre_update_backup: true
```

`--backup` was the always-on behavior in earlier builds, but it was adding minutes to every update on large homes, so it's now opt-in. The lightweight pairing-data snapshot above still runs unconditionally.

Expected output looks like:

```
$ hermes update  
Updating Hermes Agent...  
📥 Pulling latest code...  
Already up to date.  (or: Updating abc1234..def5678)  
📦 Updating dependencies...  
✅ Dependencies updated  
🔍 Checking for new config options...  
✅ Config is up to date  (or: Found 2 new options — running migration...)  
🔄 Restarting gateways...  
✅ Gateway restarted  
✅ Hermes Agent updated successfully!
```

### Recommended Post-Update Validation[​](index.md#recommended-post-update-validation "Direct link to Recommended Post-Update Validation")

`hermes update` handles the main update path, but a quick validation confirms everything landed cleanly:

1. `git status --short` — if the tree is unexpectedly dirty, inspect before continuing
2. `hermes doctor` — checks config, dependencies, and service health
3. `hermes --version` — confirm the version bumped as expected
4. If you use the gateway: `hermes gateway status`
5. If `doctor` reports npm audit issues: run `npm audit fix` in the flagged directory

Dirty working tree after update

If `git status --short` shows unexpected changes after `hermes update`, stop and inspect them before continuing. This usually means local modifications were reapplied on top of the updated code, or a dependency step refreshed lockfiles.

### If your terminal disconnects mid-update[​](index.md#if-your-terminal-disconnects-mid-update "Direct link to If your terminal disconnects mid-update")

`hermes update` protects itself against accidental terminal loss:

- The update ignores `SIGHUP`, so closing your SSH session or terminal window no longer kills it mid-install. `pip` and `git` child processes inherit this protection, so the Python environment cannot be left half-installed by a dropped connection.
- All output is mirrored to `~/.hermes/logs/update.log` while the update runs. If your terminal disappears, reconnect and inspect the log to see whether the update finished and whether the gateway restart succeeded:

```
tail -f ~/.hermes/logs/update.log
```

- `Ctrl-C` (SIGINT) and system shutdown (SIGTERM) are still honored — those are deliberate cancellations, not accidents.

You no longer need to wrap `hermes update` in `screen` or `tmux` to survive a terminal drop.

### Checking your current version[​](index.md#checking-your-current-version "Direct link to Checking your current version")

```
hermes version
```

Compare against the latest release at the [GitHub releases page](https://github.com/NousResearch/hermes-agent/releases).

### Updating from Messaging Platforms[​](index.md#updating-from-messaging-platforms "Direct link to Updating from Messaging Platforms")

You can also update directly from Telegram, Discord, Slack, WhatsApp, or Teams by sending:

```
/update
```

This pulls the latest code, updates dependencies, and restarts running gateways. The bot will briefly go offline during the restart (typically 5–15 seconds) and then resume.

### Manual Update[​](index.md#manual-update "Direct link to Manual Update")

If you installed manually (not via the quick installer):

```
cd /path/to/hermes-agent  
export VIRTUAL_ENV="$(pwd)/venv"  
  
# Pull latest code and submodules  
git pull origin main  
git submodule update --init --recursive  
  
# Reinstall (picks up new dependencies)  
uv pip install -e ".[all]"  
uv pip install -e "./tinker-atropos"  
  
# Check for new config options  
hermes config check  
hermes config migrate   # Interactively add any missing options
```

### Rollback instructions[​](index.md#rollback-instructions "Direct link to Rollback instructions")

If an update introduces a problem, you can roll back to a previous version:

```
cd /path/to/hermes-agent  
  
# List recent versions  
git log --oneline -10  
  
# Roll back to a specific commit  
git checkout <commit-hash>  
git submodule update --init --recursive  
uv pip install -e ".[all]"  
  
# Restart the gateway if running  
hermes gateway restart
```

To roll back to a specific release tag:

```
git checkout v0.6.0  
git submodule update --init --recursive  
uv pip install -e ".[all]"
```

warning

Rolling back may cause config incompatibilities if new options were added. Run `hermes config check` after rolling back and remove any unrecognized options from `config.yaml` if you encounter errors.

### Note for Nix users[​](index.md#note-for-nix-users "Direct link to Note for Nix users")

If you installed via Nix flake, updates are managed through the Nix package manager:

```
# Update the flake input  
nix flake update hermes-agent  
  
# Or rebuild with the latest  
nix profile upgrade hermes-agent
```

Nix installations are immutable — rollback is handled by Nix's generation system:

```
nix profile rollback
```

See [Nix Setup](../nix-setup/index.md) for more details.

---

## Uninstalling[​](index.md#uninstalling "Direct link to Uninstalling")

```
hermes uninstall
```

The uninstaller gives you the option to keep your configuration files (`~/.hermes/`) for a future reinstall.

### Manual Uninstall[​](index.md#manual-uninstall "Direct link to Manual Uninstall")

```
rm -f ~/.local/bin/hermes  
rm -rf /path/to/hermes-agent  
rm -rf ~/.hermes            # Optional — keep if you plan to reinstall
```

info

If you installed the gateway as a system service, stop and disable it first:

```
hermes gateway stop  
# Linux: systemctl --user disable hermes-gateway  
# macOS: launchctl remove ai.hermes.gateway
```

- [Updating](index.md#updating)
  - [What happens during an update](index.md#what-happens-during-an-update)
  - [Preview-only: `hermes update --check`](index.md#preview-only-hermes-update---check)
  - [Full pre-update backup: `--backup`](index.md#full-pre-update-backup---backup)
  - [Recommended Post-Update Validation](index.md#recommended-post-update-validation)
  - [If your terminal disconnects mid-update](index.md#if-your-terminal-disconnects-mid-update)
  - [Checking your current version](index.md#checking-your-current-version)
  - [Updating from Messaging Platforms](index.md#updating-from-messaging-platforms)
  - [Manual Update](index.md#manual-update)
  - [Rollback instructions](index.md#rollback-instructions)
  - [Note for Nix users](index.md#note-for-nix-users)
- [Uninstalling](index.md#uninstalling)
  - [Manual Uninstall](index.md#manual-uninstall)
