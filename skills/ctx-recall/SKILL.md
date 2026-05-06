---
name: ctx-recall
description: "Async recall: search all conversation history in background. /ctx-recall <query> [--all] [--budget N]. Results are candidates — use /ctx-jobs to apply or discard."
---

# ctx-recall — async recall

Search all local AI conversation history (CodeBuddy, Claude Code, Codex) in background without blocking the current session.

## Usage

```
/ctx-recall <query>
/ctx-recall <query> --all
/ctx-recall <query> --budget 4000
```

## Steps

### Step 1: Launch recall worker in background

Use Bash with `run_in_background: true`:

```bash
CTX_DIR="${CTX_HOME:-$(find ~ -maxdepth 5 -type d -name ctx 2>/dev/null | head -1)}" && cd "$CTX_DIR" && PYTHONPATH=src python3 -m context_os.ctx.workers.recall "<query>" --scope all --budget 8000 --max-hits 5
```

Parameter mapping:
- Default `--scope all`
- If user doesn't specify budget, default `--budget 8000`
- `--max-hits 5`

**Must use `run_in_background: true` — this is the key to async.**

### Step 2: Reply immediately

Do NOT wait for the result. Immediately tell the user:

> Recall job started, query: "<query>"
> Continue chatting. Use `/ctx-jobs` to check results.

## Notes

- This is async — results won't appear immediately
- Results are candidates; user must `/ctx-jobs` apply to inject
- Each call creates a new job
