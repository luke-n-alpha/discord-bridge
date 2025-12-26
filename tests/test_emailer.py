from email.message import EmailMessage

import smtplib
import pytest

from bridge.config import SMTPConfig
from bridge.emailer import send_email


class DummySMTP:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.logged_in = False
        self.sent = []

    def __enter__(self):
        DummySMTP.instance = self
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self, context=None):
        self.started_tls = True

    def login(self, username, password):
        self.logged_in = (username, password)

    def send_message(self, msg: EmailMessage):
        self.sent.append(msg)


def test_send_email(monkeypatch):
    cfg = SMTPConfig(
        host="smtp.office365.com",
        port=587,
        username="user@example.com",
        password="pass",
        use_tls=True,
        from_email="user@example.com",
        to_emails=["a@example.com", "b@example.com"],
    )

    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)

    send_email(cfg, "Subject", "Body", attachments=[("test.txt", b"data", "text/plain")])

    smtp = DummySMTP.instance
    assert smtp.host == "smtp.office365.com"
    assert smtp.port == 587
    assert smtp.started_tls is True
    assert smtp.logged_in == ("user@example.com", "pass")
    assert len(smtp.sent) == 1
    msg = smtp.sent[0]
    assert msg["Subject"] == "Subject"
    assert "a@example.com" in msg["To"]
    assert "b@example.com" in msg["To"]
    # attachment should be present
    assert len(msg.get_payload()) > 1
