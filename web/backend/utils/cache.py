from datetime import datetime, timedelta, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)
from typing import Any, Optional


class SessionCache:
    """
    Simple in-memory dict for active agent sessions.
    Each entry holds the agent SessionManager, LLM config, and parameters.
    Entries expire after `ttl_seconds` of inactivity.
    """

    def __init__(self, ttl_seconds: int = 1800):
        self._store: dict[str, dict[str, Any]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, session_id: str) -> Optional[dict[str, Any]]:
        entry = self._store.get(session_id)
        if entry is None:
            return None
        if _now() - entry["last_accessed"] > self.ttl:
            del self._store[session_id]
            return None
        entry["last_accessed"] = _now()
        return entry

    def set(self, session_id: str, data: dict[str, Any]) -> None:
        data["last_accessed"] = _now()
        data["created_at"] = data.get("created_at", _now())
        self._store[session_id] = data

    def delete(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def evict_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        now = _now()
        expired = [sid for sid, entry in self._store.items()
                   if now - entry["last_accessed"] > self.ttl]
        for sid in expired:
            del self._store[sid]
        return len(expired)

    def __contains__(self, session_id: str) -> bool:
        return self.get(session_id) is not None

    def __len__(self) -> int:
        return len(self._store)


# Singleton cache instance used across the application
session_cache = SessionCache()
