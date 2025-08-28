from fastapi import APIRouter, Query
from models.places import Country, City
from db.cities import CITIES, REGIONS, LOCATIONS, get_city_name

router = APIRouter()


@router.get('/countries')
async def get_countries(lang: str = Query('uk')):
    """Возвращает список стран на указанном языке"""
    countries = await Country.all()
    result = []
    
    for country in countries:
        if lang == 'uk':
            name = country.name_uk
        elif lang == 'en':
            name = country.name_en
        elif lang == 'pl':
            name = country.name_pl
        elif lang == 'fr':
            name = country.name_fr
        elif lang == 'de':
            name = country.name_de
        else:
            name = country.name_uk
            
        result.append({
            'id': country.id,
            'name': name,
            'slug': getattr(country, f'slug_{lang}', country.slug_uk)
        })
    
    return {'countries': result}


@router.get('/cities')
async def get_cities(lang: str = Query('uk'), country_id: int = Query(None)):
    """Возвращает список городов на указанном языке, опционально фильтруя по стране"""
    query = City.all()
    if country_id:
        query = query.filter(country_id=country_id)
    
    cities = await query.prefetch_related('country')
    result = []
    
    for city in cities:
        if lang == 'uk':
            name = city.name_uk
        elif lang == 'en':
            name = city.name_en
        elif lang == 'pl':
            name = city.name_pl
        elif lang == 'fr':
            name = city.name_fr
        elif lang == 'de':
            name = city.name_de
        else:
            name = city.name_uk
            
        result.append({
            'id': city.id,
            'name': name,
            'country_id': city.country_id,
            'country_name': getattr(city.country, f'name_{lang}', city.country.name_uk),
            'slug': getattr(city, f'slug_{lang}', city.slug_uk)
        })
    
    return {'cities': result}


@router.get('/cities/{country_id}')
async def get_cities_by_country(country_id: int, lang: str = Query('uk')):
    """Возвращает список городов для конкретной страны"""
    cities = await City.filter(country_id=country_id)
    result = []
    
    for city in cities:
        if lang == 'uk':
            name = city.name_uk
        elif lang == 'en':
            name = city.name_en
        elif lang == 'pl':
            name = city.name_pl
        elif lang == 'fr':
            name = city.name_fr
        elif lang == 'de':
            name = city.name_de
        else:
            name = city.name_uk
            
        result.append({
            'id': city.id,
            'name': name,
            'slug': getattr(city, f'slug_{lang}', city.slug_uk)
        })
    
    return {'cities': result}


@router.get('/regions')
async def get_regions(lang: str = Query('uk')):
    """Возвращает список регионов на указанном языке"""
    translated_regions = [get_city_name(region, lang) for region in REGIONS]
    return {'regions': translated_regions}


@router.get('/locations')
async def get_locations(lang: str = Query('uk')):
    """Возвращает список всех локаций на указанном языке"""
    translated_locations = [get_city_name(location, lang) for location in LOCATIONS]
    return {'locations': translated_locations} 