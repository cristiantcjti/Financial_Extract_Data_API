import pytest
from datetime import datetime
from pydantic import ValidationError

from src.financial.schemas.schemas import (
    ExtractionRequestSchema,
    TransactionSchema,
    BalanceSchema,
    AccountSchema,
    SummarySchema,
    FinancialDataResponseSchema
)


class TestExtractionRequestSchema:

    def test_valid_request(self):
        # Arrange
        valid_data = {"user_document": "12345678901"}
        
        # Act
        request = ExtractionRequestSchema(**valid_data)
        
        # Assert
        assert request.user_document == "12345678901"

    def test_invalid_short_document(self):
        # Arrange
        invalid_data = {"user_document": "123"}
        
        # Act & Assert
        with pytest.raises(ValidationError):
            ExtractionRequestSchema(**invalid_data)


class TestTransactionSchema:

    def test_valid_transaction(self):
        # Arrange
        valid_data = {
            "transaction_id": "trans-123",
            "transaction_type": "DEPOSIT",
            "transaction_status": "COMPLETED",
            "amount": 100.50,
            "currency": "BRL",
            "direction": "IN",
            "description": "Test transaction",
            "date": datetime.now()
        }
        
        # Act
        transaction = TransactionSchema(**valid_data)
        
        # Assert
        assert transaction.transaction_id == "trans-123"
        assert transaction.amount == 100.50

    def test_transaction_model_dump(self):
        # Arrange
        transaction_data = {
            "transaction_id": "trans-123",
            "transaction_type": "DEPOSIT",
            "transaction_status": "COMPLETED",
            "amount": 100.50,
            "currency": "BRL",
            "direction": "IN",
            "description": "Test transaction",
            "date": datetime(2025, 1, 15, 10, 30, 0)
        }
        transaction = TransactionSchema(**transaction_data)
        
        # Act
        dumped = transaction.model_dump()
        
        # Assert
        assert isinstance(dumped, dict)
        assert dumped["transaction_id"] == "trans-123"
        assert dumped["amount"] == 100.50


class TestBalanceSchema:

    def test_valid_balance(self):
        # Arrange
        valid_data = {
            "amount": 1500.75,
            "currency": "BRL"
        }
        
        # Act
        balance = BalanceSchema(**valid_data)
        
        # Assert
        assert balance.amount == 1500.75
        assert balance.currency == "BRL"


class TestAccountSchema:

    def test_valid_account(self, sample_balance_data, sample_transaction_data):
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"]
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data["transaction_status"],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now()
        }
        transaction = TransactionSchema(**transaction_data)
        
        valid_data = {
            "account_id": "account-123",
            "account_type": "CHECKING",
            "account_status": "ACTIVE",
            "balance": balance,
            "transactions": [transaction]
        }
        
        # Act
        account = AccountSchema(**valid_data)
        
        # Assert
        assert account.account_id == "account-123"
        assert len(account.transactions) == 1

    def test_account_model_dump(self, sample_balance_data, sample_transaction_data):
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"]
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data["transaction_status"],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now()
        }
        transaction = TransactionSchema(**transaction_data)
        
        account_data = {
            "account_id": "account-123",
            "account_type": "CHECKING",
            "account_status": "ACTIVE",
            "balance": balance,
            "transactions": [transaction]
        }
        account = AccountSchema(**account_data)
        
        # Act
        dumped = account.model_dump()
        
        # Assert
        assert isinstance(dumped, dict)
        assert dumped["account_id"] == "account-123"
        assert isinstance(dumped["balance"], dict)
        assert isinstance(dumped["transactions"], list)


class TestSummarySchema:

    def test_valid_summary(self):
        # Arrange
        valid_data = {
            "total_accounts": 2,
            "total_transactions": 10,
            "processing_time_ms": 1500,
            "errors": []
        }
        
        # Act
        summary = SummarySchema(**valid_data)
        
        # Assert
        assert summary.total_accounts == 2
        assert summary.total_transactions == 10
        assert summary.processing_time_ms == 1500
        assert len(summary.errors) == 0

    def test_summary_with_errors(self):
        # Arrange
        valid_data = {
            "total_accounts": 0,
            "total_transactions": 0,
            "processing_time_ms": 500,
            "errors": ["Connection failed", "Timeout error"]
        }
        
        # Act
        summary = SummarySchema(**valid_data)
        
        # Assert
        assert len(summary.errors) == 2


class TestFinancialDataResponseSchema:

    def test_valid_response(self, sample_balance_data, sample_transaction_data):
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"]
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data["transaction_status"],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now()
        }
        transaction = TransactionSchema(**transaction_data)
        account = AccountSchema(
            account_id="account-123",
            account_type="CHECKING",
            account_status="ACTIVE",
            balance=balance,
            transactions=[transaction]
        )
        summary = SummarySchema(
            total_accounts=1,
            total_transactions=1,
            processing_time_ms=1500,
            errors=[]
        )
        
        valid_data = {
            "user_document": "12345678901",
            "extraction_date": datetime.now(),
            "accounts": [account],
            "summary": summary
        }
        
        # Act
        response = FinancialDataResponseSchema(**valid_data)
        
        # Assert
        assert response.user_document == "12345678901"
        assert len(response.accounts) == 1
        assert response.summary.total_accounts == 1

    def test_response_model_dump(self, sample_balance_data, sample_transaction_data):
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"]
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data["transaction_status"],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now()
        }
        transaction = TransactionSchema(**transaction_data)
        account = AccountSchema(
            account_id="account-123",
            account_type="CHECKING", 
            account_status="ACTIVE",
            balance=balance,
            transactions=[transaction]
        )
        summary = SummarySchema(
            total_accounts=1,
            total_transactions=1,
            processing_time_ms=1500,
            errors=[]
        )
        
        response_data = {
            "user_document": "12345678901",
            "extraction_date": datetime.now(),
            "accounts": [account],
            "summary": summary
        }
        response = FinancialDataResponseSchema(**response_data)
        
        # Act
        dumped = response.model_dump()
        
        # Assert
        assert isinstance(dumped, dict)
        assert dumped["user_document"] == "12345678901"
        assert isinstance(dumped["accounts"], list)
        assert isinstance(dumped["summary"], dict)
        assert len(dumped["accounts"]) == 1

    def test_empty_response(self):
        # Arrange
        summary = SummarySchema(
            total_accounts=0,
            total_transactions=0,
            processing_time_ms=100,
            errors=["No data found"]
        )
        
        valid_data = {
            "user_document": "12345678901",
            "extraction_date": datetime.now(),
            "accounts": [],
            "summary": summary
        }
        
        # Act
        response = FinancialDataResponseSchema(**valid_data)
        
        # Assert
        assert response.user_document == "12345678901"
        assert len(response.accounts) == 0
        assert len(response.summary.errors) == 1