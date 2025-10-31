from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Request, Query, HTTPException

from routers.secur import get_current_user
from schemas.company import PaginationParams, CompanyCreateSchema, CompanyUpdateSchema
from services.company import CompanyService


router = APIRouter()

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]


@router.get('/companies')
async def get_companies(
    pagination: PaginationDep,
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("relevance"),
):
    companies = await CompanyService.get_all_companies(
        limit=pagination.limit, 
        offset=pagination.offset,
        category=category,
        subcategory=subcategory,
        country=country,
        city=city,
        search=search,
        sort=sort
    )
    return companies


@router.get('/companies/{company_id}')
async def get_company_by_id(company_id: int):
    company = await CompanyService.get_company_by_id(company_id)
    return company

@router.get('/companies/slug/{slug_with_id}')
async def get_company_by_slug(slug_with_id: str):
    """Get company by slug in format: slug-id"""
    if '-' not in slug_with_id:
        raise HTTPException(status_code=400, detail="Invalid slug format. Expected: slug-id")

    parts = slug_with_id.rsplit('-', 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid slug format. Expected: slug-id")
    
    slug_part, id_part = parts
    
    try:
        company_id = int(id_part)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid company ID in slug")
    
    company = await CompanyService.get_company_by_slug_and_id(slug_part, company_id)
    return company


@router.get('/companies/slug/{company_slug}/{company_id}')
async def get_company_by_slug(company_slug: str, company_id: str):
    company = await CompanyService.get_company_by_slug(company_slug, int(company_id))
    return company


@router.get('/companies/profile/get_companies')
async def get_company_by_owner(request: Request):
    user = await get_current_user(request)
    company = await CompanyService.get_company_by_owner(int(user.id))
    return company

@router.post('/companies')
async def create_company(request: Request, company: CompanyCreateSchema):
    result = await CompanyService.create_company(request, company)
    return result

@router.post('/companies-fast')
async def create_company_fast(request: Request, company: CompanyCreateSchema):
    """Fast company creation with lazy background translation"""
    result = await CompanyService.create_company_fast(request, company)
    return result


@router.put('/companies/{company_id}')
async def update_company(company_id: int, company: CompanyUpdateSchema):
    result = await CompanyService.update_company(company_id, company)
    return result


@router.delete('/companies/{company_id}')
async def delete_company(company_id: int):
    result = await CompanyService.delete_company(company_id)
    return result