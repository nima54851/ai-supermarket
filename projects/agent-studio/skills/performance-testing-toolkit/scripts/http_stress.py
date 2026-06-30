#!/usr/bin/env python3
"""
HTTP Stress Testing Tool
Usage: python3 http_stress.py --url <url> --concurrency <n> --duration <seconds>
"""

import argparse
import asyncio
import time
import statistics
from urllib.parse import urlparse
import httpx

async def request_task(client, url, method, results, start_time, duration):
    end_time = start_time + duration
    while time.time() < end_time:
        req_start = time.perf_counter()
        try:
            resp = await client.request(method, url, timeout=30.0)
            latency = (time.perf_counter() - req_start) * 1000
            results.append((latency, resp.status_code))
        except Exception as e:
            latency = (time.perf_counter() - req_start) * 1000
            results.append((latency, 0))

async def run_stress(url, concurrency, duration, method="GET"):
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    results = []
    start_time = time.time()

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        tasks = [request_task(client, url, method, results, start_time, duration)
                 for _ in range(concurrency)]
        await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    latencies = [r[0] for r in results]
    success = sum(1 for r in results if 200 <= r[1] < 300)
    errors = len(results) - success

    latencies.sort()
    n = len(latencies)

    def pct(p):
        idx = int(n * p / 100)
        return latencies[min(idx, n-1)]

    print(f"\n{'='*50}")
    print(f"  HTTP Stress Test Results")
    print(f"{'='*50}")
    print(f"  Target:      {url}")
    print(f"  Method:      {method}")
    print(f"  Concurrency: {concurrency}")
    print(f"  Duration:    {duration}s")
    print(f"{'='*50}")
    print(f"  Total reqs:  {len(results)}")
    print(f"  Success:     {success} ({success/len(results)*100:.1f}%)")
    print(f"  Errors:      {errors}")
    print(f"  Total time:  {total_time:.2f}s")
    print(f"  QPS:         {len(results)/total_time:.1f} req/s")
    print(f"{'='*50}")
    print(f"  Avg latency: {statistics.mean(latencies):.1f}ms")
    print(f"  Min latency: {min(latencies):.1f}ms")
    print(f"  Max latency: {max(latencies):.1f}ms")
    print(f"  p50:         {pct(50):.1f}ms")
    print(f"  p90:         {pct(90):.1f}ms")
    print(f"  p99:         {pct(99):.1f}ms")
    print(f"  std dev:     {statistics.stdev(latencies):.1f}ms")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--method", default="GET")
    args = parser.parse_args()

    asyncio.run(run_stress(args.url, args.concurrency, args.duration, args.method))
