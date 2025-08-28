from fastapi import APIRouter
from models import Category, UnderCategory


router = APIRouter()


@router.get("/categories")
async def get_categories():
    return await Category.all()


@router.get("/subcategories")
async def get_subcategories():
    subcategories = await UnderCategory.all().prefetch_related('full_category')
    result = []
    for sub in subcategories:
        result.append({
            'id': sub.id,
            'full_category_id': sub.full_category.id,
            'name_uk': sub.name_uk,
            'name_en': sub.name_en,
            'name_pl': sub.name_pl,
            'name_fr': sub.name_fr,
            'name_de': sub.name_de,
        })
    return result
