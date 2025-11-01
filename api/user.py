from fastapi import APIRouter, Request, Response, Depends, HTTPException, Query, Form
from typing import Optional, List

from services.user.security.utils import JWT_COOKIE_NAME
from services.user.service import UserServices
from schemas.user import UserRegisterForm, UserLoginForm
from routers.secur import get_current_user
from models.user import User

async def get_current_user_dependency(request: Request):
    return await get_current_user(request)


router = APIRouter()


@router.get("/users")
async def get_users(search: Optional[str] = Query(None)):
    users = await UserServices.get_users(search=search)
    return users


@router.get("/user/{id}")
async def get_user(id: int):
    user = await UserServices.get_user_by_id(id=id)
    return user


@router.post('/register')
async def register_post(
    name: str = Form(...),
    email: str = Form(...),
    country: int = Form(...),
    city: str = Form(...),
    password: str = Form(...),
    role: Optional[str] = Form('user'),
    language: Optional[str] = Form('en'),
    categories: Optional[List[str]] = Form(None),
    subcategories: Optional[List[str]] = Form(None)
):
    form_data = UserRegisterForm(
        name=name,
        email=email,
        country=country,
        city=city,
        password=password,
        role=role,
        language=language,
        categories=categories or [],
        subcategories=subcategories or []
    )
    return await UserServices.register_user(form_data)


@router.post("/login")
async def login_post(login_data: UserLoginForm):
    return await UserServices.authenticate_user(login_data)


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key= JWT_COOKIE_NAME, httponly=True, samesite="lax", secure=False, path="/")
    return {"detail": "Logged out"}


@router.post('/verify-code')
async def verify_code_post(request: Request):
    return await UserServices.verify_email_code(request)


@router.get("/me")
async def get_current_user_info(user: User = Depends(get_current_user_dependency)):
    """Get current user information"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "language": user.language,
        "city": user.city
    }