from datetime import datetime
from typing import Any


class Schema:
    pass


class ExtractionResult(Schema):
    success: bool
    user_document: str
    extraction_date: datetime
    accounts: list[dict[str, Any]]
    balances: list[dict[str, Any]]
    transactions: list[dict[str, Any]]
    summary: dict[str, Any]
    errors: list[str]
    processing_time_ms: int
