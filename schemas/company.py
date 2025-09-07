from typing import Optional, List

from pydantic import BaseModel, Field, field_validator


class PaginationParams(BaseModel):
    limit: int = Field(20, ge=0, le=100)
    offset: int = Field(0, ge=0)


class CompanyCreateSchema(BaseModel):
    name: str = Field(..., max_length=64)
    
    # Многоязычные названия (необязательные, будут переведены автоматически)
    name_uk: Optional[str] = Field(None, max_length=64)
    name_en: Optional[str] = Field(None, max_length=64)
    name_pl: Optional[str] = Field(None, max_length=64)
    name_fr: Optional[str] = Field(None, max_length=64)
    name_de: Optional[str] = Field(None, max_length=64)

    description_uk: Optional[str] = Field(None, max_length=1024)
    description_en: Optional[str] = Field(None, max_length=1024)
    description_pl: Optional[str] = Field(None, max_length=1024)
    description_fr: Optional[str] = Field(None, max_length=1024)
    description_de: Optional[str] = Field(None, max_length=1024)

    slug_name: Optional[str] = Field(None, max_length=64)

    country: Optional[int] = None
    city: Optional[int] = None

    category: Optional[List[int]] = None
    under_category: Optional[List[int]] = None

    @field_validator("country", "city", mode="before")
    def convert_to_int(cls, v):
        if v == "" or v is None:
            return None
        return int(v)


class CompanyUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=64)
    
    # Многоязычные названия
    name_uk: Optional[str] = Field(None, max_length=64)
    name_en: Optional[str] = Field(None, max_length=64)
    name_pl: Optional[str] = Field(None, max_length=64)
    name_fr: Optional[str] = Field(None, max_length=64)
    name_de: Optional[str] = Field(None, max_length=64)

    description_uk: Optional[str] = Field(None, max_length=256)
    description_en: Optional[str] = Field(None, max_length=256)
    description_pl: Optional[str] = Field(None, max_length=256)
    description_fr: Optional[str] = Field(None, max_length=256)
    description_de: Optional[str] = Field(None, max_length=256)

    slug_name: Optional[str] = Field(None, max_length=64)

    country: Optional[int] = None
    city: Optional[int] = None

    category: Optional[List[int]] = None
    under_category: Optional[List[int]] = None

    @field_validator("country", "city", mode="before")
    def convert_to_int(cls, v):
        if v == "" or v is None:
            return None
        return int(v)
