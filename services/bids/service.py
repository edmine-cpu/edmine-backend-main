from typing import Optional
import secrets
import os
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request
from tortoise.expressions import Q
import asyncio

from api.bids_config import DELETE_TOKEN_LENGTH
from api_old.email_utils import (
    send_bid_confirmation_email,
    send_bid_response_email
)
from api_old.slug_utils import generate_bid_slugs
from crud.bid import BidCRUD
from models import Bid
from routers.secur import get_current_user
from schemas.bid import BidCreateRequest, BidVerifyRequest
from services.translation.utils import auto_translate_bid_fields
from utils.bid import _validate_uploaded_files, _move_files_to_final_location


class BidService:

    @staticmethod
    async def create_request(data: BidCreateRequest, files, lang: str, user_role: int, user_email: str,
                             request: Request):

        current_user = await get_current_user(request)

        # Валидация файлов
        temp_files = await _validate_uploaded_files(
            files=files,
            user_role=user_role,
            user_email=user_email,
            lang=lang,
            form=data.dict()  # словарь с полями формы
        )

        file_paths = await _move_files_to_final_location(temp_files)
        # Создаем данные для заявки, используя current_user как автора
        request_data = data.dict()
        request_data["author"] = current_user
        request_data["files"] = file_paths
        request_data["delete_token"] = secrets.token_urlsafe(DELETE_TOKEN_LENGTH)

        # Определяем основной язык бида
        from services.translation.utils import detect_primary_language
        main_language = detect_primary_language(
            title_uk=request_data.get('title_uk'),
            title_en=request_data.get('title_en'),
            title_pl=request_data.get('title_pl'),
            title_fr=request_data.get('title_fr'),
            title_de=request_data.get('title_de'),
            description_uk=request_data.get('description_uk'),
            description_en=request_data.get('description_en'),
            description_pl=request_data.get('description_pl'),
            description_fr=request_data.get('description_fr'),
            description_de=request_data.get('description_de')
        )
        request_data['main_language'] = main_language

        # ДОБАВЛЯЕМ АВТОПЕРЕВОД
        translation_result = await auto_translate_bid_fields(
            title_uk=request_data.get('title_uk'),
            title_en=request_data.get('title_en'),
            title_pl=request_data.get('title_pl'),
            title_fr=request_data.get('title_fr'),
            title_de=request_data.get('title_de'),
            description_uk=request_data.get('description_uk'),
            description_en=request_data.get('description_en'),
            description_pl=request_data.get('description_pl'),
            description_fr=request_data.get('description_fr'),
            description_de=request_data.get('description_de')
        )

        # Обновляем данные переведенными значениями
        request_data.update({
            'title_uk': translation_result['title_uk'],
            'title_en': translation_result['title_en'],
            'title_pl': translation_result['title_pl'],
            'title_fr': translation_result['title_fr'],
            'title_de': translation_result['title_de'],
            'description_uk': translation_result['description_uk'],
            'description_en': translation_result['description_en'],
            'description_pl': translation_result['description_pl'],
            'description_fr': translation_result['description_fr'],
            'description_de': translation_result['description_de'],
            'auto_translated_fields': translation_result['auto_translated_fields']
        })

        print(f"DEBUG DATA (AUTHENTICATED), \n {request_data}")

        # Создаем заявку
        bid = await BidCRUD.create_bid(request_data)

        # Генерируем слаги
        slugs = await generate_bid_slugs(
            title_uk=bid.title_uk,
            title_en=bid.title_en,
            title_pl=bid.title_pl,
            title_fr=bid.title_fr,
            title_de=bid.title_de,
            bid_id=bid.id
        )
        await BidCRUD.update_bid(bid, slugs)

        # Отправляем email с подтверждением
        delete_link = f'{request.base_url}/delete-request/{bid.delete_token}'
        await send_bid_confirmation_email(current_user.email, delete_link)

        return JSONResponse({
            "success": True,
            "message": "Заявка успешно создана",
            "requires_verification": False
        })

    @staticmethod
    async def create_request_fast(data: BidCreateRequest, files, lang: str, user_role: int, user_email: str,
                                 request: Request):
        """
        Сверхбыстрое создание заявки с ленивым переводом
        """
        # Запускаем все операции параллельно
        current_user_task = asyncio.create_task(get_current_user(request))
        files_task = asyncio.create_task(_validate_uploaded_files(
            files=files, user_role=user_role, user_email=user_email, lang=lang, form=data.dict()
        ))
        
        # Ждем завершения критических операций
        current_user, temp_files = await asyncio.gather(current_user_task, files_task)
        
        # Параллельно обрабатываем файлы и готовим данные
        file_paths_task = asyncio.create_task(_move_files_to_final_location(temp_files))
        
        # Подготавливаем данные для заявки
        request_data = data.dict()
        request_data["author"] = current_user
        request_data["delete_token"] = secrets.token_urlsafe(DELETE_TOKEN_LENGTH)

        # Определяем основной язык бида
        from services.translation.utils import detect_primary_language
        main_language = detect_primary_language(
            title_uk=request_data.get('title_uk'),
            title_en=request_data.get('title_en'),
            title_pl=request_data.get('title_pl'),
            title_fr=request_data.get('title_fr'),
            title_de=request_data.get('title_de'),
            description_uk=request_data.get('description_uk'),
            description_en=request_data.get('description_en'),
            description_pl=request_data.get('description_pl'),
            description_fr=request_data.get('description_fr'),
            description_de=request_data.get('description_de')
        )
        request_data['main_language'] = main_language

        # Ждем завершения обработки файлов
        file_paths = await file_paths_task
        request_data["files"] = file_paths

        # Создаем заявку сразу (без переводов)
        bid = await BidCRUD.create_bid(request_data)

        # Генерируем слаги для основного языка
        primary_lang = main_language
        primary_title = request_data.get(f'title_{primary_lang}', '')
        if primary_title:
            from api_old.slug_utils import generate_slug
            slug = generate_slug(primary_title, primary_lang)
            if bid.id:
                slug = f"{slug}-{bid.id}"
            
            # Обновляем только основной slug
            await BidCRUD.update_bid(bid, {f'slug_{primary_lang}': slug})
        
        # Запускаем перевод в фоне (не ждем)
        translation_task = asyncio.create_task(auto_translate_bid_fields(
            title_uk=request_data.get('title_uk'),
            title_en=request_data.get('title_en'),
            title_pl=request_data.get('title_pl'),
            title_fr=request_data.get('title_fr'),
            title_de=request_data.get('title_de'),
            description_uk=request_data.get('description_uk'),
            description_en=request_data.get('description_en'),
            description_pl=request_data.get('description_pl'),
            description_fr=request_data.get('description_fr'),
            description_de=request_data.get('description_de')
        ))
        
        # Запускаем обновление переводов в фоне
        async def update_translations():
            try:
                translation_result = await translation_task
                # Обновляем данные переведенными значениями
                update_data = {
                    'title_uk': translation_result['title_uk'],
                    'title_en': translation_result['title_en'],
                    'title_pl': translation_result['title_pl'],
                    'title_fr': translation_result['title_fr'],
                    'title_de': translation_result['title_de'],
                    'description_uk': translation_result['description_uk'],
                    'description_en': translation_result['description_en'],
                    'description_pl': translation_result['description_pl'],
                    'description_fr': translation_result['description_fr'],
                    'description_de': translation_result['description_de'],
                    'auto_translated_fields': translation_result['auto_translated_fields']
                }
                
                # Генерируем все слаги
                slugs = await generate_bid_slugs(
                    title_uk=update_data['title_uk'],
                    title_en=update_data['title_en'],
                    title_pl=update_data['title_pl'],
                    title_fr=update_data['title_fr'],
                    title_de=update_data['title_de'],
                    bid_id=bid.id
                )
                
                # Обновляем заявку с переводами и слагами
                update_data.update(slugs)
                await BidCRUD.update_bid(bid, update_data)
                
            except Exception as e:
                print(f"Background translation update failed: {e}")
        
        # Запускаем обновление в фоне
        asyncio.create_task(update_translations())
        
        # Отправляем email в фоне (не ждем)
        delete_link = f'{request.base_url}/delete-request/{bid.delete_token}'
        asyncio.create_task(send_bid_confirmation_email(current_user.email, delete_link))

        return JSONResponse({
            "success": True,
            "message": "Заявка успешно создана (переводы обновляются в фоне)",
            "bid_id": bid.id,
            "requires_verification": False
        })

    @staticmethod
    async def submit_response(job_id: int, name: str, email: str, message: str):
        bid = await BidCRUD.get_bid_by_id(job_id)
        if not bid:
            return JSONResponse({'error': 'Заявку не знайдено'}, status_code=404)

        await send_bid_response_email(bid.email, name, email, message, bid.title_uk)
        return JSONResponse({'success': True})

    @staticmethod
    async def delete_bid(bid_id: int, user_role: int):
        if user_role != 1:
            return JSONResponse({'error': 'Недостатньо прав'}, status_code=403)

        bid = await BidCRUD.get_bid_by_id(bid_id)
        if not bid:
            return JSONResponse({'error': 'Заявку не знайдено'}, status_code=404)

        if bid.files:
            for file_path in bid.files:
                try:
                    full_path = os.path.join(os.getcwd(), file_path.lstrip('/'))
                    if os.path.exists(full_path):
                        os.remove(full_path)
                except Exception as e:
                    print(f"DEBUG: Error deleting file {file_path}: {e}")

        await BidCRUD.delete_bid(bid)
        return JSONResponse({'success': True})

    @staticmethod
    async def list_bids(
            category: Optional[str] = None,
            subcategory: Optional[int] = None,
            country: Optional[int] = None,
            city: Optional[str] = None,
            search: Optional[str] = None,
            limit: Optional[int] = None,
            sort: Optional[str] = "date_desc",
    ):
        # Оптимизированный запрос с select_related для уменьшения количества запросов
        qs = Bid.all().select_related('country', 'author')

        # Применяем фильтры в порядке селективности (наиболее ограничивающие первыми)
        
        # Страна (обычно наиболее селективный фильтр)
        if country is not None:
            qs = qs.filter(country_id=country)

        # Город
        if city:
            try:
                city_id = int(city)
                qs = qs.filter(city=city_id)
            except ValueError:
                # Если city не число, игнорируем фильтр
                pass

        # Категории - ИСПРАВЛЕНО: Поиск в JSON массиве categories
        if category:
            try:
                category_id = int(category)
                # Для PostgreSQL используется оператор @>
                qs = qs.filter(categories__contains=[category_id])
            except ValueError:
                # Если category не число, игнорируем фильтр
                pass

        # Подкатегории - ИСПРАВЛЕНО: Поиск в JSON массиве under_categories
        if subcategory is not None:
            qs = qs.filter(under_categories__contains=[subcategory])

        # Поиск по тексту (наиболее затратный - применяем последним)
        if search:
            search_lower = search.lower()
            # Оптимизируем поиск - сначала проверяем украинский, потом остальные
            qs = qs.filter(
                Q(title_uk__icontains=search_lower) |
                Q(description_uk__icontains=search_lower) |
                Q(title_en__icontains=search_lower) |
                Q(title_pl__icontains=search_lower) |
                Q(title_fr__icontains=search_lower) |
                Q(title_de__icontains=search_lower) |
                Q(description_en__icontains=search_lower) |
                Q(description_pl__icontains=search_lower) |
                Q(description_fr__icontains=search_lower) |
                Q(description_de__icontains=search_lower)
            )

        # Сортировка
        if sort == "date_asc":
            qs = qs.order_by("created_at")
        elif sort == "title_asc":
            qs = qs.order_by("title_uk")
        elif sort == "title_desc":
            qs = qs.order_by("-title_uk")
        else:  # date_desc, relevance, popular - все по умолчанию по дате
            qs = qs.order_by("-created_at")

        # Ограничиваем результат для защиты от больших выборок
        if limit:
            qs = qs.limit(min(limit, 100))  # Максимум 100 записей
        else:
            qs = qs.limit(20)  # По умолчанию 20 записей

        return await qs

    @staticmethod
    async def get_bid_by_id(bid_id: int):
        """
        Получить заявку по ID с данными автора
        """
        return await Bid.get_or_none(id=bid_id).select_related('author')

