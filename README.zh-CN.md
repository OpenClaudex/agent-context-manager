# 🚀 Agent Context Manager

<p align="center">
  <img src="docs/assets/cover.png" alt="Agent Context Manager cover" width="960">
</p>

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
> **从 harness-local memory，到 agent-native context recovery。**
>
> 我是在第 N 次重讲项目背景时意识到这个问题的。
>
> 我的电脑里有十几个 coding agent 入口：Claude Code、Codex、CodeBuddy、Cursor、Trae、Code Desk，还有一些公司内部版本。它们都很强，也都在做自己的 memory。但每次切到一个新的 harness，我还是会遇到同一个问题：我明明已经和另一个窗口聊过这个任务、解释过约束、排除过方案、踩过坑，可新窗口仍然像什么都不知道。
>
> **问题不只是 memory，而是跨 harness 的 context recovery。**
>
> 单个工具的记忆系统当然有用，但它解决不了“我之前在哪个 agent 里聊过这件事？”这个问题。真实的工作流早就不是单一 agent、单一窗口、单一项目路径了。上下文散落在本地轨迹里，但下一次 agent 启动时，它们很难被找回。
>
> **所以我做了 Agent Context Manager。**
>
> 我的理解很简单：既然这些对话和操作都已经保存在本地，为什么不能搜索它们？为什么不能让 agent 从过去的 harness trace 里召回相关片段，压缩成一个候选 context block，然后由我审查、应用或丢弃？这就是 `ctx` 的目标：给 agent 一个跨工具的本地上下文层。

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

告诉你的 coding agent：

> 请从 https://github.com/OpenClaudex/agent-context-manager 安装 Agent Context Manager。扫描我的 home 目录下有哪些本地 coding-agent 对话轨迹，把发现的 Claude Code / Codex / CodeBuddy / Cursor / Windsurf / Trae / Code Desk / Roo Code / Cline / Continue / Aider / Goose / OpenHands / Devin / Copilot Workspace / 公司内部 agent 历史路径注册为 recall sources，并配置跨 harness 召回、异步 compact job 和可审阅的 context apply。

安装后，在 agent session 中使用 `/ctx-recall`、`/ctx-compact`、`/ctx-jobs`。底层实现细节在 [`skills/`](skills) 下的 slash-command skills 里。

## ✨ 功能

Agent Context Manager 聚焦一个工作流：

- 在一个 session 里搜索很多本地 coding-agent 历史。
- 把当前 session context 压缩成候选摘要。
- 在候选 context 进入当前 prompt 前保持可审阅。
- 当发现新的 harness 时，让 coding agent 把它的本地 trace source 接进来。

## 🧩 命令

| 命令 | 范围 | 预期行为 |
|---|---|---|
| `/ctx-recall <query>` | 全局、跨 harness | 搜索本地历史日志，生成候选 context block。 |
| `/ctx-compact [instruction]` | 当前 session | 为当前活跃 session 生成候选 compact 摘要。 |
| `/ctx-jobs` | 本地 job store | 列出 job、预览结果、apply 完成结果或 discard 噪声。 |

### 本地召回来源

`/ctx-recall` 的目标是搜索任何你有权限检查的本地 coding-agent 对话轨迹。它可以覆盖内置 source，也可以由 agent 继续接入更多工具，例如：

```text
Claude Code、Codex、CodeBuddy、Cursor、Windsurf、Trae、Code Desk、
Roo Code、Cline、Continue、Aider、Goose、OpenHands、Devin、
Copilot Workspace、公司内部 agent 版本，以及其他本地 harness。
```

如果你的某个 harness 没被自动扫到，直接告诉 agent 要加什么：

> 请为 Cursor 的历史对话增加 recall 支持，它们在 `~/Library/Application Support/Cursor/User/globalStorage/...`，并让 `/ctx-recall` 把这个 source 加入跨 harness 搜索。

预期工作流是 agent-native 的：告诉 coding agent 缺的是哪个工具，或者给出本地 trace 路径，让它把这个 source 接进 source discovery。

## 🛡️ 安全模型

Context 注入是高风险操作，所以 `ctx` 保持本地运行、review-first：recall 和 compact 结果都是候选内容，job 存在 `.ctx/jobs/`，任何内容进入当前 session 前都需要显式确认。

## 🧪 为什么做这个

大多数 agent harness 已经保存了丰富 trace。`ctx` 把这些 trace 变成跨工具可搜索的 context，再进入一个可审阅的操作闭环：

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

## 🙏 致谢

Agent Context Manager 特别受 [VCC](https://github.com/lllyasviel/VCC) 启发。VCC 是面向 agent trace analysis 和 conversation recovery 的 View-oriented Conversation Compiler。本项目的核心思路，包括把 conversation trace 编译成可检索的 context view，以及部分检索设计，都受到 VCC 的影响。

`ctx` 的区别在于，它不绑定某一个单一 agent harness，而是试图凌驾在具体 harness 之上：跨本地 Claude Code、CodeBuddy、Codex trace 做全局搜索，把 recall 和 compact 做成异步 job，并且在任何候选 context 进入当前 session 之前保持可审查、可应用、可丢弃。

也感谢更广泛的 context-management、conversation-recovery 和 agent-memory 项目。它们共同说明了一件事：agent context 应该可以被搜索、被检查，并且能在不同工具之间迁移。

## 📄 License

[MIT](LICENSE)
