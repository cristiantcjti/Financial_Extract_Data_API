from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest
from ninja.errors import HttpError

from src.financial.controllers.extract_financial_data import (
    extract_financial_data,
    health_check,
)
from src.financial.schemas.schemas import (
    FinancialDataResponseSchema,
    HealthCheckSchema,
)


class TestExtractFinancialDataController:
    def test_extract_financial_data_successful_flow(
        self,
        request_factory: Any,
        valid_request_data: dict[str, Any],
        sample_formatted_response: dict[str, Any],
    ) -> None:
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        with (
            patch(
                "src.financial.controllers.extract_financial_data.DynamicClientService"
            ) as mock_client_service,
            patch(
                "src.financial.controllers.extract_financial_data.ExtractionService"
            ) as mock_extraction_service,
        ):
            client_data = Mock()
            client_data.name = "Test Client"
            client_data.id = "client-123"
            client_data.token = "client-token"
            mock_client_service.return_value.get_or_create_client.return_value = client_data

            response_schema = FinancialDataResponseSchema(
                **sample_formatted_response
            )
            mock_extraction_service.return_value.extract_financial_data.return_value = response_schema

            # Act
            result = extract_financial_data(request, valid_request_data)

            # Assert
            assert isinstance(result, FinancialDataResponseSchema)  # noqa: S101
            assert result.user_document == "12345678901"  # noqa: S101
            mock_client_service.return_value.get_or_create_client.assert_called_once_with(
                "12345678901"
            )

    def test_extract_financial_data_client_service_validation_error(
        self, request_factory: Any, valid_request_data: dict[str, Any]
    ) -> None:
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        with patch(
            "src.financial.controllers.extract_financial_data.DynamicClientService"
        ) as mock_client_service:
            mock_client_service.return_value.get_or_create_client.side_effect = ValueError(
                "Invalid user document"
            )

            # Act & Assert
            with pytest.raises(HttpError) as exc_info:
                extract_financial_data(request, valid_request_data)

            assert exc_info.value.status_code == 400  # noqa: S101
            assert "Validation error" in str(exc_info.value.message)  # noqa: S101

    def test_extract_financial_data_extraction_service_error(
        self, request_factory: Any, valid_request_data: dict[str, Any]
    ) -> None:
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        with (
            patch(
                "src.financial.controllers.extract_financial_data.DynamicClientService"
            ) as mock_client_service,
            patch(
                "src.financial.controllers.extract_financial_data.ExtractionService"
            ) as mock_extraction_service,
        ):
            client_data = Mock()
            client_data.name = "Test Client"
            client_data.id = "client-123"
            client_data.token = "client-token"
            mock_client_service.return_value.get_or_create_client.return_value = client_data

            mock_extraction_service.return_value.extract_financial_data.side_effect = Exception(
                "Service unavailable"
            )

            # Act & Assert
            with pytest.raises(HttpError) as exc_info:
                extract_financial_data(request, valid_request_data)

            assert exc_info.value.status_code == 500  # noqa: S101
            assert "unexpected error" in str(exc_info.value.message)  # noqa: S101

    def test_extract_financial_data_http_error_propagation(
        self, request_factory: Any, valid_request_data: dict[str, Any]
    ) -> None:
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        with patch(
            "src.financial.controllers.extract_financial_data.DynamicClientService"
        ) as mock_client_service:
            mock_client_service.return_value.get_or_create_client.side_effect = HttpError(
                404, "Not found"
            )

            # Act & Assert
            with pytest.raises(HttpError) as exc_info:
                extract_financial_data(request, valid_request_data)

            assert exc_info.value.status_code == 404  # noqa: S101

    def test_extract_financial_data_logs_user_document(
        self, request_factory: Any, valid_request_data: dict[str, Any]
    ) -> None:
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        with (
            patch(
                "src.financial.controllers.extract_financial_data.DynamicClientService"
            ) as mock_client_service,
            patch(
                "src.financial.controllers.extract_financial_data.ExtractionService"
            ) as mock_extraction_service,
            patch(
                "src.financial.controllers.extract_financial_data.logger"
            ) as mock_logger,
        ):
            client_data = Mock()
            mock_client_service.return_value.get_or_create_client.return_value = client_data
            mock_extraction_service.return_value.extract_financial_data.side_effect = Exception(
                "Test error"
            )

            # Act
            with pytest.raises(HttpError):
                extract_financial_data(request, valid_request_data)

            # Assert
            mock_logger.info.assert_called()
            mock_logger.error.assert_called()

    def test_extract_financial_data_service_coordination(
        self,
        request_factory: Any,
        valid_request_data: dict[str, Any],
        sample_formatted_response: dict[str, Any],
    ) -> None:
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        with (
            patch(
                "src.financial.controllers.extract_financial_data.DynamicClientService"
            ) as mock_client_service,
            patch(
                "src.financial.controllers.extract_financial_data.ExtractionService"
            ) as mock_extraction_service,
        ):
            client_data = Mock()
            client_data.name = "Test Client"
            client_data.id = "client-123"
            client_data.token = "client-token"
            mock_client_service.return_value.get_or_create_client.return_value = client_data

            response_schema = FinancialDataResponseSchema(
                **sample_formatted_response
            )
            mock_extraction_service.return_value.extract_financial_data.return_value = response_schema

            # Act
            extract_financial_data(request, valid_request_data)

            # Assert
            mock_extraction_service.return_value.extract_financial_data.assert_called_once_with(
                user_document="12345678901",
                dynamic_client_id="client-123",
                dynamic_token="client-token",
            )


class TestHealthCheckController:
    def test_health_check_all_services_healthy(
        self, request_factory: Any
    ) -> None:
        # Arrange
        request = request_factory.get("/api/v1/health")

        with patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ):
            # Act
            result = health_check(request)

            # Assert
            assert isinstance(result, HealthCheckSchema)  # noqa: S101
            assert result.status in ["healthy", "degraded"]  # noqa: S101
            assert "api" in result.services  # noqa: S101
            assert result.services["api"] == "healthy"  # noqa: S101

    def test_health_check_extraction_service_failure(
        self, request_factory: Any
    ) -> None:
        # Arrange
        request = request_factory.get("/api/v1/health")

        with patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ) as mock_extraction:
            mock_extraction.side_effect = Exception("Service unavailable")

            # Act
            result = health_check(request)

            # Assert
            assert isinstance(result, HealthCheckSchema)  # noqa: S101
            assert result.status == "degraded"  # noqa: S101
            assert result.services["ofda_api"] == "unhealthy"  # noqa: S101

    def test_health_check_includes_timestamp(
        self, request_factory: Any
    ) -> None:
        # Arrange
        request = request_factory.get("/api/v1/health")

        with patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ):
            # Act
            result = health_check(request)

            # Assert
            assert hasattr(result, "timestamp")  # noqa: S101
            assert isinstance(result.timestamp, datetime)  # noqa: S101

    def test_health_check_service_status_mapping(
        self, request_factory: Any
    ) -> None:
        # Arrange
        request = request_factory.get("/api/v1/health")

        with patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ):
            # Act
            result = health_check(request)

            # Assert
            expected_services = ["api", "database", "ofda_api"]
            for service in expected_services:
                assert service in result.services  # noqa: S101
                assert result.services[service] in ["healthy", "unhealthy"]  # noqa: S101

    def test_health_check_overall_status_logic(
        self, request_factory: Any
    ) -> None:
        # Arrange
        request = request_factory.get("/api/v1/health")

        with patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ):
            # Act
            result = health_check(request)

            # Assert
            service_statuses = list(result.services.values())
            if all(status == "healthy" for status in service_statuses):
                assert result.status == "healthy"  # noqa: S101
            else:
                assert result.status in ["degraded", "unhealthy"]  # noqa: S101
