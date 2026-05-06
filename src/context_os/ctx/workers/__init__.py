"""
Shared utilities for ctx background workers.

Workers run as independent processes (via Bash run_in_background),
calling VCC.py for search/compile and claude/codebuddy -p for LLM summarization.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

# Scope → directory mapping
SCOPE_DIRS = {
    "codebuddy": [os.path.expanduser("~/.codebuddy/projects")],
    "claude": [
        os.path.expanduser("~/.claude/projects"),
        os.path.expanduser("~/.claude-internal/projects"),
    ],
    "codex": [
        os.path.expanduser("~/.codex/sessions"),
        os.path.expanduser("~/.codex-internal/sessions"),
    ],
}
SCOPE_DIRS["all"] = [d for dirs in SCOPE_DIRS.values() for d in dirs]


def detect_llm_cli() -> str:
    """Detect which CLI to use for LLM calls. codebuddy preferred, fallback claude."""
    if shutil.which("codebuddy"):
        return "codebuddy"
    if shutil.which("claude"):
        return "claude"
    raise RuntimeError("Neither codebuddy nor claude CLI found in PATH")


def get_vcc_path() -> str:
    """Find VCC.py path."""
    env = os.environ.get("VCC_SCRIPT_PATH")
    if env and os.path.isfile(env):
        return env

    candidates = [
        os.path.expanduser("~/VCC/skills/conversation-compiler/scripts/VCC.py"),
        os.path.expanduser("~/proj/VCC/skills/conversation-compiler/scripts/VCC.py"),
        os.path.expanduser("~/.codebuddy/skills/conversation-compiler/scripts/VCC.py"),
        os.path.expanduser("~/.claude/skills/conversation-compiler/scripts/VCC.py"),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    raise RuntimeError(
        "VCC.py not found. Set VCC_SCRIPT_PATH=/path/to/VCC.py or install VCC first."
    )


def _detect_current_session_files() -> set:
    """Detect currently active session JSONL files (mtime < 60s)."""
    import time

    now = time.time()
    current = set()
    for base in SCOPE_DIRS["all"]:
        if not os.path.isdir(base):
            continue
        for root, _, fnames in os.walk(base):
            for fn in fnames:
                if not fn.endswith(".jsonl"):
                    continue
                fp = os.path.join(root, fn)
                try:
                    if now - os.path.getmtime(fp) < 60:
                        current.add(fp)
                except OSError:
                    pass
    return current


def find_jsonl_files(
    scope: str = "all",
    max_files: int = 50,
    exclude_current_session: bool = False,
) -> List[str]:
    """Find JSONL files for given scope, sorted by mtime descending."""
    dirs = SCOPE_DIRS.get(scope)
    if not dirs:
        raise ValueError(f"Unknown scope: {scope}")

    exclude = _detect_current_session_files() if exclude_current_session else set()

    files = []
    for base in dirs:
        if not os.path.isdir(base):
            continue
        for root, _, fnames in os.walk(base):
            for fn in fnames:
                if not fn.endswith(".jsonl"):
                    continue
                fp = os.path.join(root, fn)
                if fp in exclude:
                    continue
                try:
                    files.append((os.path.getmtime(fp), fp))
                except OSError:
                    pass

    files.sort(key=lambda x: x[0], reverse=True)
    return [fp for _, fp in files[:max_files]]


def find_current_session_jsonl(max_age: int = 1800) -> Optional[str]:
    """Find the current active session's JSONL.

    Returns the most recently modified top-level JSONL (excludes subagent files).
    max_age: maximum age in seconds (default 30 minutes).
    """
    import time

    now = time.time()
    best_mtime = 0.0
    best_path = None

    for base in SCOPE_DIRS["all"]:
        if not os.path.isdir(base):
            continue
        for root, _, fnames in os.walk(base):
            # Skip subagent directories
            if "/subagents/" in root:
                continue
            for fn in fnames:
                if not fn.endswith(".jsonl"):
                    continue
                fp = os.path.join(root, fn)
                try:
                    mt = os.path.getmtime(fp)
                    if now - mt < max_age and mt > best_mtime:
                        best_mtime = mt
                        best_path = fp
                except OSError:
                    pass

    return best_path


def run_llm(prompt: str, timeout: int = 300) -> str:
    """Call LLM CLI for summarization. Passes prompt via stdin."""
    cli = detect_llm_cli()
    proc = subprocess.run(
        [cli, "-p", "--output-format", "text"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"{cli} -p failed: {proc.stderr[:500]}")
    return proc.stdout
