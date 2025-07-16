import json
from datetime import datetime
from unittest.mock import patch

import pytest

from src.core.services.cache_service import CacheService


class TestCacheService:
    @patch("src.core.services.cache_service.cache")
    def test_set_success(self, mock_cache, mock_settings, cache_test_data):
        # Arrange
        cache_service = CacheService()
        mock_cache.set.return_value = True

        # Act
        result = cache_service.set(
            cache_test_data["key"],
            cache_test_data["data"],
            cache_test_data["timeout"],
        )

        # Assert
        assert result is True
        mock_cache.set.assert_called_once()
        call_args = mock_cache.set.call_args[0]
        assert call_args[0] == cache_test_data["key"]
        assert json.loads(call_args[1]) == cache_test_data["data"]
        assert call_args[2] == cache_test_data["timeout"]

    @patch("src.core.services.cache_service.cache")
    def test_set_with_datetime_serialization(self, mock_cache, mock_settings):
        # Arrange
        cache_service = CacheService()
        data_with_datetime = {"timestamp": datetime(2025, 1, 15, 10, 30, 0)}
        mock_cache.set.return_value = True

        # Act
        result = cache_service.set("test_key", data_with_datetime)

        # Assert
        assert result is True
        call_args = mock_cache.set.call_args[0]
        serialized_data = json.loads(call_args[1])
        assert "2025-01-15T10:30:00" in serialized_data["timestamp"]

    @patch("src.core.services.cache_service.cache")
    def test_set_failure(self, mock_cache, mock_settings, cache_test_data):
        # Arrange
        cache_service = CacheService()
        mock_cache.set.side_effect = Exception("Redis connection failed")

        # Act
        result = cache_service.set(
            cache_test_data["key"], cache_test_data["data"]
        )

        # Assert
        assert result is False

    @patch("src.core.services.cache_service.cache")
    def test_get_success(self, mock_cache, mock_settings, cache_test_data):
        # Arrange
        cache_service = CacheService()
        serialized_data = json.dumps(cache_test_data["data"])
        mock_cache.get.return_value = serialized_data

        # Act
        result = cache_service.get(cache_test_data["key"])

        # Assert
        assert result == cache_test_data["data"]
        mock_cache.get.assert_called_once_with(cache_test_data["key"])

    @patch("src.core.services.cache_service.cache")
    def test_get_cache_miss(self, mock_cache, mock_settings):
        # Arrange
        cache_service = CacheService()
        mock_cache.get.return_value = None

        # Act
        result = cache_service.get("nonexistent_key")

        # Assert
        assert result is None

    @patch("src.core.services.cache_service.cache")
    def test_delete_success(self, mock_cache, mock_settings):
        # Arrange
        cache_service = CacheService()
        mock_cache.delete.return_value = True

        # Act
        result = cache_service.delete("test_key")

        # Assert
        assert result is True
        mock_cache.delete.assert_called_once_with("test_key")

    @patch("src.core.services.cache_service.cache")
    def test_delete_failure(self, mock_cache, mock_settings):
        # Arrange
        cache_service = CacheService()
        mock_cache.delete.side_effect = Exception("Redis connection failed")

        # Act
        result = cache_service.delete("test_key")

        # Assert
        assert result is False

    def test_generate_cache_key(self, mock_settings):
        # Arrange
        cache_service = CacheService()

        # Act
        key = cache_service._generate_cache_key("prefix", "identifier")

        # Assert
        assert key.startswith("prefix:")
        assert len(key) > len("prefix:")

    @patch("src.core.services.cache_service.cache")
    def test_cache_data_success(
        self, mock_cache, mock_settings, cache_test_data
    ):
        # Arrange
        cache_service = CacheService()
        mock_cache.set.return_value = True

        # Act
        result = cache_service.cache_data(
            "test_prefix", "test_id", cache_test_data["data"]
        )

        # Assert
        assert result is True
        mock_cache.set.assert_called_once()

    @patch("src.core.services.cache_service.cache")
    def test_get_cached_data_success(
        self, mock_cache, mock_settings, cache_test_data
    ):
        # Arrange
        cache_service = CacheService()
        cache_data = {
            "data": cache_test_data["data"],
            "cached_at": datetime.now().isoformat(),
            "identifier": "test_id",
        }
        serialized_data = json.dumps(
            cache_data, default=cache_service._json_serializer
        )
        mock_cache.get.return_value = serialized_data

        # Act
        result = cache_service.get_cached_data("test_prefix", "test_id")

        # Assert
        assert result == cache_test_data["data"]

    @patch("src.core.services.cache_service.cache")
    def test_get_cached_data_miss(self, mock_cache, mock_settings):
        # Arrange
        cache_service = CacheService()
        mock_cache.get.return_value = None

        # Act
        result = cache_service.get_cached_data("test_prefix", "test_id")

        # Assert
        assert result is None

    def test_json_serializer_datetime(self, mock_settings):
        # Arrange
        cache_service = CacheService()
        test_datetime = datetime(2025, 1, 15, 10, 30, 0)

        # Act
        result = cache_service._json_serializer(test_datetime)

        # Assert
        assert result == "2025-01-15T10:30:00"

    def test_json_serializer_unsupported_type(self, mock_settings):
        # Arrange
        cache_service = CacheService()

        # Act & Assert
        with pytest.raises(TypeError):
            cache_service._json_serializer(object())
