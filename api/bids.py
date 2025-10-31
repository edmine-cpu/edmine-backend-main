from fastapi import HTTPException, Query
from typing import List, Optional
from fastapi import APIRouter, Request, Form, UploadFile, File

from schemas.bid import BidVerifyRequest, BidCreateRequest
from services.bids.service import BidService

router = APIRouter()

@router.get("/bids")
async def list_bids(
    category: Optional[str] = Query(None),
    subcategory: Optional[int] = Query(None),
    country: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    sort: Optional[str] = Query("date_desc"),
):
    return await BidService.list_bids(
        category=category,
        subcategory=subcategory,
        country=country,
        city=city,
        search=search,
        limit=limit,
        sort=sort,
    )


@router.get("/bids/{bid_id}")
async def get_bid_by_id(bid_id: int):
    bid = await BidService.get_bid_by_id(bid_id)
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    return bid


@router.post('/{lang}/create-request')
async def create_request(lang: str, request: Request, files: Optional[List[UploadFile]] = File(None)):
    user_role = getattr(request.state, 'user_role', None)
    user_email = getattr(request.state, 'user_email', None)

    form_data = await request.form()
    data = BidCreateRequest(**form_data)

    return await BidService.create_request(data, files, lang, user_role, user_email, request)

@router.post('/{lang}/create-request-fast')
async def create_request_fast(lang: str, request: Request, files: Optional[List[UploadFile]] = File(None)):
    """Fast bid creation with lazy background translation"""
    user_role = getattr(request.state, 'user_role', None)
    user_email = getattr(request.state, 'user_email', None)

    form_data = await request.form()
    data = BidCreateRequest(**form_data)

    return await BidService.create_request_fast(data, files, lang, user_role, user_email, request)


@router.post('/{lang}/verify-request-code')
async def verify_request(lang: str, request: Request):
    form_data = await request.form()
    data = BidVerifyRequest(**form_data)
    return await BidService.verify_request(data, str(request.base_url).rstrip('/'))

@router.post('/submit-response')
async def submit_response(request: Request):
    form_data = await request.form()
    return await BidService.submit_response(
        job_id=int(form_data.get("job_id")),
        name=form_data.get("name"),
        email=form_data.get("email"),
        message=form_data.get("message")
    )


@router.delete('/bid/{bid_id}')
async def delete_bid(request: Request, bid_id: int):
    user_role = getattr(request.state, 'user_role', None)
    return await BidService.delete_bid(bid_id, user_role)
