import asyncio
from aio_pika import connect_robust, Message, IncomingMessage
import json

STOP_WORDS = {"bird-watching", "ailurophobia", "mango"}


async def process_message(message: IncomingMessage, channel):
    async with message.process():
        data = json.loads(message.body.decode())  # Parse JSON
        if any(word in data["message"] for word in STOP_WORDS):
            print(f"Message filtered: {data['message']}")
        else:
            msg = Message(json.dumps(data).encode())
            await channel.default_exchange.publish(msg, routing_key="screaming_queue")
            print(f"Message forwarded to screaming_queue: {data}")


async def main():
    connection = await connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    await channel.declare_queue("filter_queue")
    await channel.declare_queue("screaming_queue")

    queue = await channel.get_queue("filter_queue")
    await queue.consume(lambda msg: process_message(msg, channel))
    print("Filter Service is running...")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
