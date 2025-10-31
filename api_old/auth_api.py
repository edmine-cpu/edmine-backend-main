from pydantic import BaseModel
import time
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from models.user import User
from models.categories import Category, UnderCategory
from models.places import Country
from api_old.email_utils import send_email, generate_code
from api_old.security import hash_password, verify_password, create_jwt_token
from api_old.translation_utils import auto_translate_company_fields
from schemas.user import UserRegisterForm

PENDING_REGISTRATIONS: Dict[str, Dict[str, Any]] = {}
EMAIL_VERIFICATION_CODES: Dict[str, Dict[str, Any]] = {}
PENDING_LOGIN_ATTEMPTS: set = set()

templates = Jinja2Templates(directory='templates')

JWT_COOKIE_NAME = 'jwt_token'
JWT_COOKIE_MAX_AGE = 60 * 60 * 24 * 7
DEFAULT_USER_ROLE = 0  # 0 - обычный пользователь, 1 - админ
MIN_PASSWORD_LENGTH = 8








async def verify_email_code(request: Request):
    data = await request.json()
    email = data.get('email')
    submitted_code = data.get('code')

    verification_data = EMAIL_VERIFICATION_CODES.get(email)
    expected_code = verification_data.get('code') if verification_data else None

    if not expected_code or submitted_code != expected_code:
        return JSONResponse({'error': 'Невірний код підтвердження'}, status_code=400)

    if email not in PENDING_REGISTRATIONS:
        return JSONResponse({'error': 'Користувача не знайдено або вже підтверджено'}, status_code=400)

    registration_data = PENDING_REGISTRATIONS.pop(email)

    try:
        company_name = registration_data['name']
        lang = registration_data['language']

        translated_company = await auto_translate_company_fields(
            name_uk=company_name if lang == 'uk' else None,
            name_en=company_name if lang == 'en' else None,
            name_pl=company_name if lang == 'pl' else None,
            name_fr=company_name if lang == 'fr' else None,
            name_de=company_name if lang == 'de' else None,
            description_uk=None,
            description_en=None,
            description_pl=None,
            description_fr=None,
            description_de=None
        )

        country = None
        if registration_data.get('country'):
            country = await Country.filter(id=registration_data['country']).first()

        user = await User.create(
            name=registration_data['name'],
            email=registration_data['email'],
            city=registration_data['city'],
            country=country,
            password=registration_data['password'],
            language=lang,
            role=DEFAULT_USER_ROLE,
            company_name_uk=translated_company['company_name_uk'],
            company_name_en=translated_company['company_name_en'],
            company_name_pl=translated_company['company_name_pl'],
            company_name_fr=translated_company['company_name_fr'],
            company_name_de=translated_company['company_name_de'],
            company_description_uk=translated_company['company_description_uk'],
            company_description_en=translated_company['company_description_en'],
            company_description_pl=translated_company['company_description_pl'],
            company_description_fr=translated_company['company_description_fr'],
            company_description_de=translated_company['company_description_de'],
            auto_translated_fields=translated_company['auto_translated_fields']
        )

        if registration_data['categories']:
            category_objs = await Category.filter(name__in=registration_data['categories'])
            await user.categories.add(*category_objs)

        if registration_data['subcategories']:
            subcategory_objs = await UnderCategory.filter(id__in=registration_data['subcategories'])
            await user.subcategories.add(*subcategory_objs)

        EMAIL_VERIFICATION_CODES.pop(email, None)

        try:
            print(f"DEBUG: Attempting to send account creation notification to {user.email}")
            from api_old.email_utils import send_account_created_notification
            await send_account_created_notification(user.email)
            print(f"DEBUG: Account creation notification sent successfully!")
        except Exception as e:
            print(f"DEBUG: Failed to send account creation notification: {e}")
            import traceback
            traceback.print_exc()

        jwt_token = await create_jwt_token(user.id, user.email, user.language, int(user.role))
        response = JSONResponse({'message': 'User verified', 'token': jwt_token})
        response.set_cookie(
            key=JWT_COOKIE_NAME,
            value=jwt_token,
            httponly=True,
            max_age=JWT_COOKIE_MAX_AGE,
            samesite='lax'
        )
        return response

    except Exception as e:
        return JSONResponse({'error': f'Помилка створення користувача: {e}'}, status_code=500)

    except Exception as e:
        print(f"DEBUG: Error creating user: {e}")
        return templates.TemplateResponse('verify_code.html', {
            'request': request,
            'error': 'Помилка створення користувача',
            'email': email
        })


# async def logout_user():
#     response.delete_cookie("jwt_token")
#     return response


def _render_login_error(request: Request, error_message: str) -> HTMLResponse:
    return templates.TemplateResponse('login.html', {
        'request': request,
        'error': error_message
    })


async def _render_register_error(request: Request, error_message: str) -> HTMLResponse:
    categories = await Category.all()
    subcategories = await UnderCategory.all().prefetch_related('full_category')
    return templates.TemplateResponse('register.html', {
        'request': request,
        'error': error_message,
        'categories': categories,
        'subcategories': subcategories
    })








