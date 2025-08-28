import re

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from config import JWT_COOKIE_NAME
from models.user import User
from schemas.user import UserLoginForm
from services.user.security.utils import create_jwt_token, verify_password


class AuthMixin:
    @staticmethod
    async def authenticate_user(form_data: UserLoginForm):
        email = form_data.email.strip().lower()
        password = form_data.password

        # Валидация email
        if not email:
            raise HTTPException(status_code=400, detail="Email обязателен")

        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            raise HTTPException(status_code=400, detail="Неверный формат email")

        # Валидация пароля
        if not password:
            raise HTTPException(status_code=400, detail="Пароль обязателен")

        if len(password) < 6:
            raise HTTPException(
                status_code=400, detail="Пароль должен содержать минимум 6 символов"
            )

        # Поиск пользователя напрямую в базе данных
        user = await User.get_or_none(email=email)
        if not user:
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        # Проверка пароля
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")

        return await AuthMixin._create_authenticated_response(user)

    @staticmethod
    async def _create_authenticated_response(user):
        print(f"DEBUG: Creating authenticated response for user {user.email}")

        jwt_token = await create_jwt_token(
            user.id, user.email, user.language, int(user.role)
        )
        response = JSONResponse(
            content={
                "message": "Успешный вход",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "language": user.language,
                },
                "token": jwt_token,
            },
            status_code=200,
        )
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
