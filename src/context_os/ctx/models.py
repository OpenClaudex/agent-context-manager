"""
ctx data model — Job for async context management.

Each job represents one async operation (recall or compact).
Jobs are created, run, and then applied or discarded.
"""

from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


# Valid status transitions:
#   pending → running → done → applied | discarded | stale
#   pending → running → failed
VALID_STATUSES = {"pending", "running", "done", "stale", "applied", "discarded", "failed"}
VALID_TYPES = {"compact", "recall"}
VALID_SCOPES = {"current", "all"}


@dataclass
class Job:
    """A single async context management job."""

    # Identity
    id: str = ""
    type: str = ""                      # "compact" | "recall"
    scope: str = "current"              # "current" | "all"

    # Status
    status: str = "pending"

    # Stale detection: snapshot of conversation state at job creation
    base_snapshot_hash: str = ""        # f"{mtime}:{size}" of current JSONL

    # Input
    query: str = ""                     # recall query
    instruction: str = ""               # compact instruction
    params: Dict[str, Any] = field(default_factory=dict)  # budget, max_hits, etc.

    # Result
    result_preview: str = ""            # first 500 chars
    result_full: str = ""               # complete injectable text
    result_meta: Dict[str, Any] = field(default_factory=dict)  # hits, latency, etc.

    # Lifecycle timestamps
    created_at: float = 0.0
    started_at: float = 0.0
    finished_at: float = 0.0
    error: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = uuid.uuid4().hex[:8]
        if not self.created_at:
            self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "scope": self.scope,
            "status": self.status,
            "base_snapshot_hash": self.base_snapshot_hash,
            "query": self.query,
            "instruction": self.instruction,
            "params": self.params,
            "result_preview": self.result_preview,
            "result_full": self.result_full,
            "result_meta": self.result_meta,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Job:
        return cls(
            id=d.get("id", ""),
            type=d.get("type", ""),
            scope=d.get("scope", "current"),
            status=d.get("status", "pending"),
            base_snapshot_hash=d.get("base_snapshot_hash", ""),
            query=d.get("query", ""),
            instruction=d.get("instruction", ""),
            params=d.get("params", {}),
            result_preview=d.get("result_preview", ""),
            result_full=d.get("result_full", ""),
            result_meta=d.get("result_meta", {}),
            created_at=d.get("created_at", 0.0),
            started_at=d.get("started_at", 0.0),
            finished_at=d.get("finished_at", 0.0),
            error=d.get("error", ""),
        )

    @property
    def age_str(self) -> str:
        """Human-readable age since creation."""
        elapsed = time.time() - self.created_at
        if elapsed < 60:
            return f"{elapsed:.0f}s ago"
        elif elapsed < 3600:
            return f"{elapsed/60:.0f}m ago"
        else:
            return f"{elapsed/3600:.1f}h ago"

    @property
    def summary(self) -> str:
        """One-line summary for listing."""
        label = self.query[:40] if self.query else (self.instruction[:40] if self.instruction else self.type)
        return f"[{self.id}] {self.type}/{self.scope} {self.status} — {label} ({self.age_str})"
