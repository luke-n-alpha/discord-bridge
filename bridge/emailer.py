import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional, Sequence, Tuple

from bridge.config import SMTPConfig


def send_email(
    cfg: SMTPConfig,
    subject: str,
    body: str,
    attachments: Optional[Sequence[Tuple[str, bytes, str]]] = None,
) -> None:
    """
    Send an email via SMTP. attachments: list of (filename, content_bytes, mime_type)
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = cfg.from_email
    msg["To"] = ", ".join(cfg.to_emails)
    msg.set_content(body)

    for filename, content_bytes, mime in attachments or []:
        maintype, subtype = mime.split("/", 1)
        msg.add_attachment(content_bytes, maintype=maintype, subtype=subtype, filename=filename)

    context = ssl.create_default_context()
    with smtplib.SMTP(cfg.host, cfg.port, timeout=20) as server:
        if cfg.use_tls:
            server.starttls(context=context)
        server.login(cfg.username, cfg.password)
        server.send_message(msg)
