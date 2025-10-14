from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class PaginationParams(BaseModel):
    limit: int = Field(20, ge=0, le=100)
    offset: int = Field(0, ge=0)


class BidSearchParams(BaseModel):
    """Параметры поиска бидов"""
    search: Optional[str] = None
    min_cost: Optional[int] = Field(None, ge=0)
    max_cost: Optional[int] = Field(None, ge=0)

    @field_validator("max_cost")
    @classmethod
    def validate_cost_range(cls, v, info):
        if v is not None and info.data.get("min_cost") is not None:
            if v < info.data["min_cost"]:
                raise ValueError("max_cost должен быть >= min_cost")
        return v


class BidItemResponse(BaseModel):
    """Один бид в списке"""
    title: str
    subcprice: Optional[str] = None
    cost: Optional[int] = None  # Стоимость (budget как число)
    category: Optional[List[int]] = None  # ID категорий
    undercategory: Optional[List[int]] = None  # ID подкатегорий
    country: Optional[str] = None
    city: Optional[str] = None
    slug: str
    owner_id: int


class BidsListResponse(BaseModel):
    """Ответ со списком бидов"""
    country: Optional[str] = None
    city: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    lang_search: str
    min_cost: Optional[int] = None
    max_cost: Optional[int] = None
    results: List[BidItemResponse] = []
    total: int = 0


