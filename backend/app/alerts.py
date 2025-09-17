import smtplib
from email.message import EmailMessage
import json
import urllib.request
from .core.config import get_settings


settings = get_settings()


def send_email(subject: str, body: str, to: list[str]) -> None:
    if not (settings.smtp_host and settings.smtp_from and to):
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = ", ".join(to)
    msg.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port or 587) as server:
        server.starttls()
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


def send_slack(text: str) -> None:
    if not settings.slack_webhook_url:
        return
    data = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        settings.slack_webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=10)


