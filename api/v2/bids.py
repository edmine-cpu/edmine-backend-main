from fastapi import APIRouter, HTTPException, Query
from typing import Annotated, Optional
from schemas.v2.bids import BidsListResponse, BidSearchParams
from services.v2.bids import get_bids_filtered

SUPPORTED_LANGUAGES = ["en", "uk", "pl", "de", "fr"]
router = APIRouter()


@router.get(
    "/",
    response_model=BidsListResponse,
    summary="Получить список бидов по фильтрам"
)
async def get_bids_filtered_list(
    language: Annotated[Optional[str], Query(description="Язык (uk, en, pl, de, fr)")] = None,
    country: Annotated[Optional[str], Query(description="Slug страны")] = None,
    city: Annotated[Optional[str], Query(description="Slug города")] = None,
    category: Annotated[Optional[str], Query(description="Slug категории")] = None,
    subcategory: Annotated[Optional[str], Query(description="Slug подкатегории")] = None,
    search: Annotated[Optional[str], Query(description="Поисковый запрос")] = None,
    min_cost: Annotated[Optional[int], Query(ge=0, description="Минимальная цена")] = None,
    max_cost: Annotated[Optional[int], Query(ge=0, description="Максимальная цена")] = None,
):
    """
    Получение списка бидов (заказов) с опциональными фильтрами

    - **language**: Язык (uk, en, pl, de, fr) - дефолт: en
    - **country**: Slug страны (опционально)
    - **city**: Slug города (опционально)
    - **category**: Slug категории (опционально)
    - **subcategory**: Slug подкатегории (опционально)
    - **search**: Текстовый поиск по названию и описанию
    - **min_cost**: Минимальная стоимость бюджета
    - **max_cost**: Максимальная стоимость бюджета
    """
    # Дефолтный язык - английский
    if not language:
        language = 'en'

    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый язык. Доступны: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    # Валидация диапазона цен
    if min_cost is not None and max_cost is not None and max_cost < min_cost:
        raise HTTPException(
            status_code=400,
            detail="max_cost должен быть больше или равен min_cost"
        )

    result = await get_bids_filtered(
        language=language,
        country_slug=country,
        city_slug=city,
        category_slug=category,
        subcategory_slug=subcategory,
        search=search,
        min_cost=min_cost,
        max_cost=max_cost
    )

    return result


