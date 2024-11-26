import typing

from aio_pika import connect, Message

if typing.TYPE_CHECKING:
    from message_broker.api.main import MessageRequest


async def publish_message(message: "MessageRequest"):
    connection = await connect("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()

        queue_name = "filter_queue"
        await channel.declare_queue(queue_name)

        await channel.default_exchange.publish(
            Message(body=message.model_dump_json().encode()),
            routing_key=queue_name,
        )
        print(f"Message sent: {message}")
