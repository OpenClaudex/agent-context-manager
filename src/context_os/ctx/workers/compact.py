#!/usr/bin/env python3
"""
Background compact worker.

Called by SKILL.md via Bash run_in_background:
    PYTHONPATH=src python3 -m context_os.ctx.workers.compact "instruction"
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
from context_os.ctx.workers import find_current_session_jsonl, get_vcc_path, run_llm


def main(instruction: str = ""):
    store = JobStore()

    # 1. Create job
    job = Job(
        type="compact",
        scope="current",
        instruction=instruction,
        status="running",
        base_snapshot_hash=snapshot_hash(),
    )
    job.started_at = time.time()
    store.save(job)
    print(json.dumps({"ok": True, "job_id": job.id, "status": "running"}))
    sys.stdout.flush()

    tmpdir = tempfile.mkdtemp(prefix="ctx_compact_")
    try:
        # 2. Find current session JSONL
        jsonl_path = find_current_session_jsonl()
        if not jsonl_path:
            raise RuntimeError("Cannot find current session JSONL (no file modified <60s)")

        # 3. VCC.py compile → .min.txt
        vcc = get_vcc_path()
        subprocess.run(
            [sys.executable, vcc, jsonl_path, "-o", tmpdir],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # 4. Read .min.txt files (fallback to .txt if .min.txt is empty)
        min_files = sorted(glob.glob(os.path.join(tmpdir, "*.min.txt")))
        min_txt = "\n".join(
            open(f, encoding="utf-8", errors="replace").read() for f in min_files
        ).strip() if min_files else ""

        if not min_txt:
            # Fallback: use full .txt output
            txt_files = sorted(glob.glob(os.path.join(tmpdir, "*.txt")))
            txt_files = [f for f in txt_files if not f.endswith(".min.txt")]
            min_txt = "\n".join(
                open(f, encoding="utf-8", errors="replace").read() for f in txt_files
            ).strip() if txt_files else ""

        if not min_txt:
            raise RuntimeError("VCC.py produced no usable output for this session")

        # Truncate keeping tail (most recent content is more important)
        MAX_INPUT = 100_000
        if len(min_txt) > MAX_INPUT:
            min_txt = "(earlier content truncated)\n...\n" + min_txt[-MAX_INPUT:]

        # 5. Short session → auto-discard (not enough content to compact)
        if len(min_txt) < 500:
            job.status = "discarded"
            job.error = f"Session too short to summarize ({len(min_txt)} chars)"
            job.finished_at = time.time()
            store.save(job)
            return

        # 6. Call LLM to generate summary
        instruction_line = (
            f"\nUser instruction: {instruction}" if instruction else ""
        )
        prompt = f"""You are a conversation compactor. Below is a session transcript.{instruction_line}

<session_transcript>
{min_txt}
</session_transcript>

Generate a structured summary:

[SESSION COMPACT]
## Topic
(one sentence)

## Key Decisions
- ...

## Completed
- ...

## Current State
(current progress)

## TODO
- ...

## Key Context
(file paths, architecture, technical details needed later)

Preserve ALL file paths, error messages, and technical specifics. Over-include rather than under-include."""

        summary = run_llm(prompt)

        # 7. Write result
        job.result_full = summary
        job.result_preview = summary[:500]
        job.result_meta = {
            "input_chars": len(min_txt),
            "output_chars": len(summary),
            "source_jsonl": jsonl_path,
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
    parser = argparse.ArgumentParser(description="ctx compact background worker")
    parser.add_argument("instruction", nargs="?", default="", help="Compact instruction")
    args = parser.parse_args()
    main(args.instruction)
