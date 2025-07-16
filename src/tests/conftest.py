from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from django.test import RequestFactory

from src.financial.schemas.schemas import ExtractionRequestSchema


@pytest.fixture
def mock_redis():
    redis_mock = MagicMock()
    redis_mock.set.return_value = True
    redis_mock.get.return_value = None
    redis_mock.delete.return_value = True
    return redis_mock


@pytest.fixture
def sample_account_data():
    return {
        "id": "account-123",
        "account_type": "checking",
        "account_status": "active",
        "balance": 1500.75,
    }


@pytest.fixture
def sample_balance_data():
    return {"account_id": "account-123", "balance": 1500.75, "currency": "BRL"}


@pytest.fixture
def sample_transaction_data():
    return {
        "id": "transaction-456",
        "account_id": "account-123",
        "transaction_type": "deposit",
        "transaction_status": "completed",
        "transaction_amount": 500.00,
        "transaction_direction": "in",
        "transaction_description": "Salary deposit",
        "transaction_date": "2025-01-15T10:30:00Z",
    }


@pytest.fixture
def sample_accounts_response():
    return {
        "items": [
            {
                "id": "account-123",
                "account_type": "checking",
                "account_status": "active",
            },
            {
                "id": "account-456",
                "account_type": "savings",
                "account_status": "active",
            },
        ],
        "has_next": False,
    }


@pytest.fixture
def sample_balances_response():
    return {"balance": 1500.75, "currency": "BRL"}


@pytest.fixture
def sample_transactions_response():
    return {
        "items": [
            {
                "id": "transaction-456",
                "transaction_type": "deposit",
                "transaction_status": "completed",
                "transaction_amount": 500.00,
                "transaction_direction": "in",
                "transaction_description": "Salary deposit",
                "transaction_date": "2025-01-15T10:30:00Z",
            }
        ],
        "has_next": False,
    }


@pytest.fixture
def sample_client_response():
    return {
        "client_id": "client-789",
        "client_secret": "secret-xyz",
        "client_name": "Test Client",
        "expires_at": "2025-12-31T23:59:59Z",
    }


@pytest.fixture
def sample_consent_response():
    return {
        "consent_id": "consent-abc",
        "token": "token-def",
        "status": "active",
        "expires_at": "2025-12-31T23:59:59Z",
    }


@pytest.fixture
def mock_http_response():
    def _create_response(json_data, status_code=200):
        response = Mock()
        response.json.return_value = json_data
        response.status_code = status_code
        response.ok = status_code < 400
        return response

    return _create_response


@pytest.fixture
def sample_formatted_response():
    return {
        "user_document": "12345678901",
        "extraction_date": datetime.now().isoformat(),
        "accounts": [
            {
                "account_id": "account-123",
                "account_type": "CHECKING",
                "account_status": "ACTIVE",
                "balance": {"amount": 1500.75, "currency": "BRL"},
                "transactions": [
                    {
                        "transaction_id": "transaction-456",
                        "transaction_type": "DEPOSIT",
                        "transaction_status": "COMPLETED",
                        "amount": 500.00,
                        "currency": "BRL",
                        "direction": "IN",
                        "description": "Salary deposit",
                        "date": datetime.now().isoformat(),
                    }
                ],
            }
        ],
        "summary": {
            "total_accounts": 1,
            "total_transactions": 1,
            "processing_time_ms": 1500,
            "errors": [],
        },
    }


@pytest.fixture
def cache_test_data():
    return {
        "key": "test_key",
        "data": {"test": "data", "number": 123},
        "timeout": 300,
    }


@pytest.fixture
def mock_django_cache(monkeypatch):
    cache_mock = MagicMock()
    monkeypatch.setattr("django.core.cache.cache", cache_mock)
    return cache_mock


@pytest.fixture
def mock_settings(monkeypatch):
    settings_mock = MagicMock()
    settings_mock.CACHE_DEFAULT_TIMEOUT = 300
    settings_mock.OFDA_API_BASE_URL = "http://test-api.com"
    settings_mock.OFDA_API_TIMEOUT = 30
    settings_mock.OFDA_API_RETRY_ATTEMPTS = 3
    monkeypatch.setattr("django.conf.settings", settings_mock)
    return settings_mock


# Fixtures moved from test files
@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def valid_request_data():
    return ExtractionRequestSchema(user_document="12345678901")


@pytest.fixture
def mock_dependencies():
    with (
        patch(
            "src.financial.services.extraction_service.ConsentService"
        ) as mock_consent,
        patch(
            "src.financial.services.extraction_service.RouterService"
        ) as mock_router,
        patch(
            "src.financial.services.extraction_service.CacheService"
        ) as mock_cache,
    ):
        mock_consent_instance = Mock()
        mock_router_instance = Mock()
        mock_cache_instance = Mock()

        mock_consent.return_value = mock_consent_instance
        mock_router.return_value = mock_router_instance
        mock_cache.return_value = mock_cache_instance

        yield {
            "consent": mock_consent_instance,
            "router": mock_router_instance,
            "cache": mock_cache_instance,
        }


@pytest.fixture
def extraction_service(mock_dependencies):
    from src.financial.services.extraction_service import ExtractionService

    return ExtractionService()


@pytest.fixture
def mock_services():
    with (
        patch(
            "src.financial.controllers.extract_financial_data.DynamicClientService"
        ) as mock_client_service,
        patch(
            "src.financial.controllers.extract_financial_data.ExtractionService"
        ) as mock_extraction_service,
    ):
        mock_client_instance = Mock()
        mock_extraction_instance = Mock()

        mock_client_service.return_value = mock_client_instance
        mock_extraction_service.return_value = mock_extraction_instance

        yield {
            "client_service": mock_client_instance,
            "extraction_service": mock_extraction_instance,
        }


# Route testing fixtures
@pytest.fixture
def mock_route_data():
    return {
        "token": "test-token",
        "account_id": "account-123",
        "user_document": "12345678901",
        "page": 1,
        "limit": 10,
    }


@pytest.fixture
def mock_client_data():
    return {
        "name": "Test Client",
        "organization_name": "Test Org",
        "organization_id": "org-123",
        "organization_type": "INDIVIDUAL",
        "operation": "POST",
    }
