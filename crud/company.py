from fastapi.responses import JSONResponse
from models import Company, Country, City
from schemas.company import CompanyCreateSchema
from tortoise.expressions import Q


class CompanyCRUD:
    @staticmethod
    async def get_all_companies(limit, offset, category=None, subcategory=None, country=None, city=None, search=None, sort="relevance"):
        # Оптимизированный запрос с select_related для владельца и prefetch для ManyToMany
        query = Company.all().select_related('owner').prefetch_related('categories', 'subcategories')
        
        # Применяем фильтры в порядке селективности
        
        # Страна (наиболее селективный)
        if country:
            query = query.filter(country__icontains=country)
            
        # Город
        if city:
            query = query.filter(city__icontains=city)
        
        # Категории
        if category:
            try:
                category_id = int(category)
                query = query.filter(categories__id=category_id)
            except (ValueError, TypeError):
                pass
        
        # Подкатегории
        if subcategory:
            try:
                subcategory_id = int(subcategory)
                query = query.filter(subcategories__id=subcategory_id)
            except (ValueError, TypeError):
                pass
            
        # Поиск по тексту (наиболее затратный - применяем последним)
        if search:
            search_lower = search.lower()
            # Оптимизируем поиск - сначала по имени, потом по описанию
            query = query.filter(
                Q(name__icontains=search_lower) |
                Q(description_uk__icontains=search_lower) |
                Q(description_en__icontains=search_lower) |
                Q(description_pl__icontains=search_lower) |
                Q(description_fr__icontains=search_lower) |
                Q(description_de__icontains=search_lower)
            )
        
        # Apply sorting
        if sort == "relevance":
            # Keep default order but add created_at for consistency
            query = query.order_by("-id")
        elif sort == "date_desc":
            query = query.order_by("-id")
        elif sort == "date_asc":
            query = query.order_by("id")
        elif sort == "title_asc":
            query = query.order_by("name")
        elif sort == "title_desc":
            query = query.order_by("-name")
        
        # Ограничиваем лимит для защиты
        safe_limit = min(limit, 100) if limit else 20
        
        companies = await query.limit(safe_limit).offset(offset).distinct()
        return companies



    @staticmethod
    async def get_company_by_id(company_id: int):
        company = await Company.get_or_none(id=company_id)
        if company is None:
            return JSONResponse(status_code=404, content={"message": "Company not found"})
        return company


    @staticmethod
    async def get_company_by_slug(company_slug: str, company_id: int):
        company = await Company.filter(slug_name=company_slug, id=company_id).prefetch_related('categories', 'subcategories').first()
        if company is None:
            return JSONResponse(status_code=404, content={"message": "Company not found"})
        return company

    @staticmethod
    async def get_company_by_slug_and_id(slug_part: str, company_id: int):
        """
        Получить компанию по части слага и ID
        Проверяет все слаги на всех языках
        """
        from fastapi import HTTPException
        
        company = await Company.filter(id=company_id).prefetch_related('categories', 'subcategories').first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Проверяем, что слаг соответствует одному из слагов компании
        valid_slugs = []
        if company.slug_uk and company.slug_uk.startswith(slug_part):
            valid_slugs.append(company.slug_uk)
        if company.slug_en and company.slug_en.startswith(slug_part):
            valid_slugs.append(company.slug_en)
        if company.slug_pl and company.slug_pl.startswith(slug_part):
            valid_slugs.append(company.slug_pl)
        if company.slug_fr and company.slug_fr.startswith(slug_part):
            valid_slugs.append(company.slug_fr)
        if company.slug_de and company.slug_de.startswith(slug_part):
            valid_slugs.append(company.slug_de)
        
        if not valid_slugs:
            raise HTTPException(status_code=404, detail="Company not found with this slug")
        
        return company


    @staticmethod
    async def get_company_by_owner(owner_id):
        companies = await Company.filter(owner_id=owner_id).prefetch_related('categories', 'subcategories').all()
        print(companies)
        return companies

    @staticmethod
    async def create_company(owner, company: CompanyCreateSchema):
        import asyncio
        from models import Category, UnderCategory
        
        # Получаем страну и город
        country = None
        city = None
        
        if company.country:
            country = await Country.filter(id=company.country).first()
            company.country = country.name_en if country else None
        if company.city:
            city = await City.filter(id=company.city).first()
            company.city = city.name_en if city else None

        data = company.model_dump(exclude_unset=True)
        data["owner_id"] = owner.id

        # Extract categories for ManyToMany relationship
        category_ids = data.pop('category', []) or []
        under_category_ids = data.pop('under_category', []) or []

        # Создаем компанию
        created_company = await Company.create(**data)
        
        # Добавляем категории
        if category_ids:
            categories = await Category.filter(id__in=category_ids).all()
            await created_company.categories.add(*categories)
            
        if under_category_ids:
            subcategories = await UnderCategory.filter(id__in=under_category_ids).all()
            await created_company.subcategories.add(*subcategories)

        return created_company

    @staticmethod
    async def update_company(company_id: int, data: dict):
        from models import Category, UnderCategory
        
        company = await Company.get(id=company_id)
        
        # Handle country and city - convert IDs to names
        if 'country' in data and data['country'] is not None:
            country = await Country.filter(id=data['country']).first()
            if country:
                data['country'] = country.name_en
        
        if 'city' in data and data['city'] is not None:
            city = await City.filter(id=data['city']).first()
            if city:
                data['city'] = city.name_en
        
        # Handle categories using ManyToMany
        category_ids = data.pop('category', None)
        under_category_ids = data.pop('under_category', None)
        
        # Update regular fields
        for field, value in data.items():
            if value is not None:
                setattr(company, field, value)
        await company.save()
        
        # Update categories if provided
        if category_ids is not None:
            await company.categories.clear()
            if category_ids:
                categories = await Category.filter(id__in=category_ids).all()
                await company.categories.add(*categories)
        
        if under_category_ids is not None:
            await company.subcategories.clear()
            if under_category_ids:
                subcategories = await UnderCategory.filter(id__in=under_category_ids).all()
                await company.subcategories.add(*subcategories)
        
        return company


    @staticmethod
    async def delete_company(company_id: int):
        company = await Company.get_or_none(id=company_id)
        if company is None:
            return JSONResponse(status_code=404, content={"message": "Company not found"})
        await company.delete()
        return JSONResponse(status_code=200, content={"message": "Company deleted"})