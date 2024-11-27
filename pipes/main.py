import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import multiprocessing
import json
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import signal

# Load environment variables
load_dotenv()

# Define the FastAPI app
app = FastAPI()

# Shared queues for the pipes-and-filters architecture
filter_queue = multiprocessing.Queue()
screaming_queue = multiprocessing.Queue()
publish_queue = multiprocessing.Queue()

# Define stop words
STOP_WORDS = {"bird-watching", "ailurophobia", "mango"}

# Define the data schema
class MessageRequest(BaseModel):
    user_alias: str
    message: str

@app.post("/")
async def read_message(request: MessageRequest):
    """Handles incoming messages and passes them to the first queue."""
    message = {"user_alias": request.user_alias, "message": request.message}
    filter_queue.put(json.dumps(message))
    print(f"Message received and added to filter_queue: {message}")
    return {"status": "Message received", "message": message}

# Filter service
def filter_service(input_queue, output_queue):
    while True:
        try:
            message = input_queue.get(timeout=1)  # Add timeout to prevent blocking
            if message is None:  # Stop signal
                output_queue.put(None)
                break

            data = json.loads(message)
            if any(word in data["message"] for word in STOP_WORDS):
                print(f"Message filtered out: {data['message']}")
            else:
                print(f"Message passed to screaming_queue: {data}")
                output_queue.put(json.dumps(data))
        except Exception as e:
            pass  # Timeout or other errors

# Screaming service
def screaming_service(input_queue, output_queue):
    while True:
        try:
            message = input_queue.get(timeout=1)  # Add timeout to prevent blocking
            if message is None:  # Stop signal
                output_queue.put(None)
                break

            data = json.loads(message)
            data["message"] = data["message"].upper()
            print(f"Message converted to uppercase and passed to publish_queue: {data}")
            output_queue.put(json.dumps(data))
        except Exception as e:
            pass  # Timeout or other errors

# Publish service
def publish_service(input_queue):
    while True:
        try:
            message = input_queue.get(timeout=1)  # Add timeout to prevent blocking
            if message is None:  # Stop signal
                break

            data = json.loads(message)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "ssslekhtin@gmail.com"
            sender_password = os.getenv("SMTP_PASSWORD")

            if not sender_password:
                print("SMTP_PASSWORD environment variable is not set.")
                continue

            send_email(
                smtp_server=smtp_server,
                port=smtp_port,
                sender_email=sender_email,
                sender_password=sender_password,
                subject=f"Message from {data['user_alias']}",
                message_schema=data,
            )
            print(f"Email sent successfully for message: {data}")
        except Exception as e:
            pass  # Timeout or other errors

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

# Signal handler to stop processes
def signal_handler(sig, frame):
    print("Shutting down gracefully...")
    filter_queue.put(None)
    screaming_queue.put(None)
    publish_queue.put(None)

if __name__ == "__main__":
    # Run the backend pipeline filters in separate processes
    filter_process = multiprocessing.Process(target=filter_service, args=(filter_queue, screaming_queue))
    screaming_process = multiprocessing.Process(target=screaming_service, args=(screaming_queue, publish_queue))
    publish_process = multiprocessing.Process(target=publish_service, args=(publish_queue,))

    filter_process.start()
    screaming_process.start()
    publish_process.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start the FastAPI server
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
        )
    finally:
        # Stop all processes when the app shuts down
        filter_queue.put(None)
        screaming_queue.put(None)
        publish_queue.put(None)

        filter_process.join()
        screaming_process.join()
        publish_process.join()