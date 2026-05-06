---
name: ctx-compact
description: "Async compact: generate candidate summary of current session. /ctx-compact [instruction]. Result is a candidate — use /ctx-jobs to apply or discard."
---

# ctx-compact — async compact

Generate a structured summary of the current session in background without blocking.

## Usage

```
/ctx-compact
/ctx-compact focus on architecture decisions and unfinished tasks
```

## Steps

### Step 1: Launch compact worker in background

Use Bash with `run_in_background: true`:

```bash
CTX_DIR="${CTX_HOME:-$(find ~ -maxdepth 5 -type d -name ctx 2>/dev/null | head -1)}" && cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.workers.compact "<instruction if any>"
```

If user gave no instruction, omit the argument entirely:

```bash
CTX_DIR="${CTX_HOME:-$(find ~ -maxdepth 5 -type d -name ctx 2>/dev/null | head -1)}" && cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.workers.compact
```

**Must use `run_in_background: true`.**

### Step 2: Reply immediately

> Compact job started. Continue chatting. Use `/ctx-jobs` to check results.

## Notes

- Summary is a candidate — won't replace context until user applies via `/ctx-jobs`
- Summary preserves file paths, error messages, and technical specifics
- Short sessions (<500 chars) skip LLM and use raw transcript
