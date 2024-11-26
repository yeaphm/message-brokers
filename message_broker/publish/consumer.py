import asyncio
import os
import json

import aio_pika
from pydantic import BaseModel
from dotenv import load_dotenv

from message_broker.publish.smtp import send_email

load_dotenv()


class MessageRequest(BaseModel):
    user_alias: str
    message: str


async def consume_messages(rabbitmq_url: str = "amqp://guest:guest@localhost/"):
    connection = await aio_pika.connect_robust(rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        queue_name = "publish_queue"
        queue = await channel.declare_queue(queue_name, durable=True)

        print(f"Waiting for messages in queue '{queue_name}'. To exit, press CTRL+C.")

        async for msg in queue:
            async with msg.process():
                try:
                    body = json.loads(msg.body.decode("utf-8"))
                    message = MessageRequest(**body)
                    print(f"Received message from {message.user_alias}: {message.message}")

                    send_email(
                        smtp_server="smtp.gmail.com",
                        port=587,
                        sender_email="ssslekhtin@gmail.com",
                        sender_password=os.getenv("SMTP_PASSWORD"),
                        subject=f"Message from {message.user_alias}",
                        message_schema=message
                    )
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Failed to process message: {e}")


if __name__ == '__main__':
    asyncio.run(consume_messages())
