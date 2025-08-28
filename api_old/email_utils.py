import random
import time
from typing import Tuple

LAST_CODE_SENT: dict = {}

CODE_RESEND_INTERVAL = 60
VERIFICATION_CODE_LENGTH = 6


async def send_verification_email(receiver_email: str, verification_code: str) -> None:
    """Отправляет email с кодом верификации (УНИВЕРСАЛЬНАЯ ФУНКЦИЯ)"""
    print(f"DEBUG: Sending verification email to {receiver_email}")
    try:
        from services.user.email.smtp_client import SMTPClient
        from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
        
        smtp_client = SMTPClient(
            host=SMTP_HOST,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        
        subject = "Ваш код підтвердження / Your verification code"
        body = f"""
Ваш код підтвердження: {verification_code}

Your verification code: {verification_code}

Введіть цей код на сайті для підтвердження.
Enter this code on the website to confirm.

Якщо ви не запитували цей код, проігноруйте це повідомлення.
If you did not request this code, please ignore this message.
        """
        
        await smtp_client.send_email(receiver_email, subject, body)
        print(f"DEBUG: Verification email sent successfully to {receiver_email}!")
        
    except Exception as e:
        print(f"DEBUG: Email sending failed: {e} - proceeding without email")
        raise e


async def send_email(receiver_email: str, verification_code: str) -> None:
    """Обертка для отправки email с кодом верификации"""
    await send_verification_email(receiver_email, verification_code)


def can_send_verification_code(email: str) -> Tuple[bool, int]:
    current_time = time.time()
    last_sent_time = LAST_CODE_SENT.get(email, 0)
    
    if current_time - last_sent_time < CODE_RESEND_INTERVAL:
        wait_time = int(CODE_RESEND_INTERVAL - (current_time - last_sent_time))
        return False, wait_time
    
    LAST_CODE_SENT[email] = current_time
    return True, 0


def can_send_code(email: str) -> Tuple[bool, int]:
    result = can_send_verification_code(email)
    print(f"DEBUG: can_send_code for {email}: {result}")
    return result


def generate_verification_code() -> str:
    code = ''.join(random.choices('0123456789', k=VERIFICATION_CODE_LENGTH))
    print(f"DEBUG: Generated verification code: {code}")
    return code


def generate_code() -> str:
    return generate_verification_code()


async def send_bid_confirmation_email(receiver_email: str, delete_link: str) -> None:
    """Отправляет email подтверждения о создании заявки с ссылкой для удаления"""
    try:
        from services.user.email.smtp_client import SMTPClient
        from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
        
        smtp_client = SMTPClient(
            host=SMTP_HOST,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        
        subject = "Заявка успішно створена / Request Successfully Created"
        body = f"""
Вітаємо! Ваша заявка була успішно створена та опублікована.

Congratulations! Your request has been successfully created and published.

Для видалення заявки використовуйте це посилання:
To delete your request, use this link:
{delete_link}

Збережіть це посилання в безпечному місці.
Keep this link in a safe place.

Дякуємо за використання нашого сервісу!
Thank you for using our service!
        """
        
        await smtp_client.send_email(receiver_email, subject, body)
        print(f"DEBUG: Bid confirmation email sent successfully to {receiver_email}!")
        
    except Exception as e:
        print(f"DEBUG: Bid confirmation email sending failed: {e} - proceeding without email")
        raise e


async def send_registration_and_bid_confirmation_email(receiver_email: str, user_password: str, bid) -> None:
    """Отправляет email с данными для входа и подтверждением создания заявки для нового пользователя"""
    print(f"DEBUG: Sending registration and bid confirmation email to {receiver_email}")
    try:
        from services.user.email.smtp_client import SMTPClient
        from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
        
        smtp_client = SMTPClient(
            host=SMTP_HOST,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        
        delete_link = f"http://localhost:8000/delete-bid/{bid.id}?token={bid.delete_token}"
        
        subject = "Аккаунт створено та заявка подана / Account Created and Request Submitted"
        body = f"""
Вітаємо! Ваш аккаунт було створено, а заявка успішно подана.

Congratulations! Your account has been created and your request has been successfully submitted.

Дані для входу / Login credentials:
Email: {receiver_email}
Пароль / Password: {user_password}

Заявка ID / Request ID: {bid.id}

Для видалення заявки використовуйте це посилання:
To delete your request, use this link:
{delete_link}

Збережіть ці дані в безпечному місці.
Please save this information in a secure place.
        """
        
        await smtp_client.send_email(receiver_email, subject, body)
        print(f"DEBUG: Registration and bid confirmation email sent successfully to {receiver_email}!")
        
    except Exception as e:
        print(f"DEBUG: Registration and bid confirmation email sending failed: {e} - proceeding without email")
        raise e

async def send_account_created_notification(receiver_email: str) -> None:
    """Отправляет уведомление о создании аккаунта"""
    print(f"DEBUG: Sending account creation notification to {receiver_email}")
    try:
        from services.user.email.smtp_client import SMTPClient
        from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
        
        smtp_client = SMTPClient(
            host=SMTP_HOST,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        
        subject = "Аккаунт успішно створено / Account Successfully Created"
        body = f"""
Вітаємо! Ваш аккаунт було успішно створено.

Congratulations! Your account has been successfully created.

Email: {receiver_email}

Тепер ви можете увійти в систему та користуватися всіма функціями.
You can now log in and use all features.

Дякуємо за реєстрацію!
Thank you for registering!
        """
        
        await smtp_client.send_email(receiver_email, subject, body)
        print(f"DEBUG: Account creation notification sent successfully to {receiver_email}!")
        
    except Exception as e:
        print(f"DEBUG: Account creation notification failed: {e}")

async def send_bid_created_notification(receiver_email: str, bid_id: int) -> None:
    """Отправляет уведомление о создании заявки"""
    print(f"DEBUG: Sending bid creation notification to {receiver_email}")
    try:
        from services.user.email.smtp_client import SMTPClient
        from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
        
        smtp_client = SMTPClient(
            host=SMTP_HOST,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        
        subject = "Заявка успішно створена / Request Successfully Created"
        body = f"""
Ваша заявка була успішно створена!

Your request has been successfully created!

Заявка ID / Request ID: {bid_id}

Ви можете переглянути та керувати своїми заявками в особистому кабінеті.
You can view and manage your requests in your personal account.

Дякуємо за використання нашого сервісу!
Thank you for using our service!
        """
        
        await smtp_client.send_email(receiver_email, subject, body)
        print(f"DEBUG: Bid creation notification sent successfully to {receiver_email}!")
        
    except Exception as e:
        print(f"DEBUG: Bid creation notification failed: {e}")


async def send_bid_response_email(
    bid_owner_email: str, 
    responder_name: str, 
    responder_email: str, 
    message: str, 
    bid_title: str
) -> None:
    """Отправляет email владельцу заявки о новом отклике"""
    try:
        from services.user.email.smtp_client import SMTPClient
        from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
        
        smtp_client = SMTPClient(
            host=SMTP_HOST,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )
        
        subject = f"Новий відгук на вашу заявку: {bid_title}"
        body = f"""
Ви отримали новий відгук на вашу заявку "{bid_title}".

Від: {responder_name} ({responder_email})
Повідомлення: {message}

Для відповіді зв'яжіться з відправником безпосередньо.
        """
        
        await smtp_client.send_email(bid_owner_email, subject, body)
        print(f"DEBUG: Bid response email sent successfully to {bid_owner_email}!")
        
    except Exception as e:
        print(f"DEBUG: Bid response email sending failed: {e} - proceeding without email")
        raise e


 