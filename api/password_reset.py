from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from models import User, PasswordResetToken
import random

router = APIRouter()

# === Тестовый endpoint ===
@router.get("/test-password-reset")
async def test_password_reset():
    return {"message": "Password reset API is working"}


# === Утилиты для отправки писем ===
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


# === Вспомогательная функция для универсального парсинга запроса ===
async def parse_request(request: Request):
    """Пытаемся распарсить JSON, если не получилось — form-data"""
    try:
        data = await request.json()
        print(f"DEBUG: JSON data: {data}")
    except Exception:
        form = await request.form()
        data = dict(form)
        print(f"DEBUG: Form data: {data}")
    return data


# === Запрос на сброс пароля ===
@router.post("/forgot-password")
async def forgot_password(email: str = Form(...)):
    try:
        user = await User.get_or_none(email=email.lower().strip())
        # Всегда возвращаем успех для безопасности
        if not user:
            return JSONResponse({"message": "Password reset requested successfully", "email": email})

        # Генерация кода
        verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        print(f"DEBUG: Generated verification code for {email}: {verification_code}")

        # Сохраняем код в памяти
        from api_old.auth_api import EMAIL_VERIFICATION_CODES
        EMAIL_VERIFICATION_CODES[email] = verification_code

        # Отправка письма
        await send_reset_email(email, verification_code)

        return JSONResponse({"message": "Password reset requested successfully", "email": email})

    except Exception as e:
        print(f"Error in forgot_password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# === Проверка кода сброса пароля ===
@router.post("/verify-reset-code")
async def verify_reset_code(email: str = Form(...), code: str = Form(...)):
    try:
        from api_old.auth_api import EMAIL_VERIFICATION_CODES
        expected_code = EMAIL_VERIFICATION_CODES.get(email)

        if not expected_code or code != expected_code:
            raise HTTPException(status_code=400, detail="Invalid code")

        user = await User.get_or_none(email=email.lower().strip())
        if not user:
            raise HTTPException(status_code=400, detail="Invalid code")

        # Очищаем код
        EMAIL_VERIFICATION_CODES.pop(email, None)

        return JSONResponse({"message": "Code verified successfully", "email": email})

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in verify_reset_code: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# === Сброс пароля ===
@router.post("/reset-password")
async def reset_password(request: Request):
    data = await parse_request(request)

    email = data.get("email")
    token = data.get("token")
    new_password = data.get("new_password") or data.get("newPassword") or data.get("password")

    if not new_password:
        raise HTTPException(status_code=422, detail="Password is required")
    if len(new_password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")

    user = await User.get_or_none(email=email.lower().strip())
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Хеширование пароля
    from api_old.security import hash_password
    hashed_password = hash_password(new_password)

    user.password = hashed_password
    await user.save()

    # Уведомление о смене пароля
    try:
        await send_password_changed_notification(email)
    except Exception as e:
        print(f"DEBUG: Failed to send password change notification: {e}")

    return JSONResponse({"message": "Password successfully reset"})


# === Проверка токена сброса пароля ===
@router.get("/verify-reset-token")
async def verify_reset_token(token: str):
    try:
        reset_token = await PasswordResetToken.get_or_none(token=token)
        if not reset_token or not await reset_token.is_valid():
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = await User.get(id=reset_token.user_id)
        return JSONResponse({
            "valid": True,
            "email": user.email,
            "expires_at": reset_token.expires_at.isoformat()
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in verify_reset_token: {e}")
        raise HTTPException(status_code=400, detail="Invalid token")
