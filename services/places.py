from models import Country, City
from crud.places import CountryActions
from fastapi import HTTPException


class CountryServices():
    @staticmethod
    
    async def get_country_by_id(id: int):
        country = await CountryActions.get_country_by_id(id)
        if country is None:
            raise HTTPException(status_code=404, detail="Country not found")
        return country


