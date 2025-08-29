from fastapi import Request
from crud.company import CompanyCRUD
from slugify import slugify
from routers.secur import get_current_user
from schemas.company import CompanyCreateSchema, CompanyUpdateSchema
from services.translation.companys import auto_translate_descriptions


class CompanyService:
    @staticmethod
    async def get_all_companies(limit, offset, category=None, subcategory=None, country=None, city=None, search=None, sort="relevance"):
        companies = await CompanyCRUD.get_all_companies(
            limit=limit, 
            offset=offset,
            category=category,
            subcategory=subcategory,
            country=country,
            city=city,
            search=search,
            sort=sort
        )
        return companies


    @staticmethod
    async def get_company_by_id(company_id: int):
        company = await CompanyCRUD.get_company_by_id(company_id)
        return company


    @staticmethod
    async def get_company_by_slug(company_slug: str, company_id: int):
        company = await CompanyCRUD.get_company_by_slug(company_slug, company_id)
        return company


    @staticmethod
    async def get_company_by_owner(owner_id: int):
        company = await CompanyCRUD.get_company_by_owner(owner_id)
        return company


    @staticmethod
    async def create_company(request:Request, company: CompanyCreateSchema):
        user = await get_current_user(request)

        translations = await auto_translate_descriptions(
            description_uk=company.description_uk,
            description_en=company.description_en,
            description_pl=company.description_pl,
            description_fr=company.description_fr,
            description_de=company.description_de
        )

        company.description_uk = translations['description_uk']
        company.description_en = translations['description_en']
        company.description_pl = translations['description_pl']
        company.description_fr = translations['description_fr']
        company.description_de = translations['description_de']

        if company.slug_name is None:
            company.slug_name = slugify(company.name)

        result = await CompanyCRUD.create_company(user, company)
        return result

    @staticmethod
    async def update_company(company_id: int, company: CompanyUpdateSchema):
        data = company.model_dump(exclude_unset=True)
        result = await CompanyCRUD.update_company(company_id, data)
        return result


    @staticmethod
    async def delete_company(company_id: int):
        result = await CompanyCRUD.delete_company(company_id)
        return result

