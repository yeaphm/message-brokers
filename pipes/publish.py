import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from pipes.filter import Filter

load_dotenv()


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
