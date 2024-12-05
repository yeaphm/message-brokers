import asyncio
import json
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process

STOP_WORDS = {"bird-watching", "ailurophobia", "mango"}


class Filter:
    def __init__(self, next_filter=None):
        self.next_filter = next_filter

    def process(self, message, queue=None):
        raise NotImplementedError("Subclasses should implement this method.")


class FilterService(Filter):
    def process(self, message, queue=None):
        """Check if the message contains stop words."""
        data = json.loads(message)
        if any(word in data["message"] for word in STOP_WORDS):
            print(f"Filter service: Message filtered out: {data['message']}")
            if queue is not None:
                queue.put(None)
            return
        else:
            print(f"Filter service: Message passed to next filter: {data}")
            if self.next_filter:
                self.next_filter.process(json.dumps(data), queue)


def run_filter_in_process(filter_instance, message, queue=None):
    process = Process(target=filter_instance.process, args=(message, queue))
    process.start()
    process.join()


async def run_filter_chain_async(filter_instance, message):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as executor:
        future = loop.run_in_executor(executor, run_filter_in_process, filter_instance, message, None)
        await asyncio.wrap_future(future)
