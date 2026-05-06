# 🚀 Agent Context Manager

<p align="center">
  <strong>面向 Agent Session 的异步跨 Harness 上下文管理技能。</strong>
</p>

<p align="center">
  • 全局召回 • 本地压缩 • 可审阅 Context Jobs •
</p>

<p align="center">
  <a href="README.md">English</a> •
  <a href="#-功能">功能</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-命令">命令</a> •
  <a href="#-安全模型">安全模型</a> •
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
> **全局召回，局部压缩，人工确认。**
>
> Agent session 不只是需要更大的上下文窗口。更重要的是：能安全地把旧 context 找回来，把当前 context 压轻，并明确决定哪些内容真正进入当前对话。
>
> Agent Context Manager（`ctx`）把 context 操作变成可审阅的后台 job：先 recall 或 compact，再检查候选结果，最后 apply 或 discard。

## 🧭 快速导航

> [!TIP]
> **我是人类用户** -> 继续阅读本 README，了解安装、命令、限制和项目定位。
>
> **我是 agent** -> 读取 [`skills/`](skills) 下的 slash-command skills，以及 [docs/design.md](docs/design.md)。

Agent Context Manager 是一组 slash-command skills 和 Python workers，用来在本地 agent session 中做异步 context 管理。它的命令 namespace 是 `ctx`。

- **面向 Claude Code 和 CodeBuddy**：安装 `/ctx-recall`、`/ctx-compact`、`/ctx-jobs` 三个 skills。
- **面向 Codex 和其他 harness**：可以直接通过 Python CLI 使用 backend。
- **跨 harness 召回**：在一个 session 中检索本地 Claude Code、CodeBuddy、Codex 历史对话日志。
- **上下文安全**：候选 context 不会自动注入当前对话，而是先进入 job 队列。

**状态：** `0.1-alpha`

> 本项目与 Anthropic、OpenAI、CodeBuddy、Codex、VCC 均无官方从属关系。请只在你有权限访问的本地日志和 session 上使用。

## ⚡ 快速开始

```bash
git clone https://github.com/OpenClaudex/agent-context-manager.git
cd agent-context-manager
```

### Claude Code

```bash
./scripts/install-claude.sh
```

重启 Claude Code 后使用：

```text
/ctx-recall "why did we choose BM25 instead of embeddings"
/ctx-compact preserve architecture decisions and TODOs
/ctx-jobs
```

### CodeBuddy

```bash
./scripts/install-codebuddy.sh
```

重启 CodeBuddy 后使用同样的 `/ctx-*` 命令。

### Codex / 通用 CLI

```bash
PYTHONPATH=src python3 -m context_os.ctx.workers.recall "VCC architecture" --scope all --budget 8000 --max-hits 5
PYTHONPATH=src python3 -m context_os.ctx.runner list
```

## ✨ 功能

Agent Context Manager 聚焦于可审阅的 context 操作：

- recall 和 compact 都作为后台 job 运行，前台对话可以继续。
- 跨本地 Claude Code、CodeBuddy、Codex JSONL 日志召回历史 context。
- 把当前 session 压缩成结构化候选摘要。
- 使用简单的本地文件型 job 队列存储结果。
- 通过 `apply` / `discard` 把候选生成和正式采用分离。
- 使用 VCC 风格 conversation compilation 做 transcript 搜索和 context view。
- 支持通过 `claude -p` 或 `codebuddy -p` 做后台总结。

## 🧩 命令

| 命令 | 范围 | 预期行为 |
|---|---|---|
| `/ctx-recall <query>` | 全局、跨 harness | 搜索本地历史日志，生成候选 context block。 |
| `/ctx-compact [instruction]` | 当前 session | 为当前活跃 session 生成候选 compact 摘要。 |
| `/ctx-jobs` | 本地 job store | 列出 job、预览结果、apply 完成结果或 discard 噪声。 |

### 本地召回来源

`/ctx-recall` 可以搜索：

```text
~/.codebuddy/projects
~/.claude/projects
~/.claude-internal/projects
~/.codex/sessions
~/.codex-internal/sessions
```

支持的召回 scope：

```text
--scope all | codebuddy | claude | codex
```

## 🛡️ 安全模型

Agent Context Manager 把 context 注入视为高风险操作。

- **先审阅，再 apply。** Recall 和 compact 结果都是候选内容，不会自动修改 prompt。
- **没有隐藏云端存储。** Jobs 是 `.ctx/jobs/` 下的本地 JSON 文件。
- **不持久化凭据。** 不要把 secret、token、私密截图、凭据写入示例或 job 结果。
- **compact 只针对当前 session。** `/ctx-compact` 不会默认压缩全部用户历史。
- **recall 是 best-effort。** `/ctx-recall` 可能搜不到，也可能搜到元记录；需要人工检查后再 apply。
- **显式依赖 VCC。** 当前版本用 VCC 作为 compilation/search backend。

## 🧪 为什么做这个

大多数 agent harness 已经保存了很丰富的 trace：用户消息、assistant 摘要、工具调用、终端输出、文件路径。问题不总是 agent 没有记忆，而是有用 context 在当前工作窗口之外。

Agent Context Manager 不是 memory palace。它是一个轻量 context 操作闭环：

```text
召回旧 context -> 压缩当前 context -> 审阅结果 -> 明确 apply
```

## 📚 文档

- [Design Notes](docs/design.md)
- [Agent Context Manager and VCC](docs/vcc-comparison.md)
- [Claude Code installer](scripts/install-claude.sh)
- [CodeBuddy installer](scripts/install-codebuddy.sh)
- Skills: [`ctx-recall`](skills/ctx-recall/SKILL.md), [`ctx-compact`](skills/ctx-compact/SKILL.md), [`ctx-jobs`](skills/ctx-jobs/SKILL.md)

## 🗺️ 路线图

- **v0.1**：异步 recall、异步 compact、jobs list/show/apply/discard。
- **v0.2**：更干净的 CodeBuddy/Codex 打包和安装流程。
- **v0.3**：source policy、隐私过滤、更强 stale detection。
- **v0.4**：支持 VCC 之外的可插拔 recall backend。

## 🌐 相关项目

Agent Context Manager 聚焦 agent session 的 context-management skills。相关项目：

- [VCC](https://github.com/lllyasviel/VCC) - 面向 agent trace analysis 和 conversation recovery 的 View-oriented Conversation Compiler。
- [OpenReview Agent](https://github.com/OpenClaudex/openreview-agent) - OpenClaudex 的安全 OpenReview 投稿 workflow skill / CLI。
- [Open Claudex Computer Use](https://github.com/OpenClaudex/open-claudex-computer-use) - 面向 Claude Code、Codex 和 MCP agents 的 macOS background computer use。

## 📄 License

[MIT](LICENSE)
