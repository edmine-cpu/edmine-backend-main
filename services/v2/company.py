from typing import Optional
from tortoise.expressions import Q
from models.user import Company
from models.places import Country, City
from models.categories import Category, UnderCategory


async def get_companies_filtered(
    language: str,
    country_id: Optional[int] = None,
    city_id: Optional[int] = None,
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    search: Optional[str] = None,
):
    """
    Получение отфильтрованных компаний по ID и параметрам поиска

    Args:
        language: Язык (uk, en, pl, de, fr) - дефолт: en
        country_id: ID страны (опционально)
        city_id: ID города (опционально)
        category_id: ID категории (опционально)
        subcategory_id: ID подкатегории (опционально)
        search: Поисковый запрос

    Returns:
        dict с результатами и метаданными
    """

    ация языка для защиты от инъекций (defense-in-depth)
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
    query = Company.all().prefetch_related('categories', 'subcategories', 'owner')

    # Применяем фильтры - для Company country и city это текстовые поля
    if country_id is not None and country_obj:
        # Фильтруем по текстовому названию страны
        country_name = getattr(country_obj, f"name_{language}", None)
        if country_name:
            query = query.filter(country__icontains=country_name)

    if city_id is not None and city_obj:
        # Фильтруем по текстовому названию города
        city_name = getattr(city_obj, f"name_{language}", None)
        if city_name:
            query = query.filter(city__icontains=city_name)

    # Фильтр по категориям (ManyToMany связь)
    if category_id is not None:
        query = query.filter(categories__id=category_id)

    if subcategory_id is not None:
        query = query.filter(subcategories__id=subcategory_id)

    # Текстовый поиск по name и description
    if search:
        search_filters = Q()
        name_field = f"name_{language}"
        desc_field = f"description_{language}"
        search_filters |= Q(**{f"{name_field}__icontains": search})
        search_filters |= Q(**{f"{desc_field}__icontains": search})
        query = query.filter(search_filters)

    # Получаем общее количество и результаты
    total = await query.count()
    companies = await query.all()

    # Формируем результаты
    results = []
    for company in companies:
        # Используем запрошенный язык напрямую
        slug_field = f"slug_{language}"
        name_field = f"name_{language}"
        desc_field = f"description_{language}"

        # Fallback на английский если нет в запрошенном языке
        name = getattr(company, name_field, None) or getattr(company, "name_en", None) or getattr(company, "name", "") or ""
        slug = getattr(company, slug_field, None) or getattr(company, "slug_en", None) or getattr(company, "slug_name", "") or ""
        description = getattr(company, desc_field, None) or getattr(company, "description_en", None)

        # Получаем ID категорий и подкатегорий
        category_ids = []
        subcategory_ids = []

        if hasattr(company, 'categories'):
            categories_list = await company.categories.all()
            category_ids = [cat.id for cat in categories_list]

        if hasattr(company, 'subcategories'):
            subcategories_list = await company.subcategories.all()
            subcategory_ids = [subcat.id for subcat in subcategories_list]

        results.append({
            "name": name,
            "description": description,
            "category_ids": category_ids,
            "subcategory_ids": subcategory_ids,
            "country": company.country,
            "city": company.city,
            "slug": slug,
            "owner_id": company.owner_id if company.owner_id else 0
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
        "results": results,
        "total": total
    }
