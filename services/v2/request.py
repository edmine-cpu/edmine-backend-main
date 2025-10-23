from typing import Optional
from tortoise.expressions import Q
from models.actions import Bid
from models.places import Country, City
from models.categories import Category, UnderCategory


async def get_bids_filtered(
    language: str,
    country_id: Optional[int] = None,
    city_id: Optional[int] = None,
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    search: Optional[str] = None,
    min_cost: Optional[int] = None,
    max_cost: Optional[int] = None,
):
    """
    Получение отфильтрованных бидов по ID и параметрам поиска

    Args:
        language: Язык (uk, en, pl, de, fr) - дефолт: en
        country_id: ID страны (опционально)
        city_id: ID города (опционально)
        category_id: ID категории (опционально)
        subcategory_id: ID подкатегории (опционально)
        search: Поисковый запрос
        min_cost: Минимальная цена
        max_cost: Максимальная цена

    Returns:
        dict с результатами и метаданными
    """

    # Валидация языка для защиты от инъекций (defense-in-depth)
    ALLOWED_LANGUAGES = ['uk', 'en', 'pl', 'de', 'fr']
    if language not in ALLOWED_LANGUAGES:
        language = 'en'  # Fallback на безопасное значение

    # Получаем объекты по ID (если указаны) для метаданных в ответе
    country_obj = None
    city_obj = None
    category_obj = None
    subcategory_obj = None

    if country_id is not None:
        country_obj = await Country.filter(id=country_id).first()

    if city_id is not None:
        city_obj = await City.filter(id=city_id).first()

    if category_id is not None:
        category_obj = await Category.filter(id=category_id).first()

    if subcategory_id is not None:
        subcategory_obj = await UnderCategory.filter(id=subcategory_id).first()

    # Формируем базовый запрос
    query = Bid.all().prefetch_related('country', 'city', 'author')

    # Применяем фильтры по ID
    if country_id is not None:
        query = query.filter(country_id=country_id)

    if city_id is not None:
        query = query.filter(city_id=city_id)

    # Фильтр по категориям (JSONField содержит список ID)
    if category_id is not None:
        query = query.filter(categories__contains=category_id)

    if subcategory_id is not None:
        query = query.filter(under_categories__contains=subcategory_id)

    # Фильтр по стоимости (budget хранится как строка, конвертируем)
    if min_cost is not None or max_cost is not None:
        budget_filters = Q()
        # Попытка фильтрации через CAST, зависит от БД
        if min_cost is not None:
            budget_filters &= Q(budget__gte=str(min_cost))
        if max_cost is not None:
            budget_filters &= Q(budget__lte=str(max_cost))
        query = query.filter(budget_filters)

    # Текстовый поиск по title и description
    if search:
        search_filters = Q()
        title_field = f"title_{language}"
        desc_field = f"description_{language}"
        search_filters |= Q(**{f"{title_field}__icontains": search})
        search_filters |= Q(**{f"{desc_field}__icontains": search})
        query = query.filter(search_filters)

    # Получаем общее количество и результаты
    total = await query.count()
    bids = await query.all()

    # Формируем результаты
    results = []
    for bid in bids:
        # Используем запрошенный язык напрямую
        slug_field = f"slug_{language}"
        title_field = f"title_{language}"

        # Fallback на английский если нет в запрошенном языке
        title = getattr(bid, title_field, None) or getattr(bid, "title_en", "") or ""
        slug = getattr(bid, slug_field, None) or getattr(bid, "slug_en", "") or ""

        # ЗАКОММЕНТИРОВАНО: использование main_language (для будущего использования)
        # bid_lang = bid.main_language if bid.main_language else language
        # slug_field = f"slug_{bid_lang}"
        # title_field = f"title_{bid_lang}"

        # Конвертируем budget в число для cost
        cost = None
        if bid.budget:
            try:
                cost = int(bid.budget)
            except (ValueError, TypeError):
                cost = None

        results.append({
            "title": title,
            "subcprice": bid.budget,
            "cost": cost,
            "category": bid.categories if bid.categories else [],
            "undercategory": bid.under_categories if bid.under_categories else [],
            "country": getattr(bid.country, f"name_{language}", "") if bid.country else None,
            "city": getattr(bid.city, f"name_{language}", "") if bid.city else None,
            "slug": slug,
            "owner_id": bid.author_id if bid.author_id else 0
        })

    return {
        "country": getattr(country_obj, f"name_{language}", None) if country_obj else None,
        "city": getattr(city_obj, f"name_{language}", None) if city_obj else None,
        "category": getattr(category_obj, f"name_{language}", None) if category_obj else None,
        "subcategory": getattr(subcategory_obj, f"name_{language}", None) if subcategory_obj else None,
        "country_id": country_id,
        "city_id": city_id,
        "category_id": category_id,
        "subcategory_id": subcategory_id,
        "lang_search": language,
        "min_cost": min_cost,
        "max_cost": max_cost,
        "results": results,
        "total": total
    }
