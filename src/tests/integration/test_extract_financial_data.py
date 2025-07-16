from unittest.mock import Mock, patch

import pytest
from ninja.errors import HttpError

from src.financial.controllers.extract_financial_data import (
    extract_financial_data,
)
from src.financial.schemas.schemas import ExtractionRequestSchema


class TestExtractFinancialDataController:
    def test_extract_financial_data_success(
        self,
        request_factory,
        valid_request_data,
        mock_services,
        sample_formatted_response,
    ):
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        client_data = Mock()
        client_data.name = "Test Client"
        client_data.id = "client-123"
        client_data.token = "client-token"
        mock_services[
            "client_service"
        ].get_or_create_client.return_value = client_data

        from src.financial.schemas.schemas import FinancialDataResponseSchema

        response_schema = FinancialDataResponseSchema(
            **sample_formatted_response
        )
        mock_services[
            "extraction_service"
        ].extract_financial_data.return_value = response_schema

        # Act
        result = extract_financial_data(request, valid_request_data)

        # Assert
        assert isinstance(result, FinancialDataResponseSchema)
        assert result.user_document == "12345678901"
        mock_services[
            "client_service"
        ].get_or_create_client.assert_called_once_with("12345678901")
        mock_services[
            "extraction_service"
        ].extract_financial_data.assert_called_once_with(
            user_document="12345678901",
            dynamic_client_id="client-123",
            dynamic_token="client-token",
        )

    def test_extract_financial_data_client_service_failure(
        self, request_factory, valid_request_data, mock_services
    ):
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")
        mock_services[
            "client_service"
        ].get_or_create_client.side_effect = ValueError(
            "Client creation failed"
        )

        # Act & Assert
        with pytest.raises(HttpError) as exc_info:
            extract_financial_data(request, valid_request_data)

        assert exc_info.value.status_code == 400
        assert "Validation error" in str(exc_info.value.message)

    def test_extract_financial_data_extraction_service_failure(
        self, request_factory, valid_request_data, mock_services
    ):
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        client_data = Mock()
        client_data.name = "Test Client"
        client_data.id = "client-123"
        client_data.token = "client-token"
        mock_services[
            "client_service"
        ].get_or_create_client.return_value = client_data

        mock_services[
            "extraction_service"
        ].extract_financial_data.side_effect = Exception("Extraction failed")

        # Act & Assert
        with pytest.raises(HttpError) as exc_info:
            extract_financial_data(request, valid_request_data)

        assert exc_info.value.status_code == 500
        assert "unexpected error" in str(exc_info.value.message)

    def test_extract_financial_data_with_cache_hit(
        self,
        request_factory,
        valid_request_data,
        mock_services,
        sample_formatted_response,
    ):
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        client_data = Mock()
        client_data.name = "Test Client"
        client_data.id = "client-123"
        client_data.token = "client-token"
        mock_services[
            "client_service"
        ].get_or_create_client.return_value = client_data

        from src.financial.schemas.schemas import FinancialDataResponseSchema

        cached_response = FinancialDataResponseSchema(
            **sample_formatted_response
        )
        mock_services[
            "extraction_service"
        ].extract_financial_data.return_value = cached_response

        # Act
        result = extract_financial_data(request, valid_request_data)

        # Assert
        assert isinstance(result, FinancialDataResponseSchema)
        assert result.user_document == "12345678901"

    @pytest.mark.parametrize(
        "user_document,expected_error",
        [
            ("123", "Validation error"),
            ("", "Validation error"),
            ("abc", "Validation error"),
        ],
    )
    def test_extract_financial_data_invalid_user_document(
        self, request_factory, mock_services, user_document, expected_error
    ):
        # Arrange
        request = request_factory.post("/api/v1/extract-financial-data")

        # Act & Assert
        with pytest.raises(Exception):
            invalid_data = ExtractionRequestSchema(user_document=user_document)
            extract_financial_data(request, invalid_data)


class TestHealthCheck:
    def test_health_check_success(self, request_factory):
        # Arrange
        from src.financial.controllers.extract_financial_data import (
            health_check,
        )

        request = request_factory.get("/api/v1/health")

        # Act
        with patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ):
            result = health_check(request)

        # Assert
        assert result.status in ["healthy", "degraded"]
        assert "api" in result.services

    def test_health_check_with_service_failure(self, request_factory):
        # Arrange
        from src.financial.controllers.extract_financial_data import (
            health_check,
        )

        request = request_factory.get("/api/v1/health")

        # Act
        with patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ) as mock_extraction:
            mock_extraction.side_effect = Exception("Service unavailable")
            result = health_check(request)

        # Assert
        assert result.status in ["degraded", "unhealthy"]
        assert "api" in result.services
