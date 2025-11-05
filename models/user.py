from tortoise import fields, models
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64)
    email = fields.CharField(max_length=64, unique=True)
    password = fields.CharField(max_length=128)
    categories = fields.ManyToManyField('models.Category', related_name='users')
    subcategories = fields.ManyToManyField('models.UnderCategory', related_name='users', null=True)
    role = fields.IntField(default=0)  # 0 - обычный пользователь, 1 - админ
    language = fields.CharField(max_length=2, default='en')
    
    # Profile fields
    nickname = fields.CharField(max_length=64, null=True)
    avatar = fields.CharField(max_length=500, null=True)
    user_role = fields.CharField(max_length=20, default='customer')
    profile_description = fields.TextField(null=True)
    
    slug_uk = fields.CharField(max_length=128, null=True)
    slug_en = fields.CharField(max_length=128, null=True)
    slug_pl = fields.CharField(max_length=128, null=True)
    slug_fr = fields.CharField(max_length=128, null=True)
    slug_de = fields.CharField(max_length=128, null=True)
    
    company_name_uk = fields.CharField(max_length=128, null=True)
    company_name_en = fields.CharField(max_length=128, null=True)
    company_name_pl = fields.CharField(max_length=128, null=True)
    company_name_fr = fields.CharField(max_length=128, null=True)
    company_name_de = fields.CharField(max_length=128, null=True)
    company_description_uk = fields.TextField(null=True)
    company_description_en = fields.TextField(null=True)
    company_description_pl = fields.TextField(null=True)
    company_description_fr = fields.TextField(null=True)
    company_description_de = fields.TextField(null=True)
    auto_translated_fields = fields.JSONField(null=True) 
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"


class Company(models.Model):
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=64)  # Основное название
    name_uk = fields.CharField(max_length=64, null=True)
    name_en = fields.CharField(max_length=64, null=True)
    name_pl = fields.CharField(max_length=64, null=True)
    name_fr = fields.CharField(max_length=64, null=True)
    name_de = fields.CharField(max_length=64, null=True)
    
    description_uk = fields.TextField(null=True)
    description_en = fields.TextField(null=True)
    description_pl = fields.TextField(null=True)
    description_fr = fields.TextField(null=True)
    description_de = fields.TextField(null=True)

    slug_name = fields.CharField(max_length=64, null=True)
    slug_uk = fields.CharField(max_length=128, null=True)
    slug_en = fields.CharField(max_length=128, null=True)
    slug_pl = fields.CharField(max_length=128, null=True)
    slug_fr = fields.CharField(max_length=128, null=True)
    slug_de = fields.CharField(max_length=128, null=True)

    city = fields.TextField(null=True)
    country = fields.TextField(null=True)

    categories = fields.ManyToManyField('models.Category', related_name='company', null=True)
    subcategories = fields.ManyToManyField('models.UnderCategory', related_name='company', null=True)

    owner = fields.ForeignKeyField('models.User', related_name='companies', null=True)
    
    auto_translated_fields = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    #completed_bids = ...


