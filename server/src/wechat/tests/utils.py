import asyncio
from functools import wraps


def async_test(asyncTestMethod):
    @wraps(asyncTestMethod)
    def wrapper(*args, **kwargs):
        result = asyncio.run(asyncTestMethod(*args, **kwargs))
        return result
    return wrapper
