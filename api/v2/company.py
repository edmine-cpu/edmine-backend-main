from fastapi import APIRouter, HTTPException, Query
from typing import Annotated, Optional
from schemas.v2.company import CompaniesListResponse
from services.v2.company import get_companies_filtered

SUPPORTED_LANGUAGES = ["en", "uk", "pl", "de", "fr"]
router = APIRouter()


@router.get(
    "/",
    response_model=CompaniesListResponse,
    summary="Получить список компаний по фильтрам"
)
async def get_companies_filtered_list(
    language: Annotated[Optional[str], Query(description="Язык (uk, en, pl, de, fr)")] = None,
    country_id: Annotated[Optional[int], Query(ge=1, description="ID страны")] = None,
    city_id: Annotated[Optional[int], Query(ge=1, description="ID города")] = None,
    category_id: Annotated[Optional[int], Query(ge=1, description="ID категории")] = None,
    subcategory_id: Annotated[Optional[int], Query(ge=1, description="ID подкатегории")] = None,
    search: Annotated[Optional[str], Query(description="Поисковый запрос")] = None,
):
    """
    Получение списка компаний с опциональными фильтрами

    - **language**: Язык (uk, en, pl, de, fr) - дефолт: en
    - **country_id**: ID страны (опционально)
    - **city_id**: ID города (опционально)
    - **category_id**: ID категории (опционально)
    - **subcategory_id**: ID подкатегории (опционально)
    - **search**: Текстовый поиск по названию и описанию
    """
    # Дефолтный язык - английский
    if not language:
        language = 'en'

    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый язык. Доступны: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    result = await get_companies_filtered(
        language=language,
        country_id=country_id,
        city_id=city_id,
        category_id=category_id,
        subcategory_id=subcategory_id,
        search=search
    )

    return result
