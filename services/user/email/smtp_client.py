import aiosmtplib
from email.mime.text import MIMEText

class SMTPClient:
    def __init__(self, host: str, port: int, username: str, password: str, use_tls: bool = True):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    async def send_email(self, receiver_email: str, subject: str, body: str) -> None:
        message = MIMEText(body)
        message['Subject'] = subject
        message['From'] = self.username
        message['To'] = receiver_email

        await aiosmtplib.send(
            message,
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            use_tls=self.use_tls
        )
