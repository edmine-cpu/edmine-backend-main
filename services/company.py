from fastapi import Request
from crud.company import CompanyCRUD
from slugify import slugify
from routers.secur import get_current_user
from schemas.company import CompanyCreateSchema, CompanyUpdateSchema
from services.translation.companys import auto_translate_descriptions, auto_translate_company_fields


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
    async def get_company_by_slug_and_id(slug_part: str, company_id: int):
        """
        Получить компанию по части слага и ID
        """
        company = await CompanyCRUD.get_company_by_slug_and_id(slug_part, company_id)
        return company


    @staticmethod
    async def get_company_by_owner(owner_id: int):
        company = await CompanyCRUD.get_company_by_owner(owner_id)
        return company


    @staticmethod
    async def create_company(request: Request, company: CompanyCreateSchema):
        import asyncio
        
        # Запускаем получение пользователя и перевод параллельно
        user_task = asyncio.create_task(get_current_user(request))
        translation_task = asyncio.create_task(auto_translate_company_fields(
            name=company.name,
            description_uk=company.description_uk,
            description_en=company.description_en,
            description_pl=company.description_pl,
            description_fr=company.description_fr,
            description_de=company.description_de
        ))
        
        # Ждем завершения обеих операций
        user, translations = await asyncio.gather(user_task, translation_task)

        # Обновляем данные переведенными значениями
        company.name_uk = translations['name_uk']
        company.name_en = translations['name_en']
        company.name_pl = translations['name_pl']
        company.name_fr = translations['name_fr']
        company.name_de = translations['name_de']
        
        company.description_uk = translations['description_uk']
        company.description_en = translations['description_en']
        company.description_pl = translations['description_pl']
        company.description_fr = translations['description_fr']
        company.description_de = translations['description_de']

        # Генерируем slug если не указан
        if company.slug_name is None:
            company.slug_name = slugify(company.name)

        result = await CompanyCRUD.create_company(user, company)
        
        # Генерируем слаги для всех языков
        from api_old.slug_utils import generate_company_slugs
        slugs = await generate_company_slugs(
            name_uk=translations['name_uk'],
            name_en=translations['name_en'],
            name_pl=translations['name_pl'],
            name_fr=translations['name_fr'],
            name_de=translations['name_de'],
            company_id=result.id
        )
        
        # Обновляем компанию со слагами
        await CompanyCRUD.update_company(result.id, slugs)
        
        return {
            "success": True,
            "message": "Компания успешно создана",
            "company_id": result.id,
            "company": result
        }

    @staticmethod
    async def create_company_fast(request: Request, company: CompanyCreateSchema):
        """
        Сверхбыстрое создание компании с ленивым переводом
        """
        import asyncio
        
        # Получаем пользователя
        user = await get_current_user(request)
        
        # Генерируем slug если не указан
        if company.slug_name is None:
            company.slug_name = slugify(company.name)
        
        # Создаем компанию сразу (без переводов)
        result = await CompanyCRUD.create_company(user, company)
        
        # Запускаем перевод в фоне (не ждем)
        translation_task = asyncio.create_task(auto_translate_company_fields(
            name=company.name,
            description_uk=company.description_uk,
            description_en=company.description_en,
            description_pl=company.description_pl,
            description_fr=company.description_fr,
            description_de=company.description_de
        ))
        
        # Запускаем обновление переводов в фоне
        async def update_translations():
            try:
                translations = await translation_task
                # Обновляем данные переведенными значениями
                update_data = {
                    'name_uk': translations['name_uk'],
                    'name_en': translations['name_en'],
                    'name_pl': translations['name_pl'],
                    'name_fr': translations['name_fr'],
                    'name_de': translations['name_de'],
                    'description_uk': translations['description_uk'],
                    'description_en': translations['description_en'],
                    'description_pl': translations['description_pl'],
                    'description_fr': translations['description_fr'],
                    'description_de': translations['description_de'],
                    'auto_translated_fields': translations['auto_translated_fields']
                }
                
                # Генерируем слаги для всех языков
                from api_old.slug_utils import generate_company_slugs
                slugs = await generate_company_slugs(
                    name_uk=translations['name_uk'],
                    name_en=translations['name_en'],
                    name_pl=translations['name_pl'],
                    name_fr=translations['name_fr'],
                    name_de=translations['name_de'],
                    company_id=result.id
                )
                
                # Добавляем слаги к данным обновления
                update_data.update(slugs)
                
                # Обновляем компанию с переводами и слагами
                await CompanyCRUD.update_company(result.id, update_data)
                
            except Exception as e:
                print(f"Background translation update failed for company {result.id}: {e}")
        
        # Запускаем обновление в фоне
        asyncio.create_task(update_translations())
        
        return {
            "success": True,
            "message": "Компания успешно создана (переводы обновляются в фоне)",
            "company_id": result.id,
            "company": result
        }

    @staticmethod
    async def update_company(company_id: int, company: CompanyUpdateSchema):
        data = company.model_dump(exclude_unset=True)
        result = await CompanyCRUD.update_company(company_id, data)
        return result


    @staticmethod
    async def delete_company(company_id: int):
        result = await CompanyCRUD.delete_company(company_id)
        return result

