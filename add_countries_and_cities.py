import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise, run_async
from models import Country, City
from api_old.slug_utils import generate_slug

from dotenv import load_dotenv
load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD", "WordPass_!forPostgres_%40")

async def init():
    await Tortoise.init(
        db_url=f'postgres://postgres:{DB_PASSWORD}@localhost:5432/makeasap_dev',
        modules={"models": [
            "models.user",
            "models.actions",
            "models.categories",
            "models.places",
         ]},    )
    await Tortoise.generate_schemas()

    # Список стран с переводами
    countries_data = [
        {
            'name_uk': 'Україна',
            'name_en': 'Ukraine',
            'name_pl': 'Ukraina',
            'name_fr': 'Ukraine',
            'name_de': 'Ukraine'
        },
        {
            'name_uk': 'Польща',
            'name_en': 'Poland',
            'name_pl': 'Polska',
            'name_fr': 'Pologne',
            'name_de': 'Polen'
        },
        {
            'name_uk': 'Франція',
            'name_en': 'France',
            'name_pl': 'Francja',
            'name_fr': 'France',
            'name_de': 'Frankreich'
        },
        {
            'name_uk': 'Німеччина',
            'name_en': 'Germany',
            'name_pl': 'Niemcy',
            'name_fr': 'Allemagne',
            'name_de': 'Deutschland'
        },
        {
            'name_uk': 'Інше',
            'name_en': 'Other',
            'name_pl': 'Inne',
            'name_fr': 'Autre',
            'name_de': 'Sonstiges'
        }
    ]

    # Очистка существующих данных
    await City.all().delete()
    await Country.all().delete()

    # Добавление стран
    countries = {}
    for country_data in countries_data:
        country = await Country.create(
            name_uk=country_data['name_uk'],
            name_en=country_data['name_en'],
            name_pl=country_data['name_pl'],
            name_fr=country_data['name_fr'],
            name_de=country_data['name_de'],
            slug_uk=generate_slug(country_data['name_uk']),
            slug_en=generate_slug(country_data['name_en']),
            slug_pl=generate_slug(country_data['name_pl']),
            slug_fr=generate_slug(country_data['name_fr']),
            slug_de=generate_slug(country_data['name_de'])
        )
        countries[country_data['name_uk']] = country

    # Города Украины
    ukraine_cities = [
        {'uk': 'Київ', 'en': 'Kyiv', 'pl': 'Kijów', 'fr': 'Kiev', 'de': 'Kiew'},
        {'uk': 'Харків', 'en': 'Kharkiv', 'pl': 'Charków', 'fr': 'Kharkiv', 'de': 'Charkiw'},
        {'uk': 'Одеса', 'en': 'Odesa', 'pl': 'Odessa', 'fr': 'Odessa', 'de': 'Odessa'},
        {'uk': 'Дніпро', 'en': 'Dnipro', 'pl': 'Dniepr', 'fr': 'Dniepr', 'de': 'Dnepr'},
        {'uk': 'Донецьк', 'en': 'Donetsk', 'pl': 'Donieck', 'fr': 'Donetsk', 'de': 'Donezk'},
        {'uk': 'Запоріжжя', 'en': 'Zaporizhzhia', 'pl': 'Zaporoże', 'fr': 'Zaporijjia', 'de': 'Saporischschja'},
        {'uk': 'Львів', 'en': 'Lviv', 'pl': 'Lwów', 'fr': 'Lviv', 'de': 'Lwiw'},
        {'uk': 'Кривий Ріг', 'en': 'Kryvyi Rih', 'pl': 'Krzywy Róg', 'fr': 'Kryvy Rih', 'de': 'Krywyj Rih'},
        {'uk': 'Миколаїв', 'en': 'Mykolaiv', 'pl': 'Mikołajów', 'fr': 'Mykolayiv', 'de': 'Mykolajiw'},
        {'uk': 'Маріуполь', 'en': 'Mariupol', 'pl': 'Mariupol', 'fr': 'Marioupol', 'de': 'Mariupol'},
        {'uk': 'Луганськ', 'en': 'Luhansk', 'pl': 'Ługańsk', 'fr': 'Lougansk', 'de': 'Lugansk'},
        {'uk': 'Вінниця', 'en': 'Vinnytsia', 'pl': 'Winnica', 'fr': 'Vinnytsia', 'de': 'Winnyzja'},
        {'uk': 'Херсон', 'en': 'Kherson', 'pl': 'Chersoń', 'fr': 'Kherson', 'de': 'Cherson'},
        {'uk': 'Полтава', 'en': 'Poltava', 'pl': 'Połtawa', 'fr': 'Poltava', 'de': 'Poltawa'},
        {'uk': 'Чернігів', 'en': 'Chernihiv', 'pl': 'Czernihów', 'fr': 'Tchernihiv', 'de': 'Tschernihiw'},
        {'uk': 'Черкаси', 'en': 'Cherkasy', 'pl': 'Czerkasy', 'fr': 'Tcherkassy', 'de': 'Tscherkassy'},
        {'uk': 'Хмельницький', 'en': 'Khmelnytskyi', 'pl': 'Chmielnicki', 'fr': 'Khmelnytskyy', 'de': 'Chmelnyzkyj'},
        {'uk': 'Житомир', 'en': 'Zhytomyr', 'pl': 'Żytomierz', 'fr': 'Jytomyr', 'de': 'Schytomyr'},
        {'uk': 'Суми', 'en': 'Sumy', 'pl': 'Sumy', 'fr': 'Soumy', 'de': 'Sumy'},
        {'uk': 'Тернопіль', 'en': 'Ternopil', 'pl': 'Tarnopol', 'fr': 'Ternopil', 'de': 'Ternopil'},
        {'uk': 'Чернівці', 'en': 'Chernivtsi', 'pl': 'Czerniowce', 'fr': 'Tchernivtsi', 'de': 'Czernowitz'},
        {'uk': 'Івано-Франківськ', 'en': 'Ivano-Frankivsk', 'pl': 'Iwano-Frankiwsk', 'fr': 'Ivano-Frankivsk', 'de': 'Iwano-Frankiwsk'},
        {'uk': 'Ужгород', 'en': 'Uzhhorod', 'pl': 'Użgorod', 'fr': 'Oujhorod', 'de': 'Uschhorod'},
        {'uk': 'Рівне', 'en': 'Rivne', 'pl': 'Równe', 'fr': 'Rivne', 'de': 'Riwne'},
        {'uk': 'Луцьк', 'en': 'Lutsk', 'pl': 'Łuck', 'fr': 'Loutsk', 'de': 'Luzk'}
    ]

    # Добавление городов Украины
    for city_data in ukraine_cities:
        await City.create(
            country=countries['Україна'],
            name_uk=city_data['uk'],
            name_en=city_data['en'],
            name_pl=city_data['pl'],
            name_fr=city_data['fr'],
            name_de=city_data['de'],
            slug_uk=generate_slug(city_data['uk']),
            slug_en=generate_slug(city_data['en']),
            slug_pl=generate_slug(city_data['pl']),
            slug_fr=generate_slug(city_data['fr']),
            slug_de=generate_slug(city_data['de'])
        )

    # Города Польши
    poland_cities = [
        {'uk': 'Варшава', 'en': 'Warsaw', 'pl': 'Warszawa', 'fr': 'Varsovie', 'de': 'Warschau'},
        {'uk': 'Краків', 'en': 'Krakow', 'pl': 'Kraków', 'fr': 'Cracovie', 'de': 'Krakau'},
        {'uk': 'Лодзь', 'en': 'Lodz', 'pl': 'Łódź', 'fr': 'Lodz', 'de': 'Lodz'},
        {'uk': 'Вроцлав', 'en': 'Wroclaw', 'pl': 'Wrocław', 'fr': 'Wroclaw', 'de': 'Breslau'},
        {'uk': 'Познань', 'en': 'Poznan', 'pl': 'Poznań', 'fr': 'Poznan', 'de': 'Posen'},
        {'uk': 'Гданськ', 'en': 'Gdansk', 'pl': 'Gdańsk', 'fr': 'Gdansk', 'de': 'Danzig'},
        {'uk': 'Щецин', 'en': 'Szczecin', 'pl': 'Szczecin', 'fr': 'Szczecin', 'de': 'Stettin'},
        {'uk': 'Бидгощ', 'en': 'Bydgoszcz', 'pl': 'Bydgoszcz', 'fr': 'Bydgoszcz', 'de': 'Bromberg'},
        {'uk': 'Люблін', 'en': 'Lublin', 'pl': 'Lublin', 'fr': 'Lublin', 'de': 'Lublin'},
        {'uk': 'Катовиці', 'en': 'Katowice', 'pl': 'Katowice', 'fr': 'Katowice', 'de': 'Kattowitz'}
    ]

    # Добавление городов Польши
    for city_data in poland_cities:
        await City.create(
            country=countries['Польща'],
            name_uk=city_data['uk'],
            name_en=city_data['en'],
            name_pl=city_data['pl'],
            name_fr=city_data['fr'],
            name_de=city_data['de'],
            slug_uk=generate_slug(city_data['uk']),
            slug_en=generate_slug(city_data['en']),
            slug_pl=generate_slug(city_data['pl']),
            slug_fr=generate_slug(city_data['fr']),
            slug_de=generate_slug(city_data['de'])
        )

    # Города Франции
    france_cities = [
        {'uk': 'Париж', 'en': 'Paris', 'pl': 'Paryż', 'fr': 'Paris', 'de': 'Paris'},
        {'uk': 'Марсель', 'en': 'Marseille', 'pl': 'Marsylia', 'fr': 'Marseille', 'de': 'Marseille'},
        {'uk': 'Ліон', 'en': 'Lyon', 'pl': 'Lyon', 'fr': 'Lyon', 'de': 'Lyon'},
        {'uk': 'Тулуза', 'en': 'Toulouse', 'pl': 'Tuluza', 'fr': 'Toulouse', 'de': 'Toulouse'},
        {'uk': 'Ніцца', 'en': 'Nice', 'pl': 'Nicea', 'fr': 'Nice', 'de': 'Nizza'},
        {'uk': 'Нант', 'en': 'Nantes', 'pl': 'Nantes', 'fr': 'Nantes', 'de': 'Nantes'},
        {'uk': 'Страсбург', 'en': 'Strasbourg', 'pl': 'Strasburg', 'fr': 'Strasbourg', 'de': 'Straßburg'},
        {'uk': 'Монпельє', 'en': 'Montpellier', 'pl': 'Montpellier', 'fr': 'Montpellier', 'de': 'Montpellier'},
        {'uk': 'Бордо', 'en': 'Bordeaux', 'pl': 'Bordeaux', 'fr': 'Bordeaux', 'de': 'Bordeaux'},
        {'uk': 'Лілль', 'en': 'Lille', 'pl': 'Lille', 'fr': 'Lille', 'de': 'Lille'}
    ]

    # Добавление городов Франции
    for city_data in france_cities:
        await City.create(
            country=countries['Франція'],
            name_uk=city_data['uk'],
            name_en=city_data['en'],
            name_pl=city_data['pl'],
            name_fr=city_data['fr'],
            name_de=city_data['de'],
            slug_uk=generate_slug(city_data['uk']),
            slug_en=generate_slug(city_data['en']),
            slug_pl=generate_slug(city_data['pl']),
            slug_fr=generate_slug(city_data['fr']),
            slug_de=generate_slug(city_data['de'])
        )

    # Города Германии
    germany_cities = [
        {'uk': 'Берлін', 'en': 'Berlin', 'pl': 'Berlin', 'fr': 'Berlin', 'de': 'Berlin'},
        {'uk': 'Гамбург', 'en': 'Hamburg', 'pl': 'Hamburg', 'fr': 'Hambourg', 'de': 'Hamburg'},
        {'uk': 'Мюнхен', 'en': 'Munich', 'pl': 'Monachium', 'fr': 'Munich', 'de': 'München'},
        {'uk': 'Кельн', 'en': 'Cologne', 'pl': 'Kolonia', 'fr': 'Cologne', 'de': 'Köln'},
        {'uk': 'Франкфурт', 'en': 'Frankfurt', 'pl': 'Frankfurt', 'fr': 'Francfort', 'de': 'Frankfurt'},
        {'uk': 'Штутгарт', 'en': 'Stuttgart', 'pl': 'Stuttgart', 'fr': 'Stuttgart', 'de': 'Stuttgart'},
        {'uk': 'Дюссельдорф', 'en': 'Dusseldorf', 'pl': 'Düsseldorf', 'fr': 'Düsseldorf', 'de': 'Düsseldorf'},
        {'uk': 'Лейпциг', 'en': 'Leipzig', 'pl': 'Lipsk', 'fr': 'Leipzig', 'de': 'Leipzig'},
        {'uk': 'Дортмунд', 'en': 'Dortmund', 'pl': 'Dortmund', 'fr': 'Dortmund', 'de': 'Dortmund'},
        {'uk': 'Ессен', 'en': 'Essen', 'pl': 'Essen', 'fr': 'Essen', 'de': 'Essen'}
    ]

    # Добавление городов Германии
    for city_data in germany_cities:
        await City.create(
            country=countries['Німеччина'],
            name_uk=city_data['uk'],
            name_en=city_data['en'],
            name_pl=city_data['pl'],
            name_fr=city_data['fr'],
            name_de=city_data['de'],
            slug_uk=generate_slug(city_data['uk']),
            slug_en=generate_slug(city_data['en']),
            slug_pl=generate_slug(city_data['pl']),
            slug_fr=generate_slug(city_data['fr']),
            slug_de=generate_slug(city_data['de'])
        )

    print("Страны и города успешно добавлены!")
    await Tortoise.close_connections()

if __name__ == "__main__":
    run_async(init()) 
    print(Country.all())