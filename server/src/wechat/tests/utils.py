import asyncio
from functools import wraps
import sys

if sys.version_info >= (3,7):
    run = asyncio.run
else:
    def run(awaitable):
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(awaitable)
        loop.close()
        return res

def async_test(asyncTestMethod):
    @wraps(asyncTestMethod)
    def wrapper(*args, **kwargs):
        result = run(asyncTestMethod(*args, **kwargs))
        return result
    return wrapper
