#!/usr/bin/env python3
"""
Background recall worker.

Called by SKILL.md via Bash run_in_background:
    PYTHONPATH=src python3 -m context_os.ctx.workers.recall "query" --scope all --budget 8000 --max-hits 5
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

from context_os.ctx.models import Job
from context_os.ctx.store import JobStore, snapshot_hash
from context_os.ctx.workers import find_jsonl_files, get_vcc_path, run_llm


def main(query: str, scope: str = "all", budget: int = 8000, max_hits: int = 5):
    store = JobStore()

    # 1. Create job, output job_id immediately
    job = Job(
        type="recall",
        scope=scope,
        query=query,
        status="running",
        base_snapshot_hash=snapshot_hash(),
        params={"budget": budget, "max_hits": max_hits, "scope": scope},
    )
    job.started_at = time.time()
    store.save(job)
    print(json.dumps({"ok": True, "job_id": job.id, "status": "running"}))
    sys.stdout.flush()

    tmpdir = tempfile.mkdtemp(prefix="ctx_recall_")
    try:
        # 2. Find JSONL files
        jsonl_files = find_jsonl_files(scope, exclude_current_session=True)
        if not jsonl_files:
            raise RuntimeError(f"No JSONL files found for scope={scope}")

        # 3. Call VCC.py --grep
        vcc = get_vcc_path()
        cmd = [sys.executable, vcc, *jsonl_files, "--grep", query, "-o", tmpdir]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        grep_stdout = result.stdout

        # 4. Read .view.txt files for context
        view_files = sorted(
            glob.glob(os.path.join(tmpdir, "*.view.txt")),
            key=os.path.getmtime,
            reverse=True,
        )[:max_hits]

        view_content = ""
        per_file_budget = budget // max(len(view_files), 1)
        for vf in view_files:
            with open(vf, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            if len(text) > per_file_budget:
                text = text[:per_file_budget] + "\n...(truncated)"
            view_content += f"\n--- {os.path.basename(vf)} ---\n{text}"

        # 5. No results → auto-discard (don't clutter job list)
        if not grep_stdout.strip():
            job.result_meta = {"hits": 0, "files_searched": len(jsonl_files)}
            job.status = "discarded"
            job.error = f"No results found for: {query}"
            job.finished_at = time.time()
            store.save(job)
            return

        # Count actual grep hits (non-empty lines in grep output)
        grep_hit_count = sum(1 for line in grep_stdout.strip().splitlines() if line.strip())

        # 6. Call LLM to summarize
        prompt = f"""You are a context retrieval assistant. Below are search results from conversation history matching the query "{query}".

<grep_results>
{grep_stdout[:budget]}
</grep_results>

<view_details>
{view_content[:budget]}
</view_details>

Synthesize the relevant information into a structured context block. Format:

[RECALL: {query}]
## Key Findings
- (bulleted, with source references)

## Relevant Details
(technical details, decisions, code snippets)

## Source Sessions
- (source files)

Be concise but preserve critical technical details."""

        summary = run_llm(prompt)

        # 7. Write result
        job.result_full = summary
        job.result_preview = summary[:500]
        job.result_meta = {
            "hits": grep_hit_count,
            "files_searched": len(jsonl_files),
        }
        job.status = "done"
        job.finished_at = time.time()
        store.save(job)

    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.finished_at = time.time()
        store.save(job)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ctx recall background worker")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--scope", default="all", choices=["all", "codebuddy", "claude", "codex"]
    )
    parser.add_argument("--budget", type=int, default=8000)
    parser.add_argument("--max-hits", type=int, default=5)
    args = parser.parse_args()
    main(args.query, args.scope, args.budget, args.max_hits)
