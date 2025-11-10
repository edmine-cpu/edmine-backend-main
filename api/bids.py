from fastapi import HTTPException, Query, Depends
from typing import List, Optional
from fastapi import APIRouter, Request, Form, UploadFile, File

from schemas.bid import BidVerifyRequest, BidCreateRequest, BidUpdateRequest
from services.bids.service import BidService
from routers.secur import get_current_user
from models.user import User

async def get_current_user_dependency(request: Request):
    return await get_current_user(request)

router = APIRouter()

@router.get("/bids")
async def list_bids(
    category: Optional[str] = Query(None),
    subcategory: Optional[int] = Query(None),
    country: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    sort: Optional[str] = Query("date_desc"),
):
    return await BidService.list_bids(
        category=category,
        subcategory=subcategory,
        country=country,
        city=city,
        search=search,
        limit=limit,
        sort=sort,
    )


@router.get("/bids/{bid_id}")
async def get_bid_by_id(bid_id: int):
    bid = await BidService.get_bid_by_id(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    return bid


@router.post('/{lang}/create-request')
async def create_request(lang: str, request: Request, files: Optional[List[UploadFile]] = File(None)):
    user_role = getattr(request.state, 'user_role', None)
    user_email = getattr(request.state, 'user_email', None)

    form_data = await request.form()
    data = BidCreateRequest(**form_data)

    return await BidService.create_request(data, files, lang, user_role, user_email, request)

@router.post('/{lang}/create-request-fast')
async def create_request_fast(lang: str, request: Request, files: Optional[List[UploadFile]] = File(None)):
    """Fast bid creation with lazy background translation"""
    user_role = getattr(request.state, 'user_role', None)
    user_email = getattr(request.state, 'user_email', None)

    form_data = await request.form()
    data = BidCreateRequest(**form_data)

    return await BidService.create_request_fast(data, files, lang, user_role, user_email, request)


@router.post('/{lang}/verify-request-code')
async def verify_request(lang: str, request: Request):
    form_data = await request.form()
    data = BidVerifyRequest(**form_data)
    return await BidService.verify_request(data, str(request.base_url).rstrip('/'))

@router.post('/submit-response')
async def submit_response(request: Request):
    form_data = await request.form()
    return await BidService.submit_response(
        job_id=int(form_data.get("job_id")),
        name=form_data.get("name"),
        email=form_data.get("email"),
        message=form_data.get("message")
    )


@router.delete('/bid/{bid_id}')
async def delete_bid(request: Request, bid_id: int):
    user_role = getattr(request.state, 'user_role', None)
    return await BidService.delete_bid(bid_id, user_role)


# Эндпоинты для управления заявками пользователя

@router.get('/my-bids')
async def get_my_bids(
    request: Request,
    user: User = Depends(get_current_user_dependency),
    limit: Optional[int] = Query(20, le=100)
):
    """
    Получить все заявки текущего пользователя

    **Параметры:**
    - limit (optional): Количество заявок (максимум 100, по умолчанию 20)

    **Возвращает:**
    - Список заявок пользователя, отсортированных по дате создания (новые первыми)
    - add_button: URL для создания новой заявки
    """
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    bids = await BidService.get_user_bids(user.id, limit)

    # Получаем язык пользователя для создания правильного URL
    lang = user.language if user.language else 'en'

    return {
        "bids": bids,
        "add_button": {
            "label": "Add Request",
            "url": f"/{lang}/create-request",
            "style": "red"  # Указываем, что кнопка должна быть красной
        }
    }


@router.put('/my-bids/{bid_id}')
async def update_my_bid(
    bid_id: int,
    request: Request,
    user: User = Depends(get_current_user_dependency)
):
    """
    Обновить свою заявку

    **Параметры:**
    - bid_id: ID заявки для обновления
    - Form data: Поля для обновления (см. BidUpdateRequest)

    **Поля для обновления (все опциональные):**
    - title_uk, title_en, title_pl, title_fr, title_de: Заголовки на разных языках
    - description_uk, description_en, description_pl, description_fr, description_de: Описания
    - country: ID страны
    - city: ID города
    - budget: Бюджет
    - budget_type: Тип бюджета
    - category: Список ID категорий (через запятую или массив)
    - under_category: Список ID подкатегорий (через запятую или массив)

    **Возвращает:**
    - success: true
    - message: Сообщение об успехе

    **Примечание:**
    - Автоматически переводит пустые языковые поля
    - Автоматически обновляет slug'и
    - Пользователь может редактировать только свои заявки
    """
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    form_data = await request.form()
    data = BidUpdateRequest(**form_data)

    # Фильтруем только те поля, которые были переданы
    update_data = {k: v for k, v in data.dict().items() if v is not None}

    # Преобразуем категории и подкатегории в нужный формат
    if 'category' in update_data:
        update_data['categories'] = update_data.pop('category')
    if 'under_category' in update_data:
        update_data['under_categories'] = update_data.pop('under_category')

    return await BidService.update_user_bid(bid_id, user.id, update_data)


@router.delete('/my-bids/{bid_id}')
async def delete_my_bid(
    bid_id: int,
    user: User = Depends(get_current_user_dependency)
):
    """
    Удалить свою заявку

    **Параметры:**
    - bid_id: ID заявки для удаления

    **Возвращает:**
    - success: true
    - message: Сообщение об успехе

    **Примечание:**
    - Автоматически удаляет все прикрепленные файлы
    - Пользователь может удалять только свои заявки
    """
    if not user:
        raise HTTPException(status_code=401, detail="Необходима авторизация")

    return await BidService.delete_user_bid(bid_id, user.id)
