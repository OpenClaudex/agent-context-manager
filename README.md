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

> Install Agent Context Manager from https://github.com/OpenClaudex/agent-context-manager. Scan my home directory for local coding-agent conversation traces, register the discovered Claude Code / Codex / CodeBuddy / Cursor / Windsurf / Trae / Code Desk / Roo Code / Cline / Continue / Aider / Goose / OpenHands / Devin / Copilot Workspace / internal-agent history paths as recall sources, and set up cross-harness recall, async compact jobs, and reviewable context application.

After setup, use `/ctx-recall`, `/ctx-compact`, and `/ctx-jobs` from your agent session. Low-level implementation details live in the slash-command skills under [`skills/`](skills).

## ✨ Features

Agent Context Manager focuses on one workflow:

- Search many local coding-agent histories from one session.
- Compact current-session context into a candidate summary.
- Keep recall and compact results reviewable before they enter the active prompt.
- Let a coding agent add more local trace sources when it finds a new harness.

## 🧩 Commands

| Command | Scope | Expected Behavior |
|---|---|---|
| `/ctx-recall <query>` | Global, cross-harness | Search historical local logs and produce a candidate context block. |
| `/ctx-compact [instruction]` | Current session | Produce a candidate compact summary of the active session. |
| `/ctx-jobs` | Local job store | List jobs, preview results, apply completed results, or discard noise. |

### Local Recall Sources

`/ctx-recall` is meant to search any local coding-agent conversation trace you are authorized to inspect. This includes built-in support and agent-added sources for tools such as:

```text
Claude Code, Codex, CodeBuddy, Cursor, Windsurf, Trae, Code Desk,
Roo Code, Cline, Continue, Aider, Goose, OpenHands, Devin,
Copilot Workspace, internal company builds, and other local harnesses.
```

If your agent does not find another harness, tell it what to add:

> Add recall support for Cursor conversations stored under `~/Library/Application Support/Cursor/User/globalStorage/...`, then make `/ctx-recall` include that source in cross-harness search.

The intended workflow is agent-native: name the missing coding agent or give the local trace path, and let your coding agent wire it into source discovery.

## 🛡️ Safety Model

Context injection is high-risk, so `ctx` stays local and review-first: recall and compact results are candidates, jobs are stored under `.ctx/jobs/`, and nothing is applied to the active session until you explicitly accept it.

## 🧪 Why This Exists

Most agent harnesses already persist rich traces. `ctx` makes those traces searchable across tools, then turns the result into a reviewable context operation:

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
