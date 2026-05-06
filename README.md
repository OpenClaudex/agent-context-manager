# ctx

Async cross-harness context management for agent sessions.

`ctx` is a small set of slash-command skills for reviewable context operations:

- `/ctx-recall`: recall historical context across local Claude Code, CodeBuddy, and Codex logs.
- `/ctx-compact`: compact the current session into a reviewable summary.
- `/ctx-jobs`: review, apply, or discard context jobs.

Slogan:

```text
Recall globally. Compact locally. Apply deliberately.
```

## Why

Agent sessions often lose useful context because old conversation logs live outside the current window. Direct recall can also pollute the current session when the result is noisy or wrong.

`ctx` turns context work into a job queue:

```text
foreground chat continues
  -> background recall or compact job runs
  -> result becomes a reviewable suggestion
  -> user applies or discards it
```

This is not a full memory palace and not a replacement for the model context window. It is a lightweight context-management loop.

## Commands

| Command | Scope | Purpose |
|---|---|---|
| `/ctx-recall <query>` | Global, cross-harness | Search historical local logs and produce a candidate context block. |
| `/ctx-compact [instruction]` | Current session | Produce a candidate compact summary of the active session. |
| `/ctx-jobs` | Local job store | List jobs, preview results, apply, or discard. |

## Supported local sources

`/ctx-recall` searches JSONL logs from these local locations:

```text
~/.codebuddy/projects
~/.claude/projects
~/.claude-internal/projects
~/.codex/sessions
~/.codex-internal/sessions
```

You can narrow recall scope with:

```text
--scope all | codebuddy | claude | codex
```

## Requirements

- Python 3.9+
- `claude` or `codebuddy` CLI available in `PATH` for background summarization
- VCC `VCC.py` available for log compilation and grep

Set `VCC_SCRIPT_PATH` if VCC is not in one of the default locations:

```bash
export VCC_SCRIPT_PATH="/path/to/VCC/skills/conversation-compiler/scripts/VCC.py"
```

## Install for Claude Code

Clone this repo:

```bash
git clone https://github.com/OpenClaudex/ctx.git
cd ctx
```

Install the skills by symlink:

```bash
./scripts/install-claude.sh
```

Restart Claude Code after installation.

## Install for CodeBuddy

CodeBuddy skill installation is also supported:

```bash
./scripts/install-codebuddy.sh
```

Restart CodeBuddy after installation.

## Manual CLI

The backend can be run directly:

```bash
cd /path/to/ctx
PYTHONPATH=src python3 -m context_os.ctx.workers.recall "VCC architecture" --scope all --budget 8000 --max-hits 5
PYTHONPATH=src python3 -m context_os.ctx.runner list
```

## Status

`v0.1-alpha`.

Working today:

- Async recall jobs.
- Async compact jobs.
- File-based job store.
- Apply and discard flow.
- Cross-harness recall over local CodeBuddy, Claude Code, and Codex logs.

Known limits:

- `apply` injects text back into the conversation; it does not edit a model's internal context state.
- Recall is fuzzy and can return no result or meta-results.
- Compact is current-session only.
- VCC is currently required as a backend.

## Relationship to VCC

`ctx` is built on the same core insight as VCC: historical logs are not lost, they need to be compiled into agent-friendly context.

VCC focuses on compiling and searching conversation logs. `ctx` adds an async review loop around context operations:

```text
VCC: recover and read historical context
ctx: recall or compact context as reviewable jobs
```

In short:

```text
Built on the VCC insight, ctx turns context recovery into an async, reviewable context-management loop.
```
