import json

from pipes.filter import Filter


class ScreamingService(Filter):
    def process(self, message, queue=None):
        """Convert the message to uppercase."""
        data = json.loads(message)
        data["message"] = data["message"].upper()
        print(f"Screaming service: Message converted to uppercase: {data}")

        updated_message = json.dumps(data)
        if self.next_filter:
            self.next_filter.process(updated_message, queue)
