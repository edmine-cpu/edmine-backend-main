from typing import Optional, List
from pydantic import BaseModel, field_validator


class BidCreateRequest(BaseModel):
    title_uk: Optional[str] = ""
    title_en: Optional[str] = ""
    title_pl: Optional[str] = ""
    title_fr: Optional[str] = ""
    title_de: Optional[str] = ""
    description_uk: Optional[str] = ""
    description_en: Optional[str] = ""
    description_pl: Optional[str] = ""
    description_fr: Optional[str] = ""
    description_de: Optional[str] = ""

    
    country: Optional[int] = None
    city: Optional[int] = None

    budget: Optional[int] = None
    budget_type: Optional[str] = None

    auto_translated_fields: Optional[List[str]] = []
    temp_files: Optional[List[str]] = []

    category: Optional[List[int]] = None
    under_category: Optional[List[int]] = None

    @field_validator("category", "under_category", mode="before")
    def convert_to_int_list(cls, v):
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            return [int(x) for x in v.split(",") if x.strip().isdigit()]
        return v

    @field_validator("country", "city", mode="before")
    def convert_to_int(cls, v):
        if v == "" or v is None:
            return None
        return int(v)

    @field_validator("budget", mode="before")
    def convert_budget(cls, v):
        if v == "" or v is None:
            return None
        return int(v)


class BidResponse(BaseModel):
    id: int
    title_uk: str
    description_uk: str
    email: str

    class Config:
        from_atributes = True


class BidVerifyRequest(BaseModel):
    email: str
    code: str