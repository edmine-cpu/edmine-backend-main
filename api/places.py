from fastapi import APIRouter
from models import City, Country
from services.places import CountryServices

router = APIRouter()


@router.get('/country')
async def get_county():
    return await Country.all()


@router.get("/country/{id}")
async def get_country(id: int):
    country = await CountryServices.get_country_by_id(id=id)
    return country


@router.get('/city')
async def get_city():
    return await City.all()