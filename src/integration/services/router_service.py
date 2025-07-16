import logging
from typing import Any
from urllib.error import HTTPError

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import RequestException, Timeout

from src.core.utils.retry import retry_with_backoff
from src.integration.routes.base import BaseRoute


class RouterService:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    @retry_with_backoff(max_retries=3, backoff_increment=1)
    def router_process(self, route: BaseRoute) -> Any:
        try:
            integration_result = route.integrate()
            if integration_result.success:
                return integration_result
        except HTTPError as exc:
            self._logger.error(
                f"Exception when running integration process. Error: {exc}"
            )
            raise
        except (RequestException, RequestsConnectionError, Timeout) as exc:
            self._logger.error(
                f"Request exception when running integration process. Error: {exc}"
            )
            raise
        except Exception as exc:
            self._logger.error(
                f"Unexpected exception when running integration process. Error: {exc}"
            )
            raise
