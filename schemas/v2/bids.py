from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class PaginationParams(BaseModel):
    limit: int = Field(20, ge=0, le=100)
    offset: int = Field(0, ge=0)


class Bid(BaseModel):
	language: str

	counrty: Optional[int] = None
	city: Optional[int] = None

    category: Optional[List[int]] = None
    under_category: Optional[List[int]] = None

    @field_validator("category", "under_category", mode="before")
    def convert_to_int_list(cls, v):
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            return [int(x) for x in v.split(",") if x.strip().isdigit()]
        return v


