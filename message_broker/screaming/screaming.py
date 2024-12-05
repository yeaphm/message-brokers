import asyncio
from aio_pika import connect_robust, Message, IncomingMessage
import json


async def process_message(message: IncomingMessage, channel):
    async with message.process():
        data = json.loads(message.body.decode())
        data["message"] = data["message"].upper()
        msg = Message(json.dumps(data).encode())
        await channel.default_exchange.publish(msg, routing_key="publish_queue")
        print(f"Message forwarded to publish_queue: {data}")


async def main():
    connection = await connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    await channel.declare_queue("screaming_queue")
    await channel.declare_queue("publish_queue", durable=True)

    queue = await channel.get_queue("screaming_queue")
    await queue.consume(lambda msg: process_message(msg, channel))
    print("SCREAMING Service is running...")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
