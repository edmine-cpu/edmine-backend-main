# from typing import List, Optional, Dict, Any
# from fastapi import APIRouter, Request, Form, UploadFile, File
# from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
# from fastapi.templating import Jinja2Templates
# from models.actions import Bid
# from models.categories import Category, UnderCategory
# from tortoise.exceptions import DoesNotExist
# import secrets
# import os
# from api_old.email_utils import (
#     send_bid_confirmation_email,
#     send_email,
#     generate_code,
#     can_send_code,
#     send_bid_response_email
# )
# from api_old.translation_utils import auto_translate_bid_fields
# from api_old.slug_utils import generate_bid_slugs
# import random
# from services.bids.service import BidServices
#
#
# router = APIRouter()
# templates = Jinja2Templates(directory='templates')
#
# PENDING_REQUESTS: Dict[str, Dict[str, Any]] = {}
# EMAIL_VERIFICATION_CODES: Dict[str, str] = {}
#
# MAX_FILES_COUNT = 10
# ALLOWED_FILE_TYPES = {
#     'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml',
#     'application/pdf', 'image/bmp', 'image/gif'
# }
# TEMP_FILES_DIR = 'static/tmp_files'
# BID_FILES_DIR = 'static/bid_files'
# DELETE_TOKEN_LENGTH = 32
#
#
#
# @router.post('/{lang}/create-request')
# async def handle_create_request(
#     request: Request,
#     lang: str,
#     files: Optional[List[UploadFile]] = File(None)
# ):
#     print(f"DEBUG: Frontend router called with lang={lang}")
#     user_role = getattr(request.state, 'user_role', None)
#     user_email = getattr(request.state, 'user_email', None)
#     print(f"DEBUG: user_role={user_role}, user_email={user_email}")
#     form_data = await request.form()
#     print(f"DEBUG: form_data keys: {list(form_data.keys())}")
#
#     title_primary = form_data.get(f'title_{lang}')  # Основной язык из URL
#     title_uk = form_data.get('title_uk', '')
#     title_en = form_data.get('title_en', '')
#     title_pl = form_data.get('title_pl', '')
#     title_fr = form_data.get('title_fr', '')
#     title_de = form_data.get('title_de', '')
#
#     description_primary = form_data.get(f'description_{lang}')
#     description_uk = form_data.get('description_uk', '')
#     description_en = form_data.get('description_en', '')
#     description_pl = form_data.get('description_pl', '')
#     description_fr = form_data.get('description_fr', '')
#     description_de = form_data.get('description_de', '')
#
#     if lang == 'uk':
#         title_uk = title_primary or title_uk
#         description_uk = description_primary or description_uk
#         title_primary = title_uk
#         description_primary = description_uk
#     elif lang == 'en':
#         title_en = title_primary or title_en
#         description_en = description_primary or description_en
#         title_primary = title_en
#         description_primary = description_en
#     elif lang == 'pl':
#         title_pl = title_primary or title_pl
#         description_pl = description_primary or description_pl
#         title_primary = title_pl
#         description_primary = description_pl
#
#     category = form_data.get('category') or ''
#     under_category = form_data.get('under_category') or ''
#     country = form_data.get('country') or ''
#     city = form_data.get('city') or ''
#     budget = form_data.get('budget') or ''
#     currency = form_data.get('currency') or ''
#     email = form_data.get('email') or user_email
#
#     # Отладка
#     print(f"DEBUG: Received form data for language '{lang}':")
#     print(f"  title_primary ({lang}): '{title_primary}'")
#     print(f"  title_uk: '{title_uk}'")
#     print(f"  title_en: '{title_en}'")
#     print(f"  title_pl: '{title_pl}'")
#     print(f"  description_primary ({lang}): '{description_primary}'")
#     print(f"  description_uk: '{description_uk}'")
#     print(f"  description_en: '{description_en}'")
#     print(f"  description_pl: '{description_pl}'")
#     print(f"  category: '{category}'")
#     print(f"  under_category: '{under_category}'")
#     print(f"  country: '{country}'")
#     print(f"  city: '{city}'")
#     print(f"  email: '{email}'")
#
#     if files:
#         files = [file for file in files if file.filename and file.filename.strip() != '']
#     else:
#         files = []
#
#     errors = []
#     if not title_primary or not title_primary.strip():
#         if lang == 'uk':
#             errors.append('Назва заявки обов\'язкова')
#         elif lang == 'en':
#             errors.append('Request title is required')
#         elif lang == 'pl':
#             errors.append('Tytuł zlecenia jest wymagany')
#
#     if not description_primary or not description_primary.strip():
#         if lang == 'uk':
#             errors.append('Опис завдання обов\'язковий')
#         elif lang == 'en':
#             errors.append('Task description is required')
#         elif lang == 'pl':
#             errors.append('Opis zadania jest wymagany')
#
#     if not email:
#         if lang == 'uk':
#             errors.append('Email обов\'язковий')
#         elif lang == 'en':
#             errors.append('Email is required')
#         elif lang == 'pl':
#             errors.append('Email jest wymagany')
#
#     form_dict = {
#         f'title_{lang}': title_primary or '',
#         'title_uk': title_uk,
#         'title_en': title_en,
#         'title_pl': title_pl,
#         'title_fr': title_fr,
#         'title_de': title_de,
#         f'description_{lang}': description_primary or '',
#         'description_uk': description_uk,
#         'description_en': description_en,
#         'description_pl': description_pl,
#         'description_fr': description_fr,
#         'description_de': description_de,
#         'category': category or '',
#         'under_category': under_category or '',
#         'city': city or '',
#         'email': email or '',
#     }
#
#     if errors:
#         return JSONResponse({
#             "success": False,
#             "error": ' | '.join(errors)
#         }, status_code=400)
#
#     print(f"DEBUG: Applying auto-translation...")
#     translated_fields = await auto_translate_bid_fields(
#         title_uk=title_uk,
#         title_en=title_en,
#         title_pl=title_pl,
#         title_fr=title_fr,
#         title_de=title_de,
#         description_uk=description_uk,
#         description_en=description_en,
#         description_pl=description_pl,
#         description_fr=description_fr,
#         description_de=description_de
#     )
#
#     title_uk = translated_fields['title_uk'] or ''
#     title_en = translated_fields['title_en'] or ''
#     title_pl = translated_fields['title_pl'] or ''
#     title_fr = translated_fields['title_fr'] or ''
#     title_de = translated_fields['title_de'] or ''
#     description_uk = translated_fields['description_uk'] or ''
#     description_en = translated_fields['description_en'] or ''
#     description_pl = translated_fields['description_pl'] or ''
#     description_fr = translated_fields['description_fr'] or ''
#     description_de = translated_fields['description_de'] or ''
#
#     print(f"DEBUG: After auto-translation:")
#     print(f"  title_uk: '{title_uk}'")
#     print(f"  title_en: '{title_en}'")
#     print(f"  title_pl: '{title_pl}'")
#     print(f"  description_uk: '{description_uk}'")
#     print(f"  description_en: '{description_en}'")
#     print(f"  description_pl: '{description_pl}'")
#     print(f"  auto_translated_fields: {translated_fields['auto_translated_fields']}")
#
#     # Чистим строки
#     title_uk = title_uk.strip() if title_uk else ''
#     title_en = title_en.strip() if title_en else ''
#     title_pl = title_pl.strip() if title_pl else ''
#     title_fr = title_fr.strip() if title_fr else ''
#     title_de = title_de.strip() if title_de else ''
#     description_uk = description_uk.strip() if description_uk else ''
#     description_en = description_en.strip() if description_en else ''
#     description_pl = description_pl.strip() if description_pl else ''
#     description_fr = description_fr.strip() if description_fr else ''
#     description_de = description_de.strip() if description_de else ''
#     category = category.strip()
#     under_category = under_category.strip() if under_category else None
#     city = city.strip()
#     email = email.strip()
#
#     category_id = None if not category or category.strip() == '' else int(category)
#     print(f"DEBUG: Category processing skipped, category='{category}', id={category_id}")
#
#     under_category_id = None if not under_category or under_category.strip() == '' else int(under_category)
#     print(f"DEBUG: Under-category processing skipped, under_category='{under_category}', id={under_category_id}")
#
#     file_validation_result = await _validate_uploaded_files(request, files, user_role, user_email, lang, form_dict)
#     if isinstance(file_validation_result, HTMLResponse):
#         return file_validation_result
#     temp_file_paths = file_validation_result
#
#     form_id = secrets.token_urlsafe(16)
#
#
#     verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#     print(f"DEBUG: Generated verification code for {email}: {verification_code}")
#
#     EMAIL_VERIFICATION_CODES[email] = verification_code
#     country_obj = None
#     if country:
#         from models.places import Country
#         country_obj = await Country.filter(id=country).first()
#
#     PENDING_REQUESTS[email] = {
#         'title_uk': title_uk,
#         'title_en': title_en,
#         'title_pl': title_pl,
#         'title_fr': title_fr,
#         'title_de': title_de,
#         'category': category_id,
#         'under_category': under_category_id,
#         'country': country_obj,
#         'description_uk': description_uk,
#         'description_en': description_en,
#         'description_pl': description_pl,
#         'description_fr': description_fr,
#         'description_de': description_de,
#         'city': city,
#         'email': email,
#         'temp_files': temp_file_paths,
#         'form_id': form_id,
#         'auto_translated_fields': translated_fields['auto_translated_fields']
#     }
#
#     try:
#         print(f"DEBUG: Attempting to send email to {email}")
#         await send_email(email, verification_code)
#         print(f"DEBUG: Email sent successfully!")
#
#         return JSONResponse({
#             "success": True,
#             "message": "Код підтвердження відправлено на ваш email",
#             "requires_verification": True
#         })
#
#     except Exception as e:
#         print(f"DEBUG: Email sending failed: {e} - proceeding without email")
#         print("DEBUG: Fallback to direct bid creation")
#
#
#         payload = {
#             "titles": {
#                 "uk": (title_uk or '').strip(),
#                 "en": (title_en or '').strip(),
#                 "pl": (title_pl or '').strip(),
#                 "fr": (title_fr or '').strip(),
#                 "de": (title_de or '').strip(),
#             },
#             "descriptions": {
#                 "uk": (description_uk or '').strip(),
#                 "en": (description_en or '').strip(),
#                 "pl": (description_pl or '').strip(),
#                 "fr": (description_fr or '').strip(),
#                 "de": (description_de or '').strip(),
#             },
#             "category": category_id if category_id else None,
#             "country": int(country) if country and country.strip() and country != '' else None,
#             "city": city if city and city.strip() else "",
#             "contacts": (email or '').strip(),
#         }
#
#         created_bid = await BidServices.create_bid(payload=payload, upload_files=files or [])
#         return JSONResponse({
#                 "success": True,
#                 "bid_id": created_bid.id,
#                 "message": "Заявка створена успішно"
#             })
#
#
#
# @router.post('/{lang}/verify-request-code')
# async def handle_verify_request_code(request: Request, lang: str):
#
#     data = await request.form()
#
#     email = data.get("email", "").lower()
#     submitted_code = str(data.get("code", "")).strip()
#     expected_code = EMAIL_VERIFICATION_CODES.get(email)
#
#     if not expected_code or submitted_code != expected_code:
#         return JSONResponse({'error': 'Невірний код'}, status_code=400)
#
#     if email not in PENDING_REQUESTS:
#         return JSONResponse({'error': 'Заявку не знайдено або вже підтверджено'}, status_code=404)
#
#
#     request_data = PENDING_REQUESTS.pop(str(email))
#     temp_files = request_data['temp_files']
#
#     file_paths = await _move_files_to_final_location(temp_files)
#
#     delete_token = secrets.token_urlsafe(DELETE_TOKEN_LENGTH)
#     print(f"DEBUG: Creating bid with data: {request_data}")
#
#     bid = await Bid.create(
#         title_uk=request_data.get('title_uk'),
#         title_en=request_data.get('title_en'),
#         title_pl=request_data.get('title_pl'),
#         title_fr=request_data.get('title_fr'),
#         title_de=request_data.get('title_de'),
#         category=str(request_data.get('category')),
#         under_category_id=request_data.get('under_category'),
#         description_uk=request_data.get('description_uk'),
#         description_en=request_data.get('description_en'),
#         description_pl=request_data.get('description_pl'),
#         description_fr=request_data.get('description_fr'),
#         description_de=request_data.get('description_de'),
#         city=request_data.get('city'),
#         country=request_data.get('country'),
#         email=request_data.get('email'),
#         files=file_paths,
#         auto_translated_fields=request_data.get('auto_translated_fields', []),
#         delete_token=f"dev{random.randint(0, 10000)}",
#     )
#
#     bid_slugs = await generate_bid_slugs(
#         title_uk=request_data.get('title_uk', ''),
#         title_en=request_data.get('title_en', ''),
#         title_pl=request_data.get('title_pl', ''),
#         title_fr=request_data.get('title_fr', ''),
#         title_de=request_data.get('title_de', ''),
#         bid_id=bid.id
#     )
#
#     # Обновляем заявку с slug'ами
#     for slug_field, slug_value in bid_slugs.items():
#         setattr(bid, slug_field, slug_value)
#     await bid.save()
#
#     print(f"DEBUG: Bid created with ID: {bid.id} and slugs: {bid_slugs}")
#
#     base_url = str(request.base_url).rstrip('/')
#     delete_link = f'{base_url}/delete-request/{delete_token}'
#     await send_bid_confirmation_email(request_data['email'], delete_link)
#
#     EMAIL_VERIFICATION_CODES.pop(str(email), None)
#     return JSONResponse({"detail": "Created"},status_code=200)
#
#
# @router.post('/submit-response')
# async def submit_bid_response(request: Request) -> JSONResponse:
#     form_data = await request.form()
#     job_id = str(form_data.get('job_id', '')).strip()
#     name = str(form_data.get('name', '')).strip()
#     email = str(form_data.get('email', '')).strip()
#     message = str(form_data.get('message', '')).strip()
#
#     print(f"DEBUG: submit_bid_response - job_id: '{job_id}', name: '{name}', email: '{email}', message: '{message}'")
#
#     if not job_id:
#         return JSONResponse({'error': 'ID заявки обов\'язковий'}, status_code=400)
#     if not name:
#         return JSONResponse({'error': 'Ім\'я обов\'язкове'}, status_code=400)
#     if not email:
#         return JSONResponse({'error': 'Email обов\'язковий'}, status_code=400)
#     if not message:
#         return JSONResponse({'error': 'Повідомлення обов\'язкове'}, status_code=400)
#
#     try:
#         bid = await Bid.get(id=job_id)
#         await send_bid_response_email(bid.email, str(name), str(email), str(message), bid.title_uk)
#         return JSONResponse({'success': True})
#     except DoesNotExist:
#         return JSONResponse({'error': 'Заявку не знайдено'}, status_code=404)
#
#
# @router.delete('/bid/{bid_id}')
# async def delete_bid_admin(request: Request, bid_id: int) -> JSONResponse:
#     user_role = getattr(request.state, 'user_role', None)
#
#     if user_role != 1:
#         return JSONResponse({'error': 'Недостатньо прав'}, status_code=403)
#
#     try:
#         bid = await Bid.get(id=bid_id)
#         # Удаляем файлы заявки
#         if bid.files:
#             for file_path in bid.files:
#                 try:
#                     full_path = os.path.join(os.getcwd(), file_path.lstrip('/'))
#                     if os.path.exists(full_path):
#                         os.remove(full_path)
#                 except Exception as e:
#                     print(f"DEBUG: Error deleting file {file_path}: {e}")
#
#         await bid.delete()
#         return JSONResponse({'success': True})
#     except DoesNotExist:
#         return JSONResponse({'error': 'Заявку не знайдено'}, status_code=404)
#     except Exception as e:
#         print(f"DEBUG: Error deleting bid {bid_id}: {e}")
#         return JSONResponse({'error': 'Помилка видалення заявки'}, status_code=500)
#
#
# @router.post('/{lang}/bid/{bid_id}/edit')
# async def edit_bid(
#     request: Request,
#     lang: str,
#     bid_id: int,
#     title: Optional[str] = Form(None),
#     category: Optional[str] = Form(None),
#     description: Optional[str] = Form(None),
#     city: Optional[str] = Form(None),
#     files: Optional[List[UploadFile]] = File(None)
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
# async def _validate_uploaded_files(
#     request: Request,
#     files: Optional[List[UploadFile]],
#     user_role: Optional[str],
#     user_email: Optional[str],
#     lang: str,
#     form: dict
# ):
#     ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.pdf', '.bmp', '.gif'}
#
#     def is_file_allowed(file: UploadFile) -> bool:
#         if file.content_type in ALLOWED_FILE_TYPES:
#             return True
#         ext = os.path.splitext(file.filename or '')[1].lower()
#         if ext in ALLOWED_EXTENSIONS:
#             return True
#         return False
#
#     if not files:
#         return []  # нет файлов — всё ок
#
#     if len(files) > MAX_FILES_COUNT:
#         categories = await Category.all()
#         return templates.TemplateResponse('create_request.html', {
#             'request': request,
#             'error': f'Максимальна кількість файлів: {MAX_FILES_COUNT}',
#             'user_role': user_role,
#             'user_email': user_email,
#             'categories': categories,
#             'form': form,
#             'lang': lang
#         })
#
#     temp_file_paths = []
#     for file in files:
#         if not is_file_allowed(file):
#             categories = await Category.all()
#             return templates.TemplateResponse('create_request.html', {
#                 'request': request,
#                 'error': f'Непідтримуваний тип файлу: {file.content_type}',
#                 'user_role': user_role,
#                 'user_email': user_email,
#                 'categories': categories,
#                 'form': form,
#                 'lang': lang
#             })
#
#         if file.size and file.size > 10 * 1024 * 1024:
#             categories = await Category.all()
#             return templates.TemplateResponse('create_request.html', {
#                 'request': request,
#                 'error': 'Розмір файлу не може перевищувати 10MB',
#                 'user_role': user_role,
#                 'user_email': user_email,
#                 'categories': categories,
#                 'form': form,
#                 'lang': lang
#             })
#
#         file_extension = os.path.splitext(file.filename)[1] if file.filename else ''
#         temp_filename = secrets.token_urlsafe(16).replace('-', '_').replace('=', '_') + file_extension
#         temp_file_path = os.path.join(TEMP_FILES_DIR, temp_filename)
#
#         os.makedirs(TEMP_FILES_DIR, exist_ok=True)
#
#         content = await file.read()
#         with open(temp_file_path, 'wb') as f:
#             f.write(content)
#
#         temp_file_paths.append(temp_file_path)
#
#     return temp_file_paths
#
#
#
#
#
#
#
#
# async def _move_files_to_final_location(temp_file_paths: List[str]) -> List[str]:
#     final_file_paths = []
#
#     for temp_path in temp_file_paths:
#         if os.path.exists(temp_path):
#             # Очищаем имя файла от некорректных символов
#             filename = os.path.basename(temp_path)
#             # Заменяем все неалфавитные и нецифровые символы на '_', кроме точки
#             safe_filename = ''.join(c if c.isalnum() or c == '.' else '_' for c in filename)
#             final_path = os.path.join(BID_FILES_DIR, safe_filename)
#
#             # Если файл с таким именем уже существует, добавляем число к имени
#             counter = 1
#             base, ext = os.path.splitext(safe_filename)
#             while os.path.exists(final_path):
#                 safe_filename = f"{base}_{counter}{ext}"
#                 final_path = os.path.join(BID_FILES_DIR, safe_filename)
#                 counter += 1
#
#             os.makedirs(BID_FILES_DIR, exist_ok=True)
#             os.rename(temp_path, final_path)
#
#             final_file_paths.append(final_path)
#
#     return final_file_paths
#
#
# @router.post('/resend-request-code')
# async def resend_request_verification_code(request: Request) -> JSONResponse:
#     form_data = await request.form()
#     email = form_data.get('email')
#
#     if not email:
#         return JSONResponse({
#             'success': False,
#             'error': 'Email не вказано'
#         }, status_code=400)
#
#     # Проверяем можно ли отправить код
#     can_send, wait_time = can_send_code(email)
#     if not can_send:
#         return JSONResponse({
#             'success': False,
#             'error': f'Спробуйте ще раз через {wait_time} секунд'
#         }, status_code=429)
#
#     # Проверяем есть ли pending request для этого email
#     if email not in PENDING_REQUESTS:
#         return JSONResponse({
#             'success': False,
#             'error': 'Заявку для цього email не знайдено'
#         }, status_code=404)
#
#     # Генерируем новый код
#     code = generate_code()
#     EMAIL_VERIFICATION_CODES[email] = code
#
#     # Отправляем код
#     subject = 'Код підтвердження заявки'
#     message = f'Ваш код підтвердження: {code}'
#
#     if send_email(subject, message, email):
#         return JSONResponse({
#             'success': True,
#             'message': 'Код підтвердження надіслано'
#         })
#     else:
#         return JSONResponse({
#             'success': False,
#             'error': 'Помилка при відправці email'
#         }, status_code=500)
#
#
# async def _process_category_id(category):
#     """Получить ID категории или None если некорректная"""
#     try:
#         if not category or category == 'None' or category.strip() == '':
#             return None
#         category_id = int(category)
#         category_obj = await Category.get(id=category_id)
#         return category_obj.id
#     except (ValueError, DoesNotExist):
#         print(f"DEBUG: Invalid category: {category}")
#         return None
#
#
# async def _process_under_category_id(under_category):
#     """Получить ID подкategории или None если некорректная"""
#     try:
#         if not under_category or under_category == 'None' or under_category.strip() == '':
#             return None
#         under_category_id = int(under_category)
#         under_category_obj = await UnderCategory.get(id=under_category_id)
#         return under_category_obj.id
#     except (ValueError, DoesNotExist):
#         print(f"DEBUG: Invalid under_category: {under_category}")
#         return None
