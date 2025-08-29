from fastapi.responses import JSONResponse
from models import Company, Country, City
from schemas.company import CompanyCreateSchema
from tortoise.expressions import Q


class CompanyCRUD:
    @staticmethod
    async def get_all_companies(limit, offset, category=None, subcategory=None, country=None, city=None, search=None, sort="relevance"):
        query = Company.all().prefetch_related('categories', 'subcategories')
        
        # Apply filters
        if category:
            query = query.filter(categories__id=int(category))
        
        if subcategory:
            query = query.filter(subcategories__id=int(subcategory))
            
        if country:
            query = query.filter(country__icontains=country)
            
        if city:
            query = query.filter(city__icontains=city)
            
        if search:
            query = query.filter(
                Q(name__icontains=search) |
                Q(description_uk__icontains=search) |
                Q(description_en__icontains=search) |
                Q(description_pl__icontains=search) |
                Q(description_fr__icontains=search) |
                Q(description_de__icontains=search)
            )
        
        # Apply sorting
        if sort == "relevance":
            # Keep default order
            pass
        elif sort == "date_desc":
            query = query.order_by("-id")
        elif sort == "date_asc":
            query = query.order_by("id")
        elif sort == "title_asc":
            query = query.order_by("name")
        elif sort == "title_desc":
            query = query.order_by("-name")
        
        companies = await query.limit(limit).offset(offset).distinct()
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
    async def get_company_by_owner(owner_id):
        companies = await Company.filter(owner_id=owner_id).prefetch_related('categories', 'subcategories').all()
        print(companies)
        return companies

    @staticmethod
    async def create_company(owner, company: CompanyCreateSchema):
        from models import Category, UnderCategory
        
        country = await Country.filter(id=company.country).first()
        company.country = country.name_en if country else None
        city = await City.filter(id=company.city).first()
        company.city = city.name_en if city else None

        print(company.city, company.country)

        data = company.model_dump(exclude_unset=True)
        data["owner_id"] = owner.id

        # Extract categories for ManyToMany relationship
        category_ids = data.pop('category', []) or []
        under_category_ids = data.pop('under_category', []) or []

        print(data)
        created_company = await Company.create(**data)
        
        # Add categories using ManyToMany
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