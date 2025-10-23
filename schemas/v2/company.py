from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class CompanyItemResponse(BaseModel):
    """Одна компания в списке"""
    name: str
    description: Optional[str] = None
    category_ids: Optional[List[int]] = None  # ID категорий
    subcategory_ids: Optional[List[int]] = None  # ID подкатегорий
    country: Optional[str] = None
    city: Optional[str] = None
    slug: str
    owner_id: int


class CompaniesListResponse(BaseModel):
    """Ответ со списком компаний"""
    country: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    country_id: Optional[int] = None
    city_id: Optional[int] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    lang_search: str
    results: List[CompanyItemResponse] = []
    total: int = 0
