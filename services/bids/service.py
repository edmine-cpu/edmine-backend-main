from typing import Optional
import secrets
import os
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request
from tortoise.expressions import Q

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
        qs = Bid.all().prefetch_related('country')

        # ИСПРАВЛЕНО: Поиск в JSON массиве categories
        if category:
            try:
                category_id = int(category)
                # Для PostgreSQL используется оператор @>
                qs = qs.filter(categories__contains=[category_id])
            except ValueError:
                # Если category не число, игнорируем фильтр
                pass

        # ИСПРАВЛЕНО: Поиск в JSON массиве under_categories
        if subcategory is not None:
            qs = qs.filter(under_categories__contains=[subcategory])

        if country is not None:
            qs = qs.filter(country_id=country)

        if city:
            try:
                city_id = int(city)
                qs = qs.filter(city=city_id)
            except ValueError:
                # Если city не число, игнорируем фильтр
                pass

        # Поиск по заголовкам и описаниям
        if search:
            search_lower = search.lower()
            qs = qs.filter(
                Q(title_uk__icontains=search_lower) |
                Q(title_en__icontains=search_lower) |
                Q(title_pl__icontains=search_lower) |
                Q(title_fr__icontains=search_lower) |
                Q(title_de__icontains=search_lower) |
                Q(description_uk__icontains=search_lower) |
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

        if limit:
            qs = qs.limit(limit)

        return await qs
