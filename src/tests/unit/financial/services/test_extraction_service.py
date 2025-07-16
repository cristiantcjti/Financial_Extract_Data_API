import pytest
from unittest.mock import Mock
from datetime import datetime

from src.financial.services.extraction_service import ExtractionService
from src.financial.schemas.schemas import FinancialDataResponseSchema


class TestExtractionService:

    def test_extract_financial_data_cache_hit(self, extraction_service, mock_dependencies, sample_formatted_response):
        # Arrange
        mock_dependencies['cache'].get_cached_data.return_value = sample_formatted_response
        
        # Act
        result = extraction_service.extract_financial_data("12345678901", "client_id", "token")
        
        # Assert
        assert isinstance(result, FinancialDataResponseSchema)
        assert result.user_document == "12345678901"
        mock_dependencies['cache'].get_cached_data.assert_called_once_with("extraction", "12345678901")

    def test_extract_financial_data_cache_miss_success(
        self, 
        extraction_service, 
        mock_dependencies,
        sample_client_response,
        sample_consent_response,
        sample_accounts_response,
        sample_balances_response, 
        sample_transactions_response
    ):
        # Arrange
        mock_dependencies['cache'].get_cached_data.return_value = None
        
        consent_data = Mock()
        consent_data.id = "consent-123"
        consent_data.token = "consent-token"
        mock_dependencies['consent'].get_or_create_consent.return_value = consent_data
        
        # Mock successful router responses
        accounts_result = Mock()
        accounts_result.success = True
        accounts_result.response.json.return_value = sample_accounts_response
        
        balances_result = Mock()
        balances_result.success = True
        balances_result.response.json.return_value = sample_balances_response
        
        transactions_result = Mock()
        transactions_result.success = True
        transactions_result.response.json.return_value = sample_transactions_response
        
        mock_dependencies['router'].router_process.side_effect = [
            accounts_result,
            balances_result,  # balance for account-123
            balances_result,  # balance for account-456
            transactions_result,  # transactions for account-123
            transactions_result   # transactions for account-456
        ]
        
        mock_dependencies['cache'].cache_data.return_value = True
        
        # Act
        result = extraction_service.extract_financial_data("12345678901", "client_id", "token")
        
        # Assert
        assert isinstance(result, FinancialDataResponseSchema)
        assert result.user_document == "12345678901"
        assert len(result.accounts) > 0
        mock_dependencies['cache'].cache_data.assert_called_once()

    def test_extract_financial_data_consent_failure(self, extraction_service, mock_dependencies):
        # Arrange
        mock_dependencies['cache'].get_cached_data.return_value = None
        mock_dependencies['consent'].get_or_create_consent.side_effect = Exception("Consent failed")
        
        # Act
        result = extraction_service.extract_financial_data("12345678901", "client_id", "token")
        
        # Assert
        assert isinstance(result, FinancialDataResponseSchema)
        assert result.user_document == "12345678901"
        assert len(result.accounts) == 0
        assert len(result.summary.errors) > 0

    def test_extract_accounts_success(self, extraction_service, mock_dependencies, sample_accounts_response):
        # Arrange
        consent_data = Mock()
        consent_data.token = "consent-token"
        
        successful_result = Mock()
        successful_result.success = True
        successful_result.response.json.return_value = sample_accounts_response
        mock_dependencies['router'].router_process.return_value = successful_result
        
        # Act
        result = extraction_service._extract_accounts("12345678901", consent_data)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "account-123"

    def test_extract_balances_success(self, extraction_service, mock_dependencies, sample_balances_response):
        # Arrange
        consent_data = Mock()
        consent_data.token = "consent-token"
        accounts = [{"id": "account-123"}]
        
        successful_result = Mock()
        successful_result.success = True
        successful_result.response.json.return_value = sample_balances_response
        mock_dependencies['router'].router_process.return_value = successful_result
        
        # Act
        result = extraction_service._extract_balances("12345678901", consent_data, accounts)
        
        # Assert
        assert len(result) == 1
        assert result[0]["account_id"] == "account-123"
        assert result[0]["balance"]["amount"] == 1500.75

    def test_extract_transactions_success(self, extraction_service, mock_dependencies, sample_transactions_response):
        # Arrange
        consent_data = Mock()
        consent_data.token = "consent-token"
        accounts = [{"id": "account-123"}]
        
        successful_result = Mock()
        successful_result.success = True
        successful_result.response.json.return_value = sample_transactions_response
        mock_dependencies['router'].router_process.return_value = successful_result
        
        # Act
        result = extraction_service._extract_transactions("12345678901", consent_data, accounts)
        
        # Assert
        assert len(result) == 1
        assert result[0]["account_id"] == "account-123"
        assert result[0]["transaction_id"] == "transaction-456"

    def test_fetch_paginated_data_single_page(self, extraction_service, mock_dependencies, sample_accounts_response):
        # Arrange
        from src.financial.routes.accounts import AccountsRoute
        
        successful_result = Mock()
        successful_result.success = True
        successful_result.response.json.return_value = sample_accounts_response
        mock_dependencies['router'].router_process.return_value = successful_result
        
        # Act
        result = extraction_service._fetch_paginated_data(AccountsRoute, {"token": "test"})
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "account-123"

    def test_fetch_paginated_data_multiple_pages(self, extraction_service, mock_dependencies):
        # Arrange
        from src.financial.routes.accounts import AccountsRoute
        
        page1_response = {
            "items": [{"id": "account-1"}],
            "has_next": True
        }
        page2_response = {
            "items": [{"id": "account-2"}],
            "has_next": False
        }
        
        successful_result = Mock()
        successful_result.success = True
        successful_result.response.json.side_effect = [page1_response, page2_response]
        mock_dependencies['router'].router_process.return_value = successful_result
        
        # Act
        result = extraction_service._fetch_paginated_data(AccountsRoute, {"token": "test"})
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "account-1"
        assert result[1]["id"] == "account-2"

    def test_create_formatted_response(self, extraction_service):
        # Arrange
        user_document = "12345678901"
        extraction_date = datetime.now()
        accounts = [{"id": "account-123", "account_type": "checking", "account_status": "active"}]
        balances = [{"account_id": "account-123", "balance": {"amount": 1500.75, "currency": "BRL"}}]
        transactions = [
            {
                "account_id": "account-123",
                "transaction_id": "transaction-456",
                "transaction_type": "deposit",
                "transaction_status": "completed",
                "amount": 500.00,
                "currency": "BRL",
                "direction": "in",
                "description": "Test transaction",
                "date": "2025-01-15T10:30:00Z"
            }
        ]
        
        # Act
        result = extraction_service._create_formatted_response(
            user_document, extraction_date, accounts, balances, transactions, 1500, []
        )
        
        # Assert
        assert isinstance(result, FinancialDataResponseSchema)
        assert result.user_document == user_document
        assert len(result.accounts) == 1
        assert result.summary.total_accounts == 1
        assert result.summary.total_transactions == 1