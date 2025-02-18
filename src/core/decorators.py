import asyncio
from functools import wraps
from time import perf_counter
from typing import Callable, Any

from loguru import logger


def log_execution_time(func: Callable) -> Callable:
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> Any:
        start_time = perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed_time = (perf_counter() - start_time) * 1000
            logger.info(f"[{func.__name__}] took {elapsed_time:.2f}ms")
            return result
        except Exception as e:
            elapsed_time = (perf_counter() - start_time) * 1000
            logger.error(
                f"[{func.__name__}] failed after {elapsed_time:.2f}ms: {str(e)}"
            )
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> Any:
        start_time = perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed_time = (perf_counter() - start_time) * 1000
            logger.info(f"[{func.__name__}] took {elapsed_time:.2f}ms")
            return result
        except Exception as e:
            elapsed_time = (perf_counter() - start_time) * 1000
            logger.error(
                f"[{func.__name__}] failed after {elapsed_time:.2f}ms: {str(e)}"
            )
            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
