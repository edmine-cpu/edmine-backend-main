from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    city: str
    password: str
    role: str = 'executor'
    categories: List[str] = []


class BidCreate(BaseModel):
    title: str
    category: str
    description: str
    city: str
    email: str
    files: Optional[List[str]] = None 