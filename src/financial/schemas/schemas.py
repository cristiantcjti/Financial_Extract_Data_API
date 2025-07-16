from datetime import datetime

from ninja import Schema, Field


class ExtractionRequestSchema(Schema):
    user_document: str = Field(..., min_length=11, description="User document must be at least 11 characters")


class TransactionSchema(Schema):
    transaction_id: str
    transaction_type: str
    transaction_status: str
    amount: float
    currency: str
    direction: str
    description: str
    date: datetime


class BalanceSchema(Schema):
    amount: float
    currency: str


class AccountSchema(Schema):
    account_id: str
    account_type: str
    account_status: str
    balance: BalanceSchema
    transactions: list[TransactionSchema]


class SummarySchema(Schema):
    total_accounts: int
    total_transactions: int
    processing_time_ms: int
    errors: list[str]


class FinancialDataResponseSchema(Schema):
    user_document: str
    extraction_date: datetime
    accounts: list[AccountSchema]
    summary: SummarySchema


class ErrorResponseSchema(Schema):
    error_code: str
    error_message: str
    details: str = None


class HealthCheckSchema(Schema):
    status: str
    timestamp: datetime | None = None
    services: dict


class ExtractionHistorySchema(Schema):
    extraction_id: str
    user_document: str
    extraction_date: datetime
    status: str
    total_accounts: int
    total_transactions: int


class StatsSchema(Schema):
    total_extractions: int
    successful_extractions: int
    failed_extractions: int
    average_processing_time_ms: float
    last_extraction_date: datetime | None = None
