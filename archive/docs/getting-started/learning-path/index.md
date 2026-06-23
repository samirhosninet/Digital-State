---
source_url: https://hermes-agent.nousresearch.com/docs/getting-started/learning-path
title: Learning Path | Hermes Agent
archived_at: 2026-05-13T02:40:25Z
---

Hermes Agent can do a lot — CLI assistant, Telegram/Discord bot, task automation, RL training, and more. This page helps you figure out where to start and what to read based on your experience level and what you're trying to accomplish.

Start Here

If you haven't installed Hermes Agent yet, begin with the [Installation guide](../installation/index.md) and then run through the [Quickstart](../quickstart/index.md). Everything below assumes you have a working installation.

## How to Use This Page[​](index.md#how-to-use-this-page "Direct link to How to Use This Page")

- **Know your level?** Jump to the [experience-level table](index.md#by-experience-level) and follow the reading order for your tier.
- **Have a specific goal?** Skip to [By Use Case](index.md#by-use-case) and find the scenario that matches.
- **Just browsing?** Check the [Key Features](index.md#key-features-at-a-glance) table for a quick overview of everything Hermes Agent can do.

## By Experience Level[​](index.md#by-experience-level "Direct link to By Experience Level")

| Level | Goal | Recommended Reading | Time Estimate |
| --- | --- | --- | --- |
| **Beginner** | Get up and running, have basic conversations, use built-in tools | [Installation](../installation/index.md) → [Quickstart](../quickstart/index.md) → [CLI Usage](../../user-guide/cli/index.md) → [Configuration](../../user-guide/configuration/index.md) | ~1 hour |
| **Intermediate** | Set up messaging bots, use advanced features like memory, cron jobs, and skills | [Sessions](../../user-guide/sessions/index.md) → [Messaging](../../user-guide/messaging/index.md) → [Tools](../../user-guide/features/tools/index.md) → [Skills](../../user-guide/features/skills/index.md) → [Memory](../../user-guide/features/memory/index.md) → [Cron](../../user-guide/features/cron/index.md) | ~2–3 hours |
| **Advanced** | Build custom tools, create skills, train models with RL, contribute to the project | [Architecture](../../developer-guide/architecture/index.md) → [Adding Tools](../../developer-guide/adding-tools/index.md) → [Creating Skills](../../developer-guide/creating-skills/index.md) → [RL Training](../../user-guide/features/rl-training/index.md) → [Contributing](../../developer-guide/contributing/index.md) | ~4–6 hours |

## By Use Case[​](index.md#by-use-case "Direct link to By Use Case")

Pick the scenario that matches what you want to do. Each one links you to the relevant docs in the order you should read them.

### "I want a CLI coding assistant"[​](index.md#i-want-a-cli-coding-assistant "Direct link to \"I want a CLI coding assistant\"")

Use Hermes Agent as an interactive terminal assistant for writing, reviewing, and running code.

1. [Installation](../installation/index.md)
2. [Quickstart](../quickstart/index.md)
3. [CLI Usage](../../user-guide/cli/index.md)
4. [Code Execution](../../user-guide/features/code-execution/index.md)
5. [Context Files](../../user-guide/features/context-files/index.md)
6. [Tips & Tricks](../../guides/tips/index.md)

tip

Pass files directly into your conversation with context files. Hermes Agent can read, edit, and run code in your projects.

### "I want a Telegram/Discord bot"[​](index.md#i-want-a-telegramdiscord-bot "Direct link to \"I want a Telegram/Discord bot\"")

Deploy Hermes Agent as a bot on your favorite messaging platform.

1. [Installation](../installation/index.md)
2. [Configuration](../../user-guide/configuration/index.md)
3. [Messaging Overview](../../user-guide/messaging/index.md)
4. [Telegram Setup](../../user-guide/messaging/telegram/index.md)
5. [Discord Setup](../../user-guide/messaging/discord/index.md)
6. [Voice Mode](../../user-guide/features/voice-mode/index.md)
7. [Use Voice Mode with Hermes](../../guides/use-voice-mode-with-hermes/index.md)
8. [Security](../../user-guide/security/index.md)

For full project examples, see:

- [Daily Briefing Bot](../../guides/daily-briefing-bot/index.md)
- [Team Telegram Assistant](../../guides/team-telegram-assistant/index.md)

### "I want to automate tasks"[​](index.md#i-want-to-automate-tasks "Direct link to \"I want to automate tasks\"")

Schedule recurring tasks, run batch jobs, or chain agent actions together.

1. [Quickstart](../quickstart/index.md)
2. [Cron Scheduling](../../user-guide/features/cron/index.md)
3. [Batch Processing](../../user-guide/features/batch-processing/index.md)
4. [Delegation](../../user-guide/features/delegation/index.md)
5. [Hooks](../../user-guide/features/hooks/index.md)

tip

Cron jobs let Hermes Agent run tasks on a schedule — daily summaries, periodic checks, automated reports — without you being present.

### "I want to build custom tools/skills"[​](index.md#i-want-to-build-custom-toolsskills "Direct link to \"I want to build custom tools/skills\"")

Extend Hermes Agent with your own tools and reusable skill packages.

1. [Plugins](../../user-guide/features/plugins/index.md)
2. [Build a Hermes Plugin](../../guides/build-a-hermes-plugin/index.md)
3. [Tools Overview](../../user-guide/features/tools/index.md)
4. [Skills Overview](../../user-guide/features/skills/index.md)
5. [MCP (Model Context Protocol)](../../user-guide/features/mcp/index.md)
6. [Architecture](../../developer-guide/architecture/index.md)
7. [Adding Tools](../../developer-guide/adding-tools/index.md)
8. [Creating Skills](../../developer-guide/creating-skills/index.md)

tip

For most custom tool creation, start with plugins. The [Adding Tools](../../developer-guide/adding-tools/index.md)
page is for built-in Hermes core development, not the usual user/custom-tool path.

### "I want to train models"[​](index.md#i-want-to-train-models "Direct link to \"I want to train models\"")

Use reinforcement learning to fine-tune model behavior with Hermes Agent's built-in RL training pipeline.

1. [Quickstart](../quickstart/index.md)
2. [Configuration](../../user-guide/configuration/index.md)
3. [RL Training](../../user-guide/features/rl-training/index.md)
4. [Provider Routing](../../user-guide/features/provider-routing/index.md)
5. [Architecture](../../developer-guide/architecture/index.md)

tip

RL training works best when you already understand the basics of how Hermes Agent handles conversations and tool calls. Run through the Beginner path first if you're new.

### "I want to use it as a Python library"[​](index.md#i-want-to-use-it-as-a-python-library "Direct link to \"I want to use it as a Python library\"")

Integrate Hermes Agent into your own Python applications programmatically.

1. [Installation](../installation/index.md)
2. [Quickstart](../quickstart/index.md)
3. [Python Library Guide](../../guides/python-library/index.md)
4. [Architecture](../../developer-guide/architecture/index.md)
5. [Tools](../../user-guide/features/tools/index.md)
6. [Sessions](../../user-guide/sessions/index.md)

## Key Features at a Glance[​](index.md#key-features-at-a-glance "Direct link to Key Features at a Glance")

Not sure what's available? Here's a quick directory of major features:

| Feature | What It Does | Link |
| --- | --- | --- |
| **Tools** | Built-in tools the agent can call (file I/O, search, shell, etc.) | [Tools](../../user-guide/features/tools/index.md) |
| **Skills** | Installable plugin packages that add new capabilities | [Skills](../../user-guide/features/skills/index.md) |
| **Memory** | Persistent memory across sessions | [Memory](../../user-guide/features/memory/index.md) |
| **Context Files** | Feed files and directories into conversations | [Context Files](../../user-guide/features/context-files/index.md) |
| **MCP** | Connect to external tool servers via Model Context Protocol | [MCP](../../user-guide/features/mcp/index.md) |
| **Cron** | Schedule recurring agent tasks | [Cron](../../user-guide/features/cron/index.md) |
| **Delegation** | Spawn sub-agents for parallel work | [Delegation](../../user-guide/features/delegation/index.md) |
| **Code Execution** | Run Python scripts that call Hermes tools programmatically | [Code Execution](../../user-guide/features/code-execution/index.md) |
| **Browser** | Web browsing and scraping | [Browser](../../user-guide/features/browser/index.md) |
| **Hooks** | Event-driven callbacks and middleware | [Hooks](../../user-guide/features/hooks/index.md) |
| **Batch Processing** | Process multiple inputs in bulk | [Batch Processing](../../user-guide/features/batch-processing/index.md) |
| **RL Training** | Fine-tune models with reinforcement learning | [RL Training](../../user-guide/features/rl-training/index.md) |
| **Provider Routing** | Route requests across multiple LLM providers | [Provider Routing](../../user-guide/features/provider-routing/index.md) |

## What to Read Next[​](index.md#what-to-read-next "Direct link to What to Read Next")

Based on where you are right now:

- **Just finished installing?** → Head to the [Quickstart](../quickstart/index.md) to run your first conversation.
- **Completed the Quickstart?** → Read [CLI Usage](../../user-guide/cli/index.md) and [Configuration](../../user-guide/configuration/index.md) to customize your setup.
- **Comfortable with the basics?** → Explore [Tools](../../user-guide/features/tools/index.md), [Skills](../../user-guide/features/skills/index.md), and [Memory](../../user-guide/features/memory/index.md) to unlock the full power of the agent.
- **Setting up for a team?** → Read [Security](../../user-guide/security/index.md) and [Sessions](../../user-guide/sessions/index.md) to understand access control and conversation management.
- **Ready to build?** → Jump into the [Developer Guide](../../developer-guide/architecture/index.md) to understand the internals and start contributing.
- **Want practical examples?** → Check out the [Guides](../../guides/tips/index.md) section for real-world projects and tips.

tip

You don't need to read everything. Pick the path that matches your goal, follow the links in order, and you'll be productive quickly. You can always come back to this page to find your next step.

- [How to Use This Page](index.md#how-to-use-this-page)
- [By Experience Level](index.md#by-experience-level)
- [By Use Case](index.md#by-use-case)
  - ["I want a CLI coding assistant"](index.md#i-want-a-cli-coding-assistant)
  - ["I want a Telegram/Discord bot"](index.md#i-want-a-telegramdiscord-bot)
  - ["I want to automate tasks"](index.md#i-want-to-automate-tasks)
  - ["I want to build custom tools/skills"](index.md#i-want-to-build-custom-toolsskills)
  - ["I want to train models"](index.md#i-want-to-train-models)
  - ["I want to use it as a Python library"](index.md#i-want-to-use-it-as-a-python-library)
- [Key Features at a Glance](index.md#key-features-at-a-glance)
- [What to Read Next](index.md#what-to-read-next)
