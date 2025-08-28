from .smtp_client import SMTPClient

class EmailNotifications:
    def __init__(self, smtp_client: SMTPClient):
        self.smtp = smtp_client

    async def send_verification_email(self, receiver_email: str, verification_code: str) -> None:
        subject = 'Verification code for Makeasap'
        body = f'Your verification code: {verification_code}'
        await self.smtp.send_email(receiver_email, subject, body)

    async def send_bid_confirmation_email(self, receiver_email: str, delete_link: str) -> None:
        subject = 'Ваша заявка створена - FreelanceBirja'
        body = f'''
Ваша заявка успішно створена на FreelanceBirja!

Для видалення заявки перейдіть за посиланням:
{delete_link}

---
FreelanceBirja - Біржа послуг та виконавців
'''
        await self.smtp.send_email(receiver_email, subject, body)

    async def send_bid_response_email(
        self, 
        bid_owner_email: str, 
        responder_name: str, 
        responder_email: str, 
        message: str, 
        bid_title: str
    ) -> None:
        subject = f'Новий відгук на вашу заявку: {bid_title}'
        body = f'''
Отримано новий відгук на вашу заявку "{bid_title}".

Від: {responder_name}
Email: {responder_email}

Повідомлення:
{message}

---
FreelanceBirja - Біржа послуг та виконавців
'''
        await self.smtp.send_email(bid_owner_email, subject, body)
