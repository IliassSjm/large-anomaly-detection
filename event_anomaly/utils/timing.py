
import time
import functools
from contextlib import contextmanager

@contextmanager
def measure_latency(name="operation"):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    duration_ms = (end - start) * 1000
    # In a real app, we would log this to a metric system (Prometheus/StatsD)
    # print(f"{name} took {duration_ms:.2f} ms")

def time_execution(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        duration_ms = (end - start) * 1000
        # print(f"{func.__name__} took {duration_ms:.2f} ms")
        return result
    return wrapper
