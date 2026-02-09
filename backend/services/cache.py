import json
import os
import time
from typing import Any, Dict, Optional


class SimpleFileCache:
    def __init__(self, cache_path: str, default_ttl_seconds: int = 86400):
        self.cache_path = cache_path
        self.default_ttl_seconds = default_ttl_seconds
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.cache_path):
            return {}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {}

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.cache_path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def get(self, key: str) -> Optional[Any]:
        data = self._load()
        entry = data.get(key)
        if not entry:
            return None
        if time.time() - entry.get("timestamp", 0) > entry.get("ttl", self.default_ttl_seconds):
            return None
        return entry.get("value")

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        data = self._load()
        data[key] = {
            "timestamp": time.time(),
            "ttl": ttl_seconds or self.default_ttl_seconds,
            "value": value,
        }
        self._save(data)
