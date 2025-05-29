import functools
import time
import logging
from typing import Type, Tuple, Optional
from langchain_core.exceptions import OutputParserException  # Changed import

logger = logging.getLogger(__name__)

class RetryError(Exception):
    """Custom error for retry failures"""
    pass

def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1,
    max_delay: float = 10,
    exceptions: Tuple[Type[Exception], ...] = (OutputParserException, ConnectionError),  # Updated exceptions
    logger: Optional[logging.Logger] = None,
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry
        logger: Logger instance for logging retry attempts
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            local_logger = logger or logging.getLogger(func.__module__)
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    if attempt == max_retries:
                        local_logger.error(
                            f"Failed after {max_retries} retries. Final error: {str(e)}"
                        )
                        raise RetryError(f"Max retries ({max_retries}) exceeded. Last error: {str(e)}")
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    local_logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
            
            return None  # Should never reach here
        return wrapper
    return decorator