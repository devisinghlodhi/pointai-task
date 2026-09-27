import asyncio
import time
import httpx

TARGET_URL = "http://localhost:8080/upload"
VALID_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
TOTAL_REQUESTS = 60
CONCURRENT_CONNECTIONS = 15

async def send_single_request(client: httpx.AsyncClient):
    try:
        res = await client.post(TARGET_URL, json={"image": VALID_B64}, timeout=10.0)
        worker_id = res.headers.get("x-worker-node", "unknown")
        return res.status_code, worker_id
    except Exception as exc:
        return None, str(exc)

async def run_load_test():
    limits = httpx.Limits(max_connections=CONCURRENT_CONNECTIONS)
    async with httpx.AsyncClient(limits=limits) as client:
        start_time = time.perf_counter()
        tasks = [send_single_request(client) for _ in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - start_time

    node_distribution = {}
    success_count = 0
    failure_count = 0

    for status_code, node in results:
        if status_code == 200:
            success_count += 1
            node_distribution[node] = node_distribution.get(node, 0) + 1
        else:
            failure_count += 1

    print("\n" + "=" * 45)
    print("CONCURRENCY & LOAD TEST SUMMARY")
    print("=" * 45)
    print(f"Total Requests Sent   : {TOTAL_REQUESTS}")
    print(f"Concurrent Conns      : {CONCURRENT_CONNECTIONS}")
    print(f"Completed In          : {elapsed:.2f} seconds")
    print(f"Successful (200 OK)   : {success_count}")
    print(f"Failed                : {failure_count}")
    print("\nRequests Distributed Per Container Replica:")
    for node, count in node_distribution.items():
        print(f"  Container [{node}]: {count} requests")
    print("=" * 45 + "\n")

if __name__ == "__main__":
    asyncio.run(run_load_test())