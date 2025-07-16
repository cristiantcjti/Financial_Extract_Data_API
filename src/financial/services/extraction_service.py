from datetime import datetime
from typing import Any

from src.config.logging import logger
from src.core.services.cache_service import CacheService
from src.financial.routes.accounts import AccountsRoute
from src.financial.routes.balances import BalancesRoute
from src.financial.routes.transactions import TransactionsRoute
from src.financial.schemas.schemas import (
    AccountSchema,
    BalanceSchema,
    FinancialDataResponseSchema,
    SummarySchema,
    TransactionSchema,
)
from src.financial.services.consent_service import ConsentData, ConsentService
from src.integration.enums import RouteMethod
from src.integration.services.router_service import RouterService


class ExtractionService:
    def __init__(self) -> None:
        self.logger = logger
        self.consent_service = ConsentService()
        self.router_service = RouterService()
        self.cache_service = CacheService()

    def extract_financial_data(
        self, user_document: str, dynamic_client_id: str, dynamic_token: str
    ) -> FinancialDataResponseSchema:
        start_time = datetime.now()
        extraction_errors = []

        cached_data = self.cache_service.get_cached_data(
            "extraction", user_document
        )
        if cached_data:
            self.logger.info(
                f"Returning cached financial data for user_document: {user_document}"
            )
            return FinancialDataResponseSchema(**cached_data)

        try:
            self.logger.info(
                f"Starting financial data extraction for user_document: {user_document}"
            )
            consent_data = self._get_or_create_consent(
                user_document=user_document,
                dynamic_client_id=dynamic_client_id,
                token=dynamic_token,
            )
            self.logger.info(f"Consent obtained: {consent_data.id}")

            accounts_data = self._extract_accounts(user_document, consent_data)
            self.logger.info(f"Accounts extracted: {len(accounts_data)}")

            balances_data = self._extract_balances(
                user_document, consent_data, accounts_data
            )
            self.logger.info(f"Balances extracted: {len(balances_data)}")

            transactions_data = self._extract_transactions(
                user_document, consent_data, accounts_data
            )
            self.logger.info(
                f"Transactions extracted: {len(transactions_data)}"
            )

            processing_time = (
                datetime.now() - start_time
            ).total_seconds() * 1000
            formatted_response = self._create_formatted_response(
                user_document=user_document,
                extraction_date=start_time,
                accounts=accounts_data,
                balances=balances_data,
                transactions=transactions_data,
                processing_time_ms=int(processing_time),
                errors=extraction_errors,
            )

            self.logger.info(
                f"Financial data extraction completed successfully for user_document: {user_document}"
            )

            self.cache_service.cache_data(
                "extraction", user_document, formatted_response.model_dump()
            )

            return formatted_response

        except Exception as e:
            processing_time = (
                datetime.now() - start_time
            ).total_seconds() * 1000
            error_message = f"Financial data extraction failed: {str(e)}"
            extraction_errors.append(error_message)

            self.logger.error(
                f"Error in financial data extraction for user_document: {user_document}, Error: {str(e)}"
            )

            # Create empty response schema for error case
            summary = SummarySchema(
                total_accounts=0,
                total_transactions=0,
                processing_time_ms=int(processing_time),
                errors=extraction_errors,
            )

            return FinancialDataResponseSchema(
                user_document=user_document,
                extraction_date=start_time,
                accounts=[],
                summary=summary,
            )

    def _get_or_create_consent(
        self, user_document: str, dynamic_client_id: str, token: str
    ) -> ConsentData:
        try:
            return self.consent_service.get_or_create_consent(
                user_document=user_document,
                client_id=dynamic_client_id,
                token=token,
            )
        except Exception as e:
            # self.logger.error(f"Error getting/creating consent for user_document: {user_document}, Error: {str(e)}")
            raise ValueError(f"Failed to obtain consent: {str(e)}") from e

    def _fetch_paginated_data(
        self,
        route_class: type,
        route_data: dict[str, Any],
        data_key: str = "items",
    ) -> list[dict[str, Any]]:
        all_items = []
        page = 1
        has_next = True
        retry_count = 0

        while has_next:
            try:
                route_data["page"] = page
                route = route_class(data=route_data)

                result = self.router_service.router_process(route)
                if not result.success:
                    self.logger.warning(
                        f"Paginated data extraction failed on page {page}, attempt {retry_count + 1}"
                    )
                    retry_count += 1
                    continue

                response_json = result.response.json()

                if data_key in response_json:
                    page_items = response_json[data_key]
                    all_items.extend(page_items)
                    has_next = response_json.get("has_next", False)
                    self.logger.debug(
                        f"Fetched page {page} with {len(page_items)} items, has_next: {has_next}"
                    )
                else:
                    all_items.append(response_json)
                    has_next = False
                    self.logger.debug(
                        f"Fetched single item response on page {page}"
                    )

            except Exception as e:
                self.logger.warning(f"Error fetching page {page}: {str(e)}")

            page += 1
            if page > 100:
                self.logger.warning(
                    "Reached maximum page limit (100) to prevent infinite loop"
                )
                break

        self.logger.info(
            f"Successfully fetched {len(all_items)} total items across {page - 1} pages"
        )
        return all_items

    def _extract_accounts(
        self, user_document: str, consent_data: ConsentData
    ) -> list[dict[str, Any]]:
        try:
            route_data = {
                "token": consent_data.token,
                "operation": RouteMethod.GET,
            }

            accounts = self._fetch_paginated_data(
                AccountsRoute, route_data, "items"
            )

            if not accounts:
                raise ValueError("Accounts extraction failed")

            return accounts

        except Exception as e:
            self.logger.error(
                f"Error extracting accounts for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(f"Failed to extract accounts: {str(e)}") from e

    def _extract_balances(
        self,
        user_document: str,
        consent_data: ConsentData,
        accounts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        try:
            balances = []
            for account in accounts:
                route = BalancesRoute(
                    data={
                        "token": consent_data.token,
                        "account_id": account["id"],
                        "operation": RouteMethod.GET,
                    }
                )

                result = self.router_service.router_process(route)

                if not result.success:
                    raise ValueError("Balances extraction failed")

                response_json = result.response.json()
                balances.append(
                    {
                        "account_id": account["id"],
                        "balance": {
                            "amount": response_json["balance"],
                            "currency": response_json["currency"],
                        },
                    }
                )

            return balances

        except Exception as e:
            self.logger.error(
                f"Error extracting balances for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(f"Failed to extract balances: {str(e)}") from e

    def _extract_transactions(
        self,
        user_document: str,
        consent_data: ConsentData,
        accounts: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        try:
            all_transactions = []
            for account in accounts:
                route_data = {
                    "token": consent_data.token,
                    "account_id": account["id"],
                    "operation": RouteMethod.GET,
                }

                account_transactions = self._fetch_paginated_data(
                    TransactionsRoute, route_data, "items"
                )

                if not account_transactions:
                    raise ValueError("Transactions extraction failed")

                for transaction in account_transactions:
                    all_transactions.append(
                        {
                            "account_id": account["id"],
                            "transaction_id": transaction["id"],
                            "transaction_type": transaction[
                                "transaction_type"
                            ],
                            "transaction_status": transaction[
                                "transaction_status"
                            ],
                            "amount": transaction["transaction_amount"],
                            "currency": "",
                            "direction": transaction["transaction_direction"],
                            "description": transaction[
                                "transaction_description"
                            ],
                            "date": transaction["transaction_date"],
                        }
                    )

                self.logger.info(
                    f"Extracted {len(account_transactions)} transactions for account {account['id']}"
                )

            return all_transactions

        except Exception as e:
            self.logger.error(
                f"Error extracting transactions for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(
                f"Failed to extract transactions: {str(e)}"
            ) from e

    def _create_formatted_response(
        self,
        user_document: str,
        extraction_date: datetime,
        accounts: list[dict[str, Any]],
        balances: list[dict[str, Any]],
        transactions: list[dict[str, Any]],
        processing_time_ms: int,
        errors: list[str],
    ) -> FinancialDataResponseSchema:
        balance_lookup = {
            balance["account_id"]: balance["balance"] for balance in balances
        }

        transactions_by_account = {}
        for transaction in transactions:
            account_id = transaction["account_id"]
            if account_id not in transactions_by_account:
                transactions_by_account[account_id] = []
            currency = balance_lookup.get(account_id, {}).get(
                "currency", "BRL"
            )

            formatted_transaction = {
                "transaction_id": transaction["transaction_id"],
                "transaction_type": transaction["transaction_type"].upper(),
                "transaction_status": transaction[
                    "transaction_status"
                ].upper(),
                "amount": transaction["amount"],
                "currency": currency,
                "direction": transaction["direction"].upper(),
                "description": transaction["description"],
                "date": transaction["date"],
            }
            transactions_by_account[account_id].append(formatted_transaction)

        # Build formatted accounts using the conversion helper
        formatted_accounts = []
        for account in accounts:
            account_id = account["id"]
            account_balance = balance_lookup.get(
                account_id, {"amount": 0.0, "currency": "BRL"}
            )
            account_transactions = transactions_by_account.get(account_id, [])

            # Prepare account data for conversion
            account_data = {
                "account_id": account_id,
                "account_type": account.get("account_type", "UNKNOWN").upper(),
                "account_status": account.get(
                    "account_status", "UNKNOWN"
                ).upper(),
                "balance": account_balance,
                "transactions": account_transactions,
            }
            account_schema = self._convert_account_data(account_data)
            formatted_accounts.append(account_schema)

        total_transactions = sum(
            len(account_transactions)
            for account_transactions in transactions_by_account.values()
        )

        # Create summary schema
        summary = SummarySchema(
            total_accounts=len(accounts),
            total_transactions=total_transactions,
            processing_time_ms=processing_time_ms,
            errors=errors,
        )

        return FinancialDataResponseSchema(
            user_document=user_document,
            extraction_date=extraction_date,
            accounts=formatted_accounts,
            summary=summary,
        )

    def _convert_account_data(
        self, account_data: dict[str, Any]
    ) -> AccountSchema:
        balance_data = account_data.get("balance", {})
        balance = BalanceSchema(
            amount=balance_data.get("amount", 0.0),
            currency=balance_data.get("currency", "BRL"),
        )

        # Convert transactions data
        transactions = []
        for transaction_data in account_data.get("transactions", []):
            transaction = self._convert_transaction_data(transaction_data)
            transactions.append(transaction)

        return AccountSchema(
            account_id=account_data.get("account_id", ""),
            account_type=account_data.get("account_type", ""),
            account_status=account_data.get("account_status", ""),
            balance=balance,
            transactions=transactions,
        )

    def _convert_transaction_data(
        self, transaction_data: dict[str, Any]
    ) -> TransactionSchema:
        # Parse date if it's a string
        date = transaction_data.get("date")
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date.replace("Z", "+00:00"))
            except ValueError:
                date = datetime.now()
        elif not isinstance(date, datetime):
            date = datetime.now()

        return TransactionSchema(
            transaction_id=transaction_data.get("transaction_id", ""),
            transaction_type=transaction_data.get("transaction_type", ""),
            transaction_status=transaction_data.get("transaction_status", ""),
            amount=transaction_data.get("amount", 0.0),
            currency=transaction_data.get("currency", "BRL"),
            direction=transaction_data.get("direction", ""),
            description=transaction_data.get("description", ""),
            date=date,
        )
