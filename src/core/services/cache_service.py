import hashlib
import json
from datetime import datetime
from typing import Any

from django.conf import settings
from django.core.cache import cache

from src.config.logging import logger


class CacheService:
    def __init__(self) -> None:
        self.logger = logger
        self.default_timeout = getattr(settings, "CACHE_DEFAULT_TIMEOUT", 300)

    def _generate_cache_key(self, prefix: str, identifier: str) -> str:
        key_parts = [prefix, identifier]
        key_string = ":".join(str(part) for part in key_parts)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def set(self, key: str, data: Any, timeout: int | None = None) -> bool:
        try:
            timeout = timeout or self.default_timeout
            serialized_data = json.dumps(data, default=self._json_serializer)
            cache.set(key, serialized_data, timeout)
            self.logger.debug(
                f"Cached data with key: {key}, timeout: {timeout}s"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache data with key {key}: {str(e)}")
            return False

    def get(self, key: str) -> Any | None:
        try:
            serialized_data = cache.get(key)
            if serialized_data is None:
                self.logger.debug(f"Cache miss for key: {key}")
                return None

            data = json.loads(serialized_data)
            self.logger.debug(f"Cache hit for key: {key}")
            return data
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(
                f"Failed to retrieve cached data with key {key}: {str(e)}"
            )
            return None

    def delete(self, key: str) -> bool:
        try:
            cache.delete(key)
            self.logger.debug(f"Deleted cache key: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False

    def cache_data(self, prefix: str, identifier: str, data: dict) -> bool:
        cache_key = self._generate_cache_key(prefix, identifier)
        cache_data = {
            "data": data,
            "cached_at": datetime.now().isoformat(),
            "identifier": identifier,
        }

        return self.set(cache_key, cache_data)

    def get_cached_data(self, prefix: str, identifier: str) -> dict | None:
        cache_key = self._generate_cache_key(prefix, identifier)
        cached_data = self.get(cache_key)

        if cached_data:
            return cached_data.get("data")

        return None

    def invalidate_data(self, prefix: str, identifier: str) -> bool:
        cache_key = self._generate_cache_key(prefix, identifier)
        return self.delete(cache_key)

    def _json_serializer(self, obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def clear_all_cache(self) -> bool:
        try:
            cache.clear()
            self.logger.info("All cache cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {str(e)}")
            return False
