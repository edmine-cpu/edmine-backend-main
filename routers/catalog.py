from typing import List, Optional, Union
from fastapi import APIRouter, Request, Query, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from models.actions import Bid
from models.categories import Category, UnderCategory
from models.user import User
from models.places import City
from tortoise.expressions import Q
from db.cities import LOCATIONS
from tortoise.exceptions import DoesNotExist
from api.url_utils import (
    get_category_from_slug, 
    get_subcategory_from_slug, 
    parse_catalog_url,
    build_catalog_url,
    get_category_slug,
    get_subcategory_slug
)

router = APIRouter()
templates = Jinja2Templates(directory='templates')


@router.post('/{lang}/performer/{user_id}/edit', response_model=None)
async def edit_performer_save(
    request: Request,
    lang: str,
    user_id: int,
    name: str = Form(...),
    city: str = Form(...),
    language: str = Form(...)
):
    user_role = getattr(request.state, 'user_role', None)
    user_email = getattr(request.state, 'user_email', None)

    try:
        user = await User.get(id=user_id)
        
        if user_role != 1 and user.email != user_email:
            return templates.TemplateResponse('error.html', {
                'request': request,
                'error': 'Недостатньо прав'
            })

        ация данных
        if not name.strip() or not city.strip():
            return templates.TemplateResponse('edit_performer.html', {
                'request': request,
                'user': user,
                'error': 'Всі поля обов\'язкові'
            })

        user.name = name.strip()
        user.city = city.strip()
        user.language = language.strip()
        await user.save()

        return RedirectResponse(url=f'/{lang}/performers', status_code=302)

    except DoesNotExist:
        return templates.TemplateResponse('error.html', {
            'request': request,
            'error': 'Виконавця не знайдено'
        })

@router.post('/{lang}/performer/{user_id}/delete')
async def delete_performer_new(request: Request, lang: str, user_id: int):
    """Удаление исполнителя (только для админов)"""
    user_role = getattr(request.state, 'user_role', None)
    
    if user_role != 1:
        return JSONResponse({'error': 'Недостатньо прав'}, status_code=403)
    
    try:
        user = await User.get(id=user_id)
        await user.delete()
        return JSONResponse({'success': True})
    except DoesNotExist:
        return JSONResponse({'error': 'Користувача не знайдено'}, status_code=404)
    except Exception as e:
        return JSONResponse({'error': f'Помилка: {str(e)}'}, status_code=500)


@router.post('/{lang}/bid/{bid_id}/delete')
async def delete_bid(request: Request, lang: str, bid_id: int):
    """Удаление заявки (только для админов)"""
    user_role = getattr(request.state, 'user_role', None)
    
    if user_role != 1:
        return JSONResponse({'error': 'Недостатньо прав'}, status_code=403)
    
    try:
        bid = await Bid.get(id=bid_id)
        await bid.delete()
        return JSONResponse({'success': True})
    except DoesNotExist:
        return JSONResponse({'error': 'Заявку не знайдено'}, status_code=404)
    except Exception as e:
        return JSONResponse({'error': f'Помилка: {str(e)}'}, status_code=500) 