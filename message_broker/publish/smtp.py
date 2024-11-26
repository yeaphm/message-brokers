import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

emails = ["s.lekhtin@innopolis.university", "e.puzhalov@innopolis.university"]


def send_email(smtp_server, port, sender_email, sender_password, subject, message_schema):
    for email in emails:
        try:
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = email
            message["Subject"] = subject

            body = f"From user: {message_schema.user_alias}\nMessage: {message_schema.message}"
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message.as_string())

            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")
