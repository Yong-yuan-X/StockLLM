import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from core.config import (
    MAIL_FROM_ADDRESS,
    MAIL_FROM_NAME,
    MAIL_HOST,
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_USE_SSL,
    MAIL_USE_TLS,
    MAIL_USERNAME,
)


def send_html_email(to_address, subject, html_body):
    """Send an HTML email via configured SMTP server."""
    if not to_address:
        raise ValueError("未设置收件邮箱")

    if not MAIL_HOST or not MAIL_USERNAME or not MAIL_PASSWORD:
        raise ValueError("邮件服务配置不完整，请先补充 SMTP 配置")

    message = MIMEMultipart("alternative")
    message["Subject"] = Header(subject, "utf-8")
    message["From"] = formataddr((str(Header(MAIL_FROM_NAME, "utf-8")), MAIL_FROM_ADDRESS))
    message["To"] = to_address
    message.attach(MIMEText(html_body, "html", "utf-8"))

    smtp_class = smtplib.SMTP_SSL if MAIL_USE_SSL else smtplib.SMTP
    with smtp_class(MAIL_HOST, MAIL_PORT, timeout=20) as server:
        if MAIL_USE_TLS and not MAIL_USE_SSL:
            server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_FROM_ADDRESS, [to_address], message.as_string())
