from models import City, Country  


class CountryActions(Country):
    @staticmethod
    
    async def get_country_by_id(id: int):
        country = await Country.get_or_none(id=id)
        return country


