from typing import Optional
from tortoise.expressions import Q
from models.actions import Bid
from models.places import Country, City
from models.categories import Category, UnderCategory


async def get_bids_filtered(
    language: str,
    country_slug: Optional[str] = None,
    city_slug: Optional[str] = None,
    category_slug: Optional[str] = None,
    subcategory_slug: Optional[str] = None,
    search: Optional[str] = None,
    min_cost: Optional[int] = None,
    max_cost: Optional[int] = None,
):
    """
    Получение отфильтрованных бидов по slug'ам и параметрам поиска

    Args:
        language: Язык (uk, en, pl, de, fr) - дефолт: en
        country_slug: Slug страны (опционально)
        city_slug: Slug города (опционально)
        category_slug: Slug категории (опционально)
        subcategory_slug: Slug подкатегории (опционально)
        search: Поисковый запрос
        min_cost: Минимальная цена
        max_cost: Максимальная цена

    Returns:
        dict с результатами и метаданными
    """

    # Получаем объекты по slug'ам (если указаны)
    country_obj = None
    city_obj = None
    category_obj = None
    subcategory_obj = None

    if country_slug:
        country_obj = await Country.filter(**{f"slug_{language}": country_slug}).first()

    if city_slug:
        city_obj = await City.filter(**{f"slug_{language}": city_slug}).first()

    if category_slug:
        category_obj = await Category.filter(**{f"slug_{language}": category_slug}).first()

    if subcategory_slug:
        subcategory_obj = await UnderCategory.filter(**{f"slug_{language}": subcategory_slug}).first()

    # Формируем базовый запрос
    query = Bid.all().prefetch_related('country', 'city', 'author')

    # Применяем фильтры только если объекты найдены
    if country_obj:
        query = query.filter(country_id=country_obj.id)

    if city_obj:
        query = query.filter(city_id=city_obj.id)

    # Фильтр по категориям (JSONField содержит список ID)
    if category_obj:
        query = query.filter(categories__contains=category_obj.id)

    if subcategory_obj:
        query = query.filter(under_categories__contains=subcategory_obj.id)

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
        "country": getattr(country_obj, f"name_{language}", country_slug) if country_obj else None,
        "city": getattr(city_obj, f"name_{language}", city_slug) if city_obj else None,
        "category": getattr(category_obj, f"name_{language}", category_slug) if category_obj else None,
        "subcategory": getattr(subcategory_obj, f"name_{language}", subcategory_slug) if subcategory_obj else None,
        "lang_search": language,
        "min_cost": min_cost,
        "max_cost": max_cost,
        "results": results,
        "total": total
    }
