import uuid

from src.config.logging import logger
from src.financial.routes.dynamic_client import DynamicClientRoute
from src.financial.services.dtos.client import DynamicClientData
from src.integration.enums import RouteMethod
from src.integration.services.router_service import RouterService


class DynamicClientService:
    def __init__(self) -> None:
        self.logger = logger
        self.router_service = RouterService()

    def create_client(self, user_document: str) -> DynamicClientData:
        try:
            # Initialize client route
            data = {
                "name": "Belvo_Client",
                "organization_name": "Belvo",
                "organization_id": str(uuid.uuid4()),
                "organization_type": "INDIVIDUAL",
                "operation": RouteMethod.POST,
            }
            route = DynamicClientRoute(data)
            result = self.router_service.router_process(route=route)

            if not result.success:
                raise ValueError("Client creation failed")

            response_data = result.response.json()
            client_info = DynamicClientData(
                id=response_data.get("id"),
                name=response_data.get("name"),
                token=response_data.get("token"),
                organization_name=response_data.get("token"),
                organization_type=response_data.get("organization_type"),
            )

            self.logger.info(
                f"Client created successfully for user_document: {user_document}"
            )
            return client_info

        except (KeyError, ValueError, ConnectionError) as e:
            self.logger.error(
                f"Error creating client for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(f"Failed to create client: {str(e)}") from e

    def get_or_create_client(self, user_document: str) -> DynamicClientData:
        try:
            # I would check a database here and in case there is no client, I would create it.
            return self.create_client(user_document)

        except (KeyError, ValueError, ConnectionError) as e:
            self.logger.error(
                f"Error getting or creating client for user_document: {user_document}, Error: {str(e)}"
            )
            raise ValueError(
                f"Failed to get or create client: {str(e)}"
            ) from e
