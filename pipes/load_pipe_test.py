import asyncio
import httpx
import time
from statistics import mean

URL = "http://127.0.0.1:8000/"  # Pipes-and-filters endpoint
MESSAGES = [{"user_alias": f"user_{i}", "message": f"Test message {i}"} for i in range(5)]

async def send_request(client, data):
    start_time = time.time()
    response = await client.post(URL, json=data)
    end_time = time.time()
    return end_time - start_time, response.status_code

async def load_test():
    async with httpx.AsyncClient(timeout=50.0) as client:
        latencies = []
        for message in MESSAGES:
            latency, status = await send_request(client, message)
            latencies.append(latency)
            print(f"Message sent: {message['message']}, Status: {status}, Latency: {latency:.2f}s")
        print(f"Average Latency: {mean(latencies):.2f}s")

if __name__ == "__main__":
    asyncio.run(load_test())
