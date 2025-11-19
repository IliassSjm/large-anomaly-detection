
import requests
import time
import json
import numpy as np
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8000/score_sequence"
NUM_REQUESTS = 200
CONCURRENCY = 10

def send_request():
    # Create a dummy sequence
    payload = {
        "events": [
            {"timestamp": "2023-01-01T12:00:00", "service": "auth", "level": "INFO", "message": "Request received"},
            {"timestamp": "2023-01-01T12:00:01", "service": "auth", "level": "INFO", "message": "User authenticated"}
        ]
    }
    
    start = time.perf_counter()
    try:
        resp = requests.post(URL, json=payload)
        resp.raise_for_status()
        end = time.perf_counter()
        return (end - start) * 1000
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def run_load_test():
    print(f"Starting load test: {NUM_REQUESTS} requests, {CONCURRENCY} concurrency")
    latencies = []
    
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        results = list(executor.map(lambda _: send_request(), range(NUM_REQUESTS)))
        
    latencies = [r for r in results if r is not None]
    
    if not latencies:
        print("All requests failed!")
        return

    p50 = np.percentile(latencies, 50)
    p90 = np.percentile(latencies, 90)
    p99 = np.percentile(latencies, 99)
    
    print(f"Results ({len(latencies)} requests):")
    print(f"P50: {p50:.2f} ms")
    print(f"P90: {p90:.2f} ms")
    print(f"P99: {p99:.2f} ms")
    print(f"Avg: {np.mean(latencies):.2f} ms")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    run_load_test()
