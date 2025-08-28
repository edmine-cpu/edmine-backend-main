import os
import jwt
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import bcrypt
from fastapi import Request
from models import User
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 60 * 24 * 7
JWT_COOKIE_NAME = 'jwt_token'
BCRYPT_ROUNDS = 12

print(JWT_SECRET_KEY)




def create_jwt_token(data: Dict[str, Any]) -> str:
    """Создает JWT токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def get_current_user(request: Request) -> Optional[User]:
    jwt_token = request.cookies.get(JWT_COOKIE_NAME)
    if not jwt_token:
        return None

    payload = verify_jwt_token(jwt_token)
    if not payload:
        return None

    user_email = payload.get('email')
    if not user_email:
        return None

    user = await User.filter(email=user_email).first()
    return user


def extract_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    return verify_jwt_token(token) 