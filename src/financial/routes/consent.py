from typing import Any

from django.conf import settings

from src.integration.routes.base import BaseRoute


class ConsentRoute(BaseRoute):
    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__()
        self._user_document = data.get("user_document")
        self._consent_id = data.get("consent_id", "")
        self._client_id = data.get("client_id", "")
        self._token = data.get("token", "")
        self._operation = data.get("operation")

    def get_base_url(self) -> str:
        return settings.OFDA_API_BASE_URL

    def get_resource_path(self) -> str:
        path = "/consent/"
        if self._consent_id:
            return path + f"{self._consent_id}/"
        return path

    def get_authorization_header(self) -> Any:
        return {"Authorization": f"{self._token}"}

    def set_method(self) -> None:
        self.method = self._operation

    def get_payload(self) -> dict[str, Any]:
        return {
            "user_document_number": self._user_document,
            "dynamic_client_id": self._client_id,
        }
