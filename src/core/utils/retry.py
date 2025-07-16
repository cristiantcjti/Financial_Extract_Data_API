import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def retry_with_backoff(
    max_retries: int = 3,
    backoff_increment: int = 5,
    logger: logging.Logger | None = None,
) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal logger
            if logger is None and args and hasattr(args[0], "_logger"):
                logger = args[0]._logger
            if logger is None:
                logger = logging.getLogger(__name__)

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries:
                        delay = backoff_increment * (attempt + 1)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}. "
                            f"Retrying in {delay} seconds. Error: {e}"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}. "
                            f"Final error: {e}"
                        )
                        raise

        return wrapper

    return decorator
