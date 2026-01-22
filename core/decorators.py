"""
Custom decorators for cross-cutting concerns.
Demonstrates Python decorator pattern with logging and timing.
"""
import time
import functools
import logging
from typing import Callable, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log execution time of async functions.
    Demonstrates Python decorators and async handling.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Wrapped function with timing logic
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function '{func.__name__}' executed in {execution_time:.4f} seconds"
            )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function '{func.__name__}' failed after {execution_time:.4f} seconds: {str(e)}"
            )
            raise
    
    return wrapper


def log_request(func: Callable) -> Callable:
    """
    Decorator to log API endpoint requests.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Wrapped function with request logging
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(f"Endpoint '{func.__name__}' called with args={args}, kwargs={kwargs}")
        result = await func(*args, **kwargs)
        logger.info(f"Endpoint '{func.__name__}' completed successfully")
        return result
    
    return wrapper