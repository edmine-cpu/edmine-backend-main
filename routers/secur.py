from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError as JWTError
from typing import Optional
from models import User
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET_KEY = os.environ.get('JWT_SECRET') or 'my-secret-key-123'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_MINUTES = 60 * 24 * 7
JWT_COOKIE_NAME = 'jwt_token'
BCRYPT_ROUNDS = 12

security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request) -> Optional[User]:
    token = None
    
    if request:
        token = request.cookies.get(JWT_COOKIE_NAME)
    
    if not token and request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
    except (ExpiredSignatureError, JWTError):
        return None

    user = await User.get_or_none(id=user_id)
    return user



@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=JWT_COOKIE_NAME, 
        path="/",
        secure=True,
        httponly=True,
        samesite="none"
    )
    return {"message": "Logout successful"}


@router.get("/me")
async def read_current_user(request: Request):
    current_user = await get_current_user(request)
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        await current_user.fetch_related("categories", "subcategories")
    except Exception as e:
        pass
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "user_role": current_user.user_role,
        "profile_description": current_user.profile_description,
        "categories": current_user.categories,
        "subcategories": current_user.subcategories,
    }
