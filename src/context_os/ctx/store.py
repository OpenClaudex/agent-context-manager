"""
ctx store - file-based job storage.

Jobs are stored as individual JSON files in .ctx/jobs/.
No database, no locking — single writer per job.
"""

from __future__ import annotations
import json
import os
import hashlib
import time
import glob
from typing import List, Optional

from context_os.ctx.models import Job


def _default_store_dir() -> str:
    """Jobs stored in .ctx/jobs/ relative to the project root."""
    # Walk up from this file to find the project root (has pyproject.toml)
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if os.path.exists(os.path.join(here, "pyproject.toml")):
            return os.path.join(here, ".ctx", "jobs")
        here = os.path.dirname(here)
    # Fallback: relative to cwd
    return os.path.join(os.getcwd(), ".ctx", "jobs")


class JobStore:
    """File-system based job store."""

    def __init__(self, store_dir: Optional[str] = None):
        self.store_dir = store_dir or _default_store_dir()
        os.makedirs(self.store_dir, exist_ok=True)

    def _path(self, job_id: str) -> str:
        return os.path.join(self.store_dir, f"{job_id}.json")

    def save(self, job: Job) -> None:
        """Save (create or update) a job."""
        with open(self._path(job.id), "w", encoding="utf-8") as f:
            json.dump(job.to_dict(), f, ensure_ascii=False, indent=2)

    def load(self, job_id: str) -> Optional[Job]:
        """Load a job by ID. Returns None if not found."""
        path = self._path(job_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Job.from_dict(json.load(f))

    def list_jobs(self, type_filter: Optional[str] = None, status_filter: Optional[str] = None) -> List[Job]:
        """List all jobs, optionally filtered."""
        jobs = []
        for path in sorted(glob.glob(os.path.join(self.store_dir, "*.json"))):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    job = Job.from_dict(json.load(f))
                if type_filter and job.type != type_filter:
                    continue
                if status_filter and job.status != status_filter:
                    continue
                jobs.append(job)
            except (json.JSONDecodeError, KeyError):
                continue
        # Sort by created_at descending (newest first)
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return jobs

    def delete(self, job_id: str) -> bool:
        """Delete a job file."""
        path = self._path(job_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False


def _detect_current_session_files() -> set:
    """
    Find JSONL files that are the *current active session* (modified <60s).
    These should be excluded from snapshot hash — they change every turn.
    Same heuristic as pipeline._detect_current_sessions().
    """
    paths = [
        os.path.expanduser("~/.codebuddy/projects"),
        os.path.expanduser("~/.claude-internal/projects"),
        os.path.expanduser("~/.codex-internal/sessions"),
    ]
    now = time.time()
    current = set()

    for base in paths:
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            for fn in files:
                if not fn.endswith(".jsonl"):
                    continue
                fp = os.path.join(root, fn)
                try:
                    if now - os.path.getmtime(fp) < 60:
                        current.add(fp)
                except OSError:
                    pass
    return current


def snapshot_hash() -> str:
    """
    Compute a snapshot hash of the conversation state,
    EXCLUDING the current active session's JSONL.

    The current session's file changes every turn (Claude writes to it),
    so including it makes stale detection fire 100% of the time.
    We only track *other* recently active sessions — if THOSE change,
    the recall context may actually be stale.
    """
    paths = [
        os.path.expanduser("~/.codebuddy/projects"),
        os.path.expanduser("~/.claude-internal/projects"),
        os.path.expanduser("~/.codex-internal/sessions"),
    ]

    # Exclude current session files (modified <60s)
    current_files = _detect_current_session_files()

    recent_files = []
    now = time.time()

    for base in paths:
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            for fn in files:
                if not fn.endswith(".jsonl"):
                    continue
                fp = os.path.join(root, fn)
                if fp in current_files:
                    continue  # Skip current session
                try:
                    st = os.stat(fp)
                    # Consider files modified in last 30 minutes
                    if now - st.st_mtime < 1800:
                        recent_files.append((st.st_mtime, st.st_size, fp))
                except OSError:
                    pass

    if not recent_files:
        # No other active sessions — hash is stable
        return "no-other-sessions"

    # Sort by mtime descending, take top 5
    recent_files.sort(key=lambda x: x[0], reverse=True)
    parts = []
    for mtime, size, fp in recent_files[:5]:
        parts.append(f"{mtime:.2f}:{size}")

    raw = "|".join(parts)
    return hashlib.md5(raw.encode()).hexdigest()[:16]
