from datetime import datetime
from typing import Any

import pytest
from pydantic import ValidationError

from src.financial.schemas.schemas import (
    AccountSchema,
    BalanceSchema,
    ExtractionRequestSchema,
    FinancialDataResponseSchema,
    SummarySchema,
    TransactionSchema,
)


class TestExtractionRequestSchema:
    def test_valid_request(self) -> None:
        # Arrange
        valid_data = {"user_document": "12345678901"}

        # Act
        request = ExtractionRequestSchema(**valid_data)

        # Assert
        assert request.user_document == "12345678901"  # noqa: S101

    def test_invalid_short_document(self) -> None:
        # Arrange
        invalid_data = {"user_document": "123"}

        # Act & Assert
        with pytest.raises(ValidationError):
            ExtractionRequestSchema(**invalid_data)


class TestTransactionSchema:
    def test_valid_transaction(self) -> None:
        # Arrange
        valid_data = {
            "transaction_id": "trans-123",
            "transaction_type": "DEPOSIT",
            "transaction_status": "COMPLETED",
            "amount": 100.50,
            "currency": "BRL",
            "direction": "IN",
            "description": "Test transaction",
            "date": datetime.now(),
        }

        # Act
        transaction = TransactionSchema(**valid_data)

        # Assert
        assert transaction.transaction_id == "trans-123"  # noqa: S101
        assert transaction.amount == 100.50  # noqa: S101

    def test_transaction_model_dump(self) -> None:
        # Arrange
        transaction_data = {
            "transaction_id": "trans-123",
            "transaction_type": "DEPOSIT",
            "transaction_status": "COMPLETED",
            "amount": 100.50,
            "currency": "BRL",
            "direction": "IN",
            "description": "Test transaction",
            "date": datetime(2025, 1, 15, 10, 30, 0),
        }
        transaction = TransactionSchema(**transaction_data)

        # Act
        dumped = transaction.model_dump()

        # Assert
        assert isinstance(dumped, dict)  # noqa: S101
        assert dumped["transaction_id"] == "trans-123"  # noqa: S101
        assert dumped["amount"] == 100.50  # noqa: S101


class TestBalanceSchema:
    def test_valid_balance(self) -> None:
        # Arrange
        valid_data = {"amount": 1500.75, "currency": "BRL"}

        # Act
        balance = BalanceSchema(**valid_data)

        # Assert
        assert balance.amount == 1500.75  # noqa: S101
        assert balance.currency == "BRL"  # noqa: S101


class TestAccountSchema:
    def test_valid_account(
        self,
        sample_balance_data: dict[str, Any],
        sample_transaction_data: dict[str, Any],
    ) -> None:
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"],
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data[
                "transaction_status"
            ],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now(),
        }
        transaction = TransactionSchema(**transaction_data)

        valid_data = {
            "account_id": "account-123",
            "account_type": "CHECKING",
            "account_status": "ACTIVE",
            "balance": balance,
            "transactions": [transaction],
        }

        # Act
        account = AccountSchema(**valid_data)

        # Assert
        assert account.account_id == "account-123"  # noqa: S101
        assert len(account.transactions) == 1  # noqa: S101

    def test_account_model_dump(
        self,
        sample_balance_data: dict[str, Any],
        sample_transaction_data: dict[str, Any],
    ) -> None:
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"],
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data[
                "transaction_status"
            ],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now(),
        }
        transaction = TransactionSchema(**transaction_data)

        account_data = {
            "account_id": "account-123",
            "account_type": "CHECKING",
            "account_status": "ACTIVE",
            "balance": balance,
            "transactions": [transaction],
        }
        account = AccountSchema(**account_data)

        # Act
        dumped = account.model_dump()

        # Assert
        assert isinstance(dumped, dict)  # noqa: S101
        assert dumped["account_id"] == "account-123"  # noqa: S101
        assert isinstance(dumped["balance"], dict)  # noqa: S101
        assert isinstance(dumped["transactions"], list)  # noqa: S101


class TestSummarySchema:
    def test_valid_summary(self) -> None:
        # Arrange
        valid_data = {
            "total_accounts": 2,
            "total_transactions": 10,
            "processing_time_ms": 1500,
            "errors": [],
        }

        # Act
        summary = SummarySchema(**valid_data)

        # Assert
        assert summary.total_accounts == 2  # noqa: S101
        assert summary.total_transactions == 10  # noqa: S101
        assert summary.processing_time_ms == 1500  # noqa: S101
        assert len(summary.errors) == 0  # noqa: S101

    def test_summary_with_errors(self) -> None:
        # Arrange
        valid_data = {
            "total_accounts": 0,
            "total_transactions": 0,
            "processing_time_ms": 500,
            "errors": ["Connection failed", "Timeout error"],
        }

        # Act
        summary = SummarySchema(**valid_data)

        # Assert
        assert len(summary.errors) == 2  # noqa: S101


class TestFinancialDataResponseSchema:
    def test_valid_response(
        self,
        sample_balance_data: dict[str, Any],
        sample_transaction_data: dict[str, Any],
    ) -> None:
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"],
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data[
                "transaction_status"
            ],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now(),
        }
        transaction = TransactionSchema(**transaction_data)
        account = AccountSchema(
            account_id="account-123",
            account_type="CHECKING",
            account_status="ACTIVE",
            balance=balance,
            transactions=[transaction],
        )
        summary = SummarySchema(
            total_accounts=1,
            total_transactions=1,
            processing_time_ms=1500,
            errors=[],
        )

        valid_data = {
            "user_document": "12345678901",
            "extraction_date": datetime.now(),
            "accounts": [account],
            "summary": summary,
        }

        # Act
        response = FinancialDataResponseSchema(**valid_data)

        # Assert
        assert response.user_document == "12345678901"  # noqa: S101
        assert len(response.accounts) == 1  # noqa: S101
        assert response.summary.total_accounts == 1  # noqa: S101

    def test_response_model_dump(
        self,
        sample_balance_data: dict[str, Any],
        sample_transaction_data: dict[str, Any],
    ) -> None:
        # Arrange
        balance_data = {
            "amount": sample_balance_data["balance"],
            "currency": sample_balance_data["currency"],
        }
        balance = BalanceSchema(**balance_data)
        transaction_data = {
            "transaction_id": sample_transaction_data["id"],
            "transaction_type": sample_transaction_data["transaction_type"],
            "transaction_status": sample_transaction_data[
                "transaction_status"
            ],
            "amount": sample_transaction_data["transaction_amount"],
            "currency": "BRL",
            "direction": sample_transaction_data["transaction_direction"],
            "description": sample_transaction_data["transaction_description"],
            "date": datetime.now(),
        }
        transaction = TransactionSchema(**transaction_data)
        account = AccountSchema(
            account_id="account-123",
            account_type="CHECKING",
            account_status="ACTIVE",
            balance=balance,
            transactions=[transaction],
        )
        summary = SummarySchema(
            total_accounts=1,
            total_transactions=1,
            processing_time_ms=1500,
            errors=[],
        )

        response_data = {
            "user_document": "12345678901",
            "extraction_date": datetime.now(),
            "accounts": [account],
            "summary": summary,
        }
        response = FinancialDataResponseSchema(**response_data)

        # Act
        dumped = response.model_dump()

        # Assert
        assert isinstance(dumped, dict)  # noqa: S101
        assert dumped["user_document"] == "12345678901"  # noqa: S101
        assert isinstance(dumped["accounts"], list)  # noqa: S101
        assert isinstance(dumped["summary"], dict)  # noqa: S101
        assert len(dumped["accounts"]) == 1  # noqa: S101

    def test_empty_response(self) -> None:
        # Arrange
        summary = SummarySchema(
            total_accounts=0,
            total_transactions=0,
            processing_time_ms=100,
            errors=["No data found"],
        )

        valid_data = {
            "user_document": "12345678901",
            "extraction_date": datetime.now(),
            "accounts": [],
            "summary": summary,
        }

        # Act
        response = FinancialDataResponseSchema(**valid_data)

        # Assert
        assert response.user_document == "12345678901"  # noqa: S101
        assert len(response.accounts) == 0  # noqa: S101
        assert len(response.summary.errors) == 1  # noqa: S101
