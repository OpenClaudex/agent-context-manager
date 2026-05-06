#!/usr/bin/env python3
"""
ctx runner — CLI backend for ctx-jobs skill.

All subcommands output JSON to stdout for SKILL.md parsing.
This is NOT a user-facing CLI — it's called by Claude via Bash in SKILL.md.

Note: recall and compact are now handled by background workers
(context_os.ctx.workers.recall / compact), not by this runner.

Subcommands:
    list [--type TYPE] [--status STATUS]
    show <job-id>
    apply <job-id>
    discard <job-id>
"""

from __future__ import annotations
import argparse
import json
import sys


def _output(data: dict):
    """JSON output to stdout."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _error(msg: str, code: int = 1):
    """JSON error output."""
    _output({"ok": False, "error": msg})
    sys.exit(code)


def cmd_list(args):
    """List jobs. Default: only actionable (done/running). --all for everything."""
    import time
    from context_os.ctx.store import JobStore

    store = JobStore()
    show_all = getattr(args, 'all', False)

    jobs = store.list_jobs(
        type_filter=args.type if hasattr(args, 'type') and args.type else None,
        status_filter=args.status if hasattr(args, 'status') and args.status else None,
    )

    now = time.time()
    EXPIRE_SECONDS = 24 * 3600  # 24h

    # Auto-cleanup: delete terminal jobs older than 24h
    cleaned = 0
    kept = []
    for j in jobs:
        age = now - j.created_at
        if age > EXPIRE_SECONDS and j.status in ("applied", "discarded", "failed"):
            store.delete(j.id)
            cleaned += 1
            continue
        # Auto-expire: done jobs older than 24h → discard
        if age > EXPIRE_SECONDS and j.status == "done":
            j.status = "expired"
            store.save(j)
            if not show_all:
                continue
        # Default: only show actionable jobs
        if not show_all and j.status not in ("done", "running", "stale"):
            continue
        kept.append(j)

    _output({
        "ok": True,
        "count": len(kept),
        "cleaned": cleaned,
        "jobs": [
            {
                "id": j.id,
                "type": j.type,
                "scope": j.scope,
                "status": j.status,
                "query": j.query,
                "instruction": j.instruction,
                "created_at": j.created_at,
                "age": j.age_str,
                "preview": j.result_preview[:200] if j.result_preview else "",
                "hits": j.result_meta.get("hits", 0) if j.type == "recall" else None,
                "error": j.error if j.status == "failed" else "",
            }
            for j in kept
        ],
    })


def cmd_show(args):
    """Show full job details."""
    from context_os.ctx.store import JobStore

    store = JobStore()
    job = store.load(args.job_id)
    if not job:
        _error(f"job {args.job_id} not found")

    _output({
        "ok": True,
        "job": job.to_dict(),
    })


def cmd_apply(args):
    """Apply a job's result. Checks for stale state (unless --force)."""
    from context_os.ctx.store import JobStore, snapshot_hash

    store = JobStore()
    job = store.load(args.job_id)
    if not job:
        _error(f"job {args.job_id} not found")

    if job.status not in ("done", "stale"):
        _error(f"cannot apply job with status '{job.status}' (must be 'done' or 'stale' with --force)")

    if not job.result_full:
        _error("job has no result to apply")

    # Stale check (skip if --force)
    force = getattr(args, 'force', False)
    if not force:
        current_hash = snapshot_hash()
        if (job.base_snapshot_hash
                and job.base_snapshot_hash != "no-other-sessions"
                and current_hash != "no-other-sessions"
                and current_hash != job.base_snapshot_hash):
            job.status = "stale"
            store.save(job)
            _output({
                "ok": False,
                "status": "stale",
                "job_id": job.id,
                "message": "Context has changed since job was created. Use --force to apply anyway, or re-run.",
                "base_hash": job.base_snapshot_hash,
                "current_hash": current_hash,
            })
            return

    # Apply
    job.status = "applied"
    store.save(job)

    _output({
        "ok": True,
        "status": "applied",
        "job_id": job.id,
        "result": job.result_full,
    })


def cmd_discard(args):
    """Discard a job."""
    from context_os.ctx.store import JobStore

    store = JobStore()
    job = store.load(args.job_id)
    if not job:
        _error(f"job {args.job_id} not found")

    job.status = "discarded"
    store.save(job)

    _output({
        "ok": True,
        "status": "discarded",
        "job_id": job.id,
    })


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ctx-runner", description="ctx skill backend")
    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List jobs")
    p_list.add_argument("--type", choices=["recall", "compact"])
    p_list.add_argument("--status")
    p_list.add_argument("--all", action="store_true", help="Show all jobs including applied/discarded")

    # show
    p_show = sub.add_parser("show", help="Show job details")
    p_show.add_argument("job_id", help="Job ID")

    # apply
    p_apply = sub.add_parser("apply", help="Apply job result")
    p_apply.add_argument("job_id", help="Job ID")
    p_apply.add_argument("--force", action="store_true", help="Force apply even if stale")

    # discard
    p_discard = sub.add_parser("discard", help="Discard job")
    p_discard.add_argument("job_id", help="Job ID")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "list": cmd_list,
        "show": cmd_show,
        "apply": cmd_apply,
        "discard": cmd_discard,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
