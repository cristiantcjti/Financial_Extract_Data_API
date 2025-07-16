from typing import Any

from django.conf import settings

from src.integration.routes.base import BaseRoute


class AccountsRoute(BaseRoute):
    def __init__(self, data: dict[str, Any]):
        super().__init__()
        self._account_id = data.get("account_id")
        self._token = data.get("token", "")
        self._operation = data.get("operation")
        self._page = data.get("page", 1)
        self._limit = data.get("limit", 10)

    def get_base_url(self) -> str | None:
        return settings.OFDA_API_BASE_URL

    def get_resource_path(self) -> str:
        path = "/account/"
        if self._account_id:
            path = path + f"{self._account_id}"
        if self._page:
            path = f"/account?page={self._page}"
        return path

    def get_authorization_header(self) -> dict[str, str]:
        return {"Authorization": f"{self._token}"}

    def set_method(self) -> None:
        self.method = self._operation

    def get_payload(self) -> dict[str, Any]:
        return {}

