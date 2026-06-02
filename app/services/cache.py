import time
from typing import Any, Optional
from app.services.logger import get_logger

logger = get_logger("cache")


class Cache:
    """Simple in-memory TTL cache."""

    def __init__(self, default_ttl: int = 3600):
        self._store: dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = time.time() + (ttl or self.default_ttl)
        self._store[key] = (value, expires_at)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        now = time.time()
        return sum(1 for _, (_, exp) in self._store.items() if exp > now)


# Global cache instance
cache = Cache(default_ttl=3600)
