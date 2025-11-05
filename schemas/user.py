from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Annotated, Any


class UserBase(BaseModel):
    name: str
    email: EmailStr
    city: str
    password: str


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    company_name: Dict[str, Optional[str]]
    company_description: Dict[str, Optional[str]]
    categories: Optional[List[Dict[str, Any]]] = None
    subcategories: Optional[List[Dict[str, Any]]] = None


class UserRegisterForm(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]
    role: Optional[str] = 'user'
    language: Optional[str] = 'en'



class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    city: Optional[int] = None
    country_id: Optional[int] = None
    language: Optional[str] = None

    company_name_uk: Optional[str] = None
    company_name_en: Optional[str] = None
    company_name_pl: Optional[str] = None
    company_name_fr: Optional[str] = None
    company_name_de: Optional[str] = None

    company_description_uk: Optional[str] = None
    company_description_en: Optional[str] = None
    company_description_pl: Optional[str] = None
    company_description_fr: Optional[str] = None
    company_description_de: Optional[str] = None


class UserLoginForm(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=6)]
