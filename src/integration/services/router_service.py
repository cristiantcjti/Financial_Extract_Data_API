import logging
from typing import Any
from urllib.error import HTTPError

from src.core.utils.retry import retry_with_backoff


class RouterService:

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @retry_with_backoff(max_retries=3, backoff_increment=1)
    def router_process(self, route) -> Any:
        try:
            integration_result = route.integrate()
            if integration_result.success:
                return integration_result
        except HTTPError as exc:
            self._logger.error(
                f"Exception when running integration process. Error: {exc}"
            )
            raise
        except Exception as exc:
            self._logger.error(
                f"Exception when running integration process. Error: {exc}"
            )
            raise
