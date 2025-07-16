from typing import Any

from django.conf import settings

from src.integration.routes.base import BaseRoute


class DynamicClientRoute(BaseRoute):
    def __init__(self, data: dict[str, Any]) -> None:
        super().__init__()
        self._name = data.get("name")
        self._organization_name = data.get("organization_name")
        self._organization_id = data.get("organization_id")
        self._organization_type = data.get("organization_type")
        self._operation = data.get("operation")
        self._client_id = data.get("client_id", "")

    def get_base_url(self) -> str:
        return settings.OFDA_API_BASE_URL

    def get_resource_path(self) -> str:
        return f"/dynamic-client/{self._client_id}"

    def set_method(self) -> None:
        self.method = self._operation

    def get_payload(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "organization_name": self._organization_name,
            "organization_id": self._organization_id,
            "organization_type": self._organization_type,
        }
