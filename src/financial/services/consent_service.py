from src.config.logging import logger
from src.financial.routes.consent import ConsentRoute
from src.financial.services.dtos.consent import ConsentData
from src.integration.enums import RouteMethod
from src.integration.services.router_service import RouterService


class ConsentService:
    def __init__(self) -> None:
        self.logger = logger
        self.router_service = RouterService()

    def create_consent(
        self, token: str, user_document: str, dynamic_client_id: str
    ) -> ConsentData:
        try:
            data = {
                "token": token,
                "user_document": user_document,
                "client_id": dynamic_client_id,
                "operation": RouteMethod.POST,
            }
            route = ConsentRoute(data=data)

            result = self.router_service.router_process(route)

            response_data = result.response.json()
            consent_info = ConsentData(
                id=response_data["id"],
                dynamic_client_id=response_data["dynamic_client_id"],
                status=response_data["status"],
                token=response_data["token"],
            )

            self.logger.info(
                f"Consent created successfully for user_document: {user_document}"
            )
            return consent_info

        except (KeyError, ValueError, ConnectionError) as e:
            self.logger.error(
                f"Error creating consent for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(f"Failed to create consent: {str(e)}") from e

    def get_consent(
        self, token: str, user_document: str, consent_id: str | None = None
    ) -> ConsentData | None:
        try:
            route = ConsentRoute(
                data={
                    "token": token,
                    "user_document": user_document,
                    "consent_id": consent_id,
                    "operation": RouteMethod.GET,
                }
            )

            result = self.router_service.router_process(route)

            response_data = result.response.json()

            consent_info = None
            for consent in response_data:
                if (
                    consent["user_document_number"] == user_document
                    and consent["dynamic_client_id"] == consent_id
                    and consent["status"] == "APPROVED"
                ):
                    consent_info = ConsentData(
                        id=consent["id"],
                        dynamic_client_id=consent["dynamic_client_id"],
                        status=consent["status"],
                        token=consent["token"],
                    )
                    break

            self.logger.info(
                f"Consent retrieved successfully for user_document: {user_document}"
            )
            return consent_info

        except (KeyError, ValueError, ConnectionError) as e:
            self.logger.error(
                f"Error retrieving consent for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(f"Failed to retrieve consent: {str(e)}") from e

    def get_or_create_consent(
        self, user_document: str, client_id: str, token: str
    ) -> ConsentData:
        try:
            consent_data = self.get_consent(
                token=token, user_document=user_document
            )
            if not consent_data:
                return self.create_consent(
                    token=token,
                    user_document=user_document,
                    dynamic_client_id=client_id,
                )

            return consent_data

        except (KeyError, ValueError, ConnectionError) as e:
            self.logger.error(
                f"Error getting or creating consent for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(
                f"Failed to get or create consent: {str(e)}"
            ) from e
