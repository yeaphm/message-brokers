import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from multiprocessing import Process, Queue
import asyncio
from concurrent.futures import ProcessPoolExecutor

# Load environment variables
load_dotenv()

# Define the FastAPI app
app = FastAPI()

# Define the data schema
class MessageRequest(BaseModel):
    user_alias: str
    message: str

# Define stop words
STOP_WORDS = {"bird-watching", "ailurophobia", "mango"}

# Filter classes
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
                queue.put(None)  # Signal the next filter to stop processing
            return
        else:
            print(f"Filter service: Message passed to next filter: {data}")
            if self.next_filter:
                self.next_filter.process(json.dumps(data), queue)

class ScreamingService(Filter):
    def process(self, message, queue=None):
        """Convert the message to uppercase."""
        data = json.loads(message)
        data["message"] = data["message"].upper()
        print(f"Screaming service: Message converted to uppercase: {data}")

        updated_message = json.dumps(data)
        if self.next_filter:
            self.next_filter.process(updated_message, queue)

class PublishService(Filter):
    def process(self, message, queue=None):
        """Send the message via email."""
        data = json.loads(message)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "ssslekhtin@gmail.com"
        sender_password = os.getenv("SMTP_PASSWORD")

        if not sender_password:
            print("SMTP_PASSWORD environment variable is not set.")
            return

        send_email(
            smtp_server=smtp_server,
            port=smtp_port,
            sender_email=sender_email,
            sender_password=sender_password,
            subject=f"Message from {data['user_alias']}",
            message_schema=data,
        )
        print(f"Publish service: Email sent successfully for message: {data}")

# Email sending function
emails = [
    "s.lekhtin@innopolis.university",
    "e.puzhalov@innopolis.university",
    "e.meganov@innopolis.university",
    "v.grigorev@innopolis.university",
    "m.drazdou@innopolis.university",
]

def send_email(smtp_server, port, sender_email, sender_password, subject, message_schema):
    for email in emails:
        try:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = email
            message["Subject"] = subject

            body = f"From user: {message_schema['user_alias']}\nMessage: {message_schema['message']}"
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message.as_string())

            print(f"Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

# Function to run a filter in a separate process
def run_filter_in_process(filter_instance, message, queue=None):
    process = Process(target=filter_instance.process, args=(message, queue))
    process.start()
    process.join()

# Function to process the entire chain asynchronously
async def run_filter_chain_async(filter_instance, message):
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as executor:
        future = loop.run_in_executor(executor, run_filter_in_process, filter_instance, message, None)
        await asyncio.wrap_future(future)

# Pipeline initialization
filter_chain = FilterService(
    next_filter=ScreamingService(
        next_filter=PublishService()
    )
)

# FastAPI route
@app.post("/")
async def read_message(request: MessageRequest):
    """Handles incoming messages and processes them through the filter chain."""
    message = {"user_alias": request.user_alias, "message": request.message}
    message_json = json.dumps(message)

    print(f"Message received: {message}")

    # Run the filter chain in a background process
    await run_filter_chain_async(filter_chain, message_json)

    return {"status": "Message processing started"}

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
