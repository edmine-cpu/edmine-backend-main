from fastapi import HTTPException, Query
from typing import List, Optional
from fastapi import APIRouter, Request, Form, UploadFile, File

from schemas.bid import BidVerifyRequest, BidCreateRequest
from services.bids.service import BidService

router = APIRouter()

@router.get("/bids")
async def list_bids(
    category: Optional[str] = Query(None),
    subcategory: Optional[int] = Query(None),
    country: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    sort: Optional[str] = Query("date_desc"),  # date_desc | date_asc
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
    """Получить заявку по ID"""
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

    print(f"DEBUG: Budget from form: {data.budget}")

    return await BidService.create_request(data, files, lang, user_role, user_email, request)


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


# @router.post('/{lang}/bid/{bid_id}/edit')
# async def edit_bid(
#         request: Request,
#         lang: str,
#         bid_id: int,
#         title: Optional[str] = Form(None),
#         category: Optional[str] = Form(None),
#         description: Optional[str] = Form(None),
#         city: Optional[str] = Form(None),
#         files: Optional[List[UploadFile]] = File(None)
# ):
#     user_role = getattr(request.state, 'user_role', None)
#
#     if user_role != 1:
#         return templates.TemplateResponse('error.html', {
#             'request': request,
#             'error': 'Недостатньо прав'
#         })
#
#     try:
#         bid = await Bid.get(id=bid_id)
#         categories = await Category.all()
#
#         # Проверяем и обновляем основные поля
#         if not title or not title.strip():
#             return templates.TemplateResponse('edit_request.html', {
#                 'request': request,
#                 'error': 'Назва заявки обов\'язкова',
#                 'bid': bid,
#                 'categories': categories,
#                 'user_role': user_role
#             })
#
#         if not category or not category.strip():
#             return templates.TemplateResponse('edit_request.html', {
#                 'request': request,
#                 'error': 'Категорія обов\'язкова',
#                 'bid': bid,
#                 'categories': categories,
#                 'user_role': user_role
#             })
#
#         if not description or not description.strip():
#             return templates.TemplateResponse('edit_request.html', {
#                 'request': request,
#                 'error': 'Опис завдання обов\'язковий',
#                 'bid': bid,
#                 'categories': categories,
#                 'user_role': user_role
#             })
#
#         if not city or not city.strip():
#             return templates.TemplateResponse('edit_request.html', {
#                 'request': request,
#                 'error': 'Місто обов\'язкове',
#                 'bid': bid,
#                 'categories': categories,
#                 'user_role': user_role
#             })
#
#         # Обновляем основные поля для всех языков
#         title_primary = title.strip()
#         description_primary = description.strip()
#
#         # Устанавливаем значения для основного языка
#         if lang == 'uk':
#             bid.title_uk = title_primary
#             bid.description_uk = description_primary
#         elif lang == 'en':
#             bid.title_en = title_primary
#             bid.description_en = description_primary
#         elif lang == 'pl':
#             bid.title_pl = title_primary
#             bid.description_pl = description_primary
#         elif lang == 'fr':
#             bid.title_fr = title_primary
#             bid.description_fr = description_primary
#         elif lang == 'de':
#             bid.title_de = title_primary
#             bid.description_de = description_primary
#
#         # Автоматический перевод на другие языки
#         from api.translation_utils import translate_text
#
#         for target_lang in ['uk', 'en', 'pl', 'fr', 'de']:
#             if target_lang != lang:
#                 try:
#                     # Переводим заголовок
#                     translated_title = await translate_text(title_primary, lang, target_lang)
#                     setattr(bid, f'title_{target_lang}', translated_title)
#
#                     # Переводим описание
#                     translated_description = await translate_text(description_primary, lang, target_lang)
#                     setattr(bid, f'description_{target_lang}', translated_description)
#                 except Exception as e:
#                     print(f"Translation error for {target_lang}: {e}")
#                     # Если перевод не удался, используем оригинальный текст
#                     setattr(bid, f'title_{target_lang}', title_primary)
#                     setattr(bid, f'description_{target_lang}', description_primary)
#
#         category_id = await _process_category_id(category)
#         if category_id is not None:
#             bid.category = str(category_id)
#         bid.city = city.strip()
#
#         # Обработка новых файлов
#         if files:
#             new_file_paths = []
#             for file in files:
#                 # Проверяем расширение файла
#                 if not file.filename:
#                     continue
#
#                 file_ext = os.path.splitext(file.filename)[1].lower()
#                 if file_ext not in ['.jpg', '.jpeg', '.png', '.webp', '.svg', '.pdf', '.bmp', '.gif']:
#                     return templates.TemplateResponse('edit_request.html', {
#                         'request': request,
#                         'error': f'Непідтримуваний тип файлу: {file_ext}',
#                         'bid': bid,
#                         'categories': categories,
#                         'user_role': user_role
#                     })
#
#                 if file.size and file.size > 10 * 1024 * 1024:
#                     return templates.TemplateResponse('edit_request.html', {
#                         'request': request,
#                         'error': 'Розмір файлу не може перевищувати 10MB',
#                         'bid': bid,
#                         'categories': categories,
#                         'user_role': user_role
#                     })
#
#                 # Генерируем безопасное имя файла
#                 safe_filename = secrets.token_urlsafe(16).replace('-', '_').replace('=', '_') + file_ext
#                 file_path = os.path.join(BID_FILES_DIR, safe_filename)
#
#                 # Сохраняем файл
#                 os.makedirs(BID_FILES_DIR, exist_ok=True)
#                 content = await file.read()
#                 with open(file_path, 'wb') as f:
#                     f.write(content)
#
#                 new_file_paths.append(file_path)
#
#             # Объединяем существующие и новые файлы
#             current_files = bid.files or []
#             bid.files = current_files + new_file_paths
#
#         await bid.save()
#         return RedirectResponse(url=f'/{lang}/admins', status_code=302)
#
#     except DoesNotExist:
#         return templates.TemplateResponse('error.html', {
#             'request': request,
#             'error': 'Заявку не знайдено'
#         })
#
#
