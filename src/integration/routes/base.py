from typing import Any

import requests
from requests import HTTPError, Response

from src.config.logging import logger
from src.integration.dtos.integration_dtos import IntegrationResultDTO
from src.integration.enums import RouteMethod


class BaseRoute:
    def __init__(self) -> None:
        self.method: RouteMethod | None = None

    def get_base_url(self) -> str | None:
        raise NotImplementedError("get_base_url_not_implemented")

    def get_resource_path(self) -> str:
        raise NotImplementedError("get_resource_path_not_implemented")

    def get_data_resource_path(self) -> str:
        raise NotImplementedError("get_data_resource_path_not_implemented")

    def get_payload(self) -> dict:
        raise NotImplementedError("get_payload_not_implemented")

    def set_method(self) -> None:
        raise NotImplementedError("set_method_not_implemented")

    def get_authorization_header(self) -> Any:
        return

    def integrate(self) -> IntegrationResultDTO:
        methods = {
            RouteMethod.GET: self.execute_get,
            RouteMethod.POST: self.execute_post,
            RouteMethod.PUT: self.execute_put,
            RouteMethod.DELETE: self.execute_delete,
        }
        self.set_method()
        if self.method is None:
            raise ValueError("Method cannot be None when integrating")
        response = methods[self.method]()
        success = response.ok
        return IntegrationResultDTO(
            success=success, request=response.request, response=response
        )

    def execute_get(self) -> Response:
        url = f"{self.get_base_url()}{self.get_resource_path()}"
        return self.execute_request(RouteMethod.GET, url)

    def execute_post(self) -> Response:
        url = f"{self.get_base_url()}{self.get_resource_path()}"
        return self.execute_request(RouteMethod.POST, url, self.get_payload())

    def execute_put(self) -> Response:
        url = f"{self.get_base_url()}{self.get_data_resource_path()}"
        return self.execute_request(RouteMethod.PUT, url, self.get_payload())

    def execute_delete(self) -> Response:
        url = f"{self.get_base_url()}{self.get_data_resource_path()}"
        return self.execute_request(RouteMethod.DELETE, url)

    def execute_request(
        self, method: RouteMethod, url: str, payload: dict | None = None
    ) -> Response:
        authorization_header = self.get_authorization_header() or {}
        headers = {"content-Type": "application/json"} | authorization_header
        try:
            request_function = getattr(requests, method.value.lower())
            logger.info(
                f"Executing Request - URL:{url}, Method:{method}, Payload:{payload}, "
            )
            response = request_function(
                url=url,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response
        except HTTPError:
            logger.error(
                msg=f"Error in {self.__class__.__name__}, "
                f"method: {method}, "
                f"url: {url}, "
                f"payload: {payload} "
            )
            raise
        except Exception as err:
            logger.exception(
                msg=f"Error in {self.__class__.__name__}, "
                f"method: {method}, "
                f"url: {url}, "
                f"payload: {payload}"
                f"traceback: {err}"
            )
            raise
