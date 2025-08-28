import random
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from schemas.user import UserRegisterForm
from services.user.security.utils import create_jwt_token, JWT_COOKIE_NAME
from models import User, Country
from crud.users.get import get_user_by_email


async def send_reset_email(email: str, code: str):
    """Отправка кода для сброса пароля"""
    try:
        from api_old.email_utils import send_email
        print(f"DEBUG: Sending email to {email} with code {code}")
        await send_email(email, code)
        print("DEBUG: Email sent successfully!")
    except Exception as e:
        print(f"DEBUG: Failed to send reset email: {e}")


async def send_password_changed_notification(email: str):
    """Отправка уведомления об успешной смене пароля"""
    try:
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
        print(f"DEBUG: Password change notification sent to {email}!")
    except Exception as e:
        print(f"DEBUG: Password change notification failed: {e}")


class UserCreateMixin:
    @staticmethod
    async def register_user(user_form: UserRegisterForm):
        import re
        from fastapi import HTTPException
        from fastapi.responses import JSONResponse
        from api_old.security import hash_password
        from models.user import User
        from api_old.auth_api import EMAIL_VERIFICATION_CODES

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
            user = await User.create(
                name=user_form.name.strip(),
                email=email,
                password=hashed_password,
                country=country,
                city=user_form.city.strip(),
                role=0,
                user_role='user',
                language=user_form.language or 'en'
            )

            # Generate verification code and ensure it's properly stored
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            print(f"DEBUG: Generated verification code for {user.email}: {verification_code}")

            # Store the code BEFORE sending email
            EMAIL_VERIFICATION_CODES[email] = verification_code
            print(f"DEBUG: Stored verification code in dict: {EMAIL_VERIFICATION_CODES.get(email)}")

            try:
                from api_old.email_utils import send_email
                print(f"DEBUG: Attempting to send verification email to {user.email} with code: {verification_code}")
                await send_email(user.email, verification_code)
                print(f"DEBUG: Verification email sent successfully! CODE: {verification_code}")
            except Exception as e:
                print(f"DEBUG: Verification email sending failed: {e}")

            response = JSONResponse(
                content={
                    "message": "Пользователь зарегистрирован. Требуется верификация email.",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "role": user.role,
                        "language": user.language
                    },
                    "verification_required": True,
                    "debug_code": verification_code  # Только для разработки
                },
                status_code=201
            )

            return response

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при создании пользователя: {str(e)}")

    @staticmethod
    async def verify_email_code(request: Request):
        try:
            data = await request.json()
            email = data.get('email', '').strip().lower()  # Normalize email
            submitted_code = data.get('code', '').strip()  # Strip whitespace

            print(f"DEBUG: Verification attempt - Email: {email}, Code: {submitted_code}")

            if not email or not submitted_code:
                raise HTTPException(status_code=400, detail="Email и код обязательны")

            from api_old.auth_api import EMAIL_VERIFICATION_CODES
            expected_code = EMAIL_VERIFICATION_CODES.get(email)

            print(f"DEBUG: Expected code: {expected_code}, Submitted code: {submitted_code}")
            print(f"DEBUG: Current EMAIL_VERIFICATION_CODES dict: {EMAIL_VERIFICATION_CODES}")

            if not expected_code:
                raise HTTPException(status_code=400, detail="Код верификации не найден или истек")

            if submitted_code != expected_code:
                print(f"DEBUG: Code mismatch - Expected: '{expected_code}', Got: '{submitted_code}'")
                raise HTTPException(status_code=400, detail="Неверный код верификации")

            user = await User.get_or_none(email=email)
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")

            # Remove the code only after successful verification
            EMAIL_VERIFICATION_CODES.pop(email, None)
            print(f"DEBUG: Verification successful, removed code for {email}")

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

            try:
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
                print(f"DEBUG: Registration notification sent to {email}!")
            except Exception as e:
                print(f"DEBUG: Failed to send registration notification: {e}")

            response.set_cookie(
                key=JWT_COOKIE_NAME,
                value=jwt_token,
                max_age=60 * 60 * 24 * 7,  # 7 дней
                httponly=True,
                secure=True,
                samesite="none",
                path="/",
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            print(f"DEBUG: Verification error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Ошибка при верификации: {str(e)}")