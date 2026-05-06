# 🚀 Agent Context Manager

<p align="center">
  <img src="docs/assets/cover.png" alt="Agent Context Manager cover" width="960">
</p>

<p align="center">
  <strong>Async cross-harness context management for agent sessions.</strong>
</p>

<p align="center">
  • Global Recall • Local Compact • Reviewable Context Jobs •
</p>

<p align="center">
  <a href="README.zh-CN.md">中文文档</a> •
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-commands">Commands</a> •
  <a href="#-safety-model">Safety Model</a> •
  <a href="docs/design.md">Design</a>
</p>

<p align="center">
  <a href="https://github.com/OpenClaudex/agent-context-manager/releases"><img alt="Release" src="https://img.shields.io/github/v/release/OpenClaudex/agent-context-manager?include_prereleases&label=release"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-green"></a>
  <img alt="Status" src="https://img.shields.io/badge/status-0.1--alpha-orange">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-skill--ready-6b46c1">
  <img alt="CodeBuddy" src="https://img.shields.io/badge/CodeBuddy-skill--ready-111827">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-CLI--ready-111827">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-blue">
</p>

> [!IMPORTANT]
> **From harness-local memory to agent-native context recovery.**
>
> I noticed the problem around the Nth time I had to re-explain project context.
>
> My machine has more than a dozen coding-agent entry points: Claude Code, Codex, CodeBuddy, Cursor, Trae, Code Desk, and a few internal company builds. They are all powerful, and many of them have their own memory systems. But every time I switch to a new harness, the same thing happens: I already discussed the task, explained the constraints, ruled out bad approaches, and hit the bugs somewhere else, yet the new window starts as if it knows nothing.
>
> **The problem is not just memory. It is cross-harness context recovery.**
>
> Harness-local memory is useful, but it does not answer the question: where did I already talk about this? Real agent work no longer lives in one agent, one window, or one project path. The context exists in local traces, but it is hard to recover when the next session starts.
>
> **So I built Agent Context Manager.**
>
> The premise is simple: if these conversations and tool traces are already stored locally, why can't an agent search them? `ctx` lets agents recall relevant fragments from past harness traces, compact them into a candidate context block, and let you review, apply, or discard the result.

## 🧭 Quick Navigation

> [!TIP]
> **I'm a human** -> Continue reading this README for setup, commands, limits, and project context.
>
> **I'm an agent** -> Read the slash-command skills in [`skills/`](skills) and the design notes in [docs/design.md](docs/design.md).

Agent Context Manager is a small set of slash-command skills and Python workers for asynchronous context management in local agent sessions. Its command namespace is `ctx`.

- **For Claude Code and CodeBuddy**: install `/ctx-recall`, `/ctx-compact`, and `/ctx-jobs` as skills.
- **For Codex and other harnesses**: run the backend directly through the Python CLI.
- **For cross-harness recall**: search local Claude Code, CodeBuddy, and Codex conversation logs from one session.
- **For context safety**: candidate context is not applied automatically; it goes through a job queue.

**Status:** `0.1-alpha`

> Not affiliated with Anthropic, OpenAI, CodeBuddy, Codex, or VCC. Use only on local logs and sessions you are authorized to access.

## ⚡ Quick Start

Tell your coding agent:

> Install Agent Context Manager from https://github.com/OpenClaudex/agent-context-manager and set it up for cross-harness recall, async compact jobs, and reviewable context application in my local coding-agent workflow.

Low-level command details live in the slash-command skills under [`skills/`](skills). If your agent needs a manual fallback, use the commands below.

Clone once:

```bash
git clone https://github.com/OpenClaudex/agent-context-manager.git
cd agent-context-manager
```

### Claude Code

```bash
./scripts/install-claude.sh
```

Restart Claude Code, then use:

```text
/ctx-recall "why did we choose BM25 instead of embeddings"
/ctx-compact preserve architecture decisions and TODOs
/ctx-jobs
```

### CodeBuddy

```bash
./scripts/install-codebuddy.sh
```

Restart CodeBuddy before using the same `/ctx-*` commands.

### Codex / Generic CLI

```bash
PYTHONPATH=src python3 -m context_os.ctx.workers.recall "VCC architecture" --scope all --budget 8000 --max-hits 5
PYTHONPATH=src python3 -m context_os.ctx.runner list
```

## ✨ Features

Agent Context Manager focuses on reviewable context operations:

- Runs recall and compact as background jobs, so the foreground conversation can continue.
- Recalls historical context across local Claude Code, CodeBuddy, and Codex JSONL logs.
- Compacts the current session into a structured candidate summary.
- Stores results in a simple local file-based job queue.
- Separates candidate generation from application through `apply` / `discard`.
- Uses VCC-style conversation compilation for transcript search and context views.
- Supports `claude -p` or `codebuddy -p` for background summarization.

## 🧩 Commands

| Command | Scope | Expected Behavior |
|---|---|---|
| `/ctx-recall <query>` | Global, cross-harness | Search historical local logs and produce a candidate context block. |
| `/ctx-compact [instruction]` | Current session | Produce a candidate compact summary of the active session. |
| `/ctx-jobs` | Local job store | List jobs, preview results, apply completed results, or discard noise. |

### Local Recall Sources

`/ctx-recall` is meant to search any local coding-agent conversation trace you are authorized to inspect. The built-in source discovery currently covers common local paths such as:

```text
~/.codebuddy/projects
~/.claude/projects
~/.claude-internal/projects
~/.codex/sessions
~/.codex-internal/sessions
```

Supported built-in recall scopes:

```text
--scope all | codebuddy | claude | codex
```

If your agent does not find another harness, tell it what to add:

> Add recall support for Cursor conversations stored under `~/Library/Application Support/Cursor/User/globalStorage/...`, then make `/ctx-recall` include that source in cross-harness search.

The intended workflow is agent-native: name the missing coding agent or give the local trace path, and let your coding agent wire it into the recall source discovery.

## 🛡️ Safety Model

Agent Context Manager treats context injection as a risky operation.

- **Review before apply.** Recall and compact results are candidates, not automatic prompt mutations.
- **No hidden cloud storage.** Jobs are local JSON files under `.ctx/jobs/`.
- **No credential persistence.** Do not put secrets, tokens, private screenshots, or credentials into examples or job results.
- **Current-session compact only.** `/ctx-compact` summarizes the active session, not the entire user history.
- **Best-effort recall.** `/ctx-recall` can miss relevant history or return meta-results; users should inspect before applying.
- **Explicit VCC dependency.** VCC is currently used as the compilation/search backend.

## 🧪 Why This Exists

Most agent harnesses already persist rich traces: user messages, assistant reasoning summaries, tool calls, terminal output, and file paths. The problem is not always that the agent has no memory. The problem is that useful context lives outside the current working window.

Agent Context Manager is not a memory palace. It is a lightweight operating loop for context:

```text
recall old context -> compact current context -> review result -> apply deliberately
```

## 📚 Docs

- [Design Notes](docs/design.md)
- [Agent Context Manager and VCC](docs/vcc-comparison.md)
- [Claude Code installer](scripts/install-claude.sh)
- [CodeBuddy installer](scripts/install-codebuddy.sh)
- Skills: [`ctx-recall`](skills/ctx-recall/SKILL.md), [`ctx-compact`](skills/ctx-compact/SKILL.md), [`ctx-jobs`](skills/ctx-jobs/SKILL.md)

## 🗺️ Roadmap

- **v0.1**: async recall, async compact, jobs list/show/apply/discard.
- **v0.2**: cleaner CodeBuddy/Codex packaging and install flow.
- **v0.3**: source policy controls, privacy filters, and stronger stale detection.
- **v0.4**: pluggable recall backends beyond VCC.

## 🙏 Acknowledgements

Agent Context Manager is especially inspired by [VCC](https://github.com/lllyasviel/VCC), the View-oriented Conversation Compiler for agent trace analysis and conversation recovery. The core idea of compiling conversation traces into searchable context views, and several retrieval-oriented ideas in this project, are influenced by VCC.

The difference is that `ctx` is designed to sit above any single agent harness: it searches across local Claude Code, CodeBuddy, and Codex traces, runs recall and compact as asynchronous jobs, and keeps candidate context reviewable before anything enters the active session.

Thanks also to the broader context-management, conversation-recovery, and agent-memory projects that make it clearer why agent context should be searchable, inspectable, and portable across tools.

## ⭐ Star History

<a href="https://star-history.com/#OpenClaudex/agent-context-manager&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=OpenClaudex/agent-context-manager&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=OpenClaudex/agent-context-manager&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=OpenClaudex/agent-context-manager&type=Date" />
  </picture>
</a>

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  If this project helps your agent remember the right thing at the right time, please give it a ⭐ Star!
</p>

<p align="center">
  <a href="https://github.com/OpenClaudex/agent-context-manager/issues">Report Issues</a> ·
  <a href="https://github.com/OpenClaudex/agent-context-manager/issues/new?labels=enhancement">Feature Requests</a>
</p>
