import random
import re
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from schemas.user import UserRegisterForm
from services.user.security.utils import create_jwt_token, JWT_COOKIE_NAME
from models import User, Country
from crud.users.get import get_user_by_email
from api_old.security import hash_password
from api_old.auth_api import EMAIL_VERIFICATION_CODES
from typing import Dict, Any

PENDING_REGISTRATIONS: Dict[str, Dict[str, Any]] = {}

async def send_reset_email(email: str, code: str):
    """Отправка кода для сброса пароля"""
    from api_old.email_utils import send_email
    await send_email(email, code)


async def send_password_changed_notification(email: str):
    """Отправка уведомления об успешной смене пароля"""
    from services.user.email.smtp_client import SMTPClient
    from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD

    smtp_client = SMTPClient(
            host=SMTP_HOST,
            port=SMTP_PORT,
            username=SENDER_EMAIL,
            password=SENDER_PASSWORD
        )

    subject = "Пароль успішно змінено / Password Successfully Changed"
    body = f"""
Ваш пароль було успішно змінено.

Your password has been successfully changed.

Якщо ви не змінювали пароль, зверніться до служби підтримки.
If you did not change your password, please contact support.
        """

    await smtp_client.send_email(email, subject, body)


class UserCreateMixin:
    @staticmethod
    async def register_user(user_form: UserRegisterForm):
        email = user_form.email.strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="Email обязателен")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise HTTPException(status_code=400, detail="Неверный формат email")

        existing_user = await get_user_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

        if not user_form.name or len(user_form.name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Имя должно содержать минимум 2 символа")

        if not user_form.password or len(user_form.password) < 6:
            raise HTTPException(status_code=400, detail="Пароль должен содержать минимум 6 символов")

        if not user_form.city or len(user_form.city.strip()) < 2:
            raise HTTPException(status_code=400, detail="Город обязателен")

        hashed_password = hash_password(user_form.password)
        country = await Country.filter(id=user_form.country).first()

        try:
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            EMAIL_VERIFICATION_CODES[email] = verification_code

            PENDING_REGISTRATIONS[email] = {
                'name': user_form.name.strip(),
                'email': email,
                'password': hashed_password,
                'country': country,
                'city': user_form.city.strip(),
                'role': 0,
                'user_role': 'user',
                'language': user_form.language or 'en'
            }

            from api_old.email_utils import send_email
            await send_email(email, verification_code)

            response = JSONResponse(
                content={
                    "message": "Код верификации отправлен на email. Требуется верификация.",
                    "email": email,
                    "verification_required": True,
                    "debug_code": verification_code
                },
                status_code=201
            )

            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при отправке кода: {str(e)}")

    @staticmethod
    async def verify_email_code(request: Request):
        try:
            data = await request.json()
            email = data.get('email', '').strip().lower()
            submitted_code = data.get('code', '').strip()

            if not email or not submitted_code:
                raise HTTPException(status_code=400, detail="Email и код обязательны")

            expected_code = EMAIL_VERIFICATION_CODES.get(email)

            if not expected_code:
                raise HTTPException(status_code=400, detail="Код верификации не найден или истек")

            if submitted_code != expected_code:
                raise HTTPException(status_code=400, detail="Неверный код верификации")

            if email not in PENDING_REGISTRATIONS:
                raise HTTPException(status_code=400, detail="Данные регистрации не найдены")

            registration_data = PENDING_REGISTRATIONS.pop(email)

            user = await User.create(
                name=registration_data['name'],
                email=registration_data['email'],
                password=registration_data['password'],
                country=registration_data['country'],
                city=registration_data['city'],
                role=registration_data['role'],
                user_role=registration_data['user_role'],
                language=registration_data['language']
            )

            EMAIL_VERIFICATION_CODES.pop(email, None)

            jwt_token = await create_jwt_token(user.id, user.email, user.language, user.role)

            response = JSONResponse(
                content={
                    "message": "Email успешно верифицирован",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "role": user.role,
                        "language": user.language
                    },
                    "token": jwt_token,
                    "verification_completed": True
                },
                status_code=200
            )

            from services.user.email.smtp_client import SMTPClient
            from config import SMTP_HOST, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
            smtp_client = SMTPClient(
                host=SMTP_HOST,
                port=SMTP_PORT,
                username=SENDER_EMAIL,
                password=SENDER_PASSWORD
            )
            subject = "Зареєстровані успішно / Registered Successfully"
            body = f"""
Вітаємо! Ваш акаунт на MakeASAP був успішно створений.

Congratulations! Your MakeASAP account has been successfully registered.
"""
            await smtp_client.send_email(user.email, subject, body)

            response.set_cookie(
                key=JWT_COOKIE_NAME,
                value=jwt_token,
                max_age=60 * 60 * 24 * 7,
                httponly=True,
                secure=False,
                samesite="lax",
                path="/",
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при верификации: {str(e)}")