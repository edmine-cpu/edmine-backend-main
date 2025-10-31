
CITY_TRANSLATIONS = {
    'Київ': {'en': 'Kyiv', 'pl': 'Kijów', 'fr': 'Kiev', 'de': 'Kiew'},
    'Харків': {'en': 'Kharkiv', 'pl': 'Charków', 'fr': 'Kharkiv', 'de': 'Charkiw'},
    'Одеса': {'en': 'Odesa', 'pl': 'Odessa', 'fr': 'Odessa', 'de': 'Odessa'},
    'Дніпро': {'en': 'Dnipro', 'pl': 'Dniepr', 'fr': 'Dniepr', 'de': 'Dnepr'},
    'Донецьк': {'en': 'Donetsk', 'pl': 'Donieck', 'fr': 'Donetsk', 'de': 'Donezk'},
    'Запоріжжя': {'en': 'Zaporizhzhia', 'pl': 'Zaporoże', 'fr': 'Zaporijjia', 'de': 'Saporischschja'},
    'Львів': {'en': 'Lviv', 'pl': 'Lwów', 'fr': 'Lviv', 'de': 'Lwiw'},
    'Кривий Ріг': {'en': 'Kryvyi Rih', 'pl': 'Krzywy Róg', 'fr': 'Kryvy Rih', 'de': 'Krywyj Rih'},
    'Миколаїв': {'en': 'Mykolaiv', 'pl': 'Mikołajów', 'fr': 'Mykolayiv', 'de': 'Mykolajiw'},
    'Маріуполь': {'en': 'Mariupol', 'pl': 'Mariupol', 'fr': 'Marioupol', 'de': 'Mariupol'},
    'Луганськ': {'en': 'Luhansk', 'pl': 'Ługańsk', 'fr': 'Lougansk', 'de': 'Lugansk'},
    'Вінниця': {'en': 'Vinnytsia', 'pl': 'Winnica', 'fr': 'Vinnytsia', 'de': 'Winnyzja'},
    'Херсон': {'en': 'Kherson', 'pl': 'Chersoń', 'fr': 'Kherson', 'de': 'Cherson'},
    'Полтава': {'en': 'Poltava', 'pl': 'Połtawa', 'fr': 'Poltava', 'de': 'Poltawa'},
    'Чернігів': {'en': 'Chernihiv', 'pl': 'Czernihów', 'fr': 'Tchernihiv', 'de': 'Tschernihiw'},
    'Черкаси': {'en': 'Cherkasy', 'pl': 'Czerkasy', 'fr': 'Tcherkassy', 'de': 'Tscherkassy'},
    'Хмельницький': {'en': 'Khmelnytskyi', 'pl': 'Chmielnicki', 'fr': 'Khmelnytskyy', 'de': 'Chmelnyzkyj'},
    'Житомир': {'en': 'Zhytomyr', 'pl': 'Żytomierz', 'fr': 'Jytomyr', 'de': 'Schytomyr'},
    'Суми': {'en': 'Sumy', 'pl': 'Sumy', 'fr': 'Soumy', 'de': 'Sumy'},
    'Тернопіль': {'en': 'Ternopil', 'pl': 'Tarnopol', 'fr': 'Ternopil', 'de': 'Ternopil'},
    'Чернівці': {'en': 'Chernivtsi', 'pl': 'Czerniowce', 'fr': 'Tchernivtsi', 'de': 'Czernowitz'},
    'Івано-Франківськ': {'en': 'Ivano-Frankivsk', 'pl': 'Iwano-Frankiwsk', 'fr': 'Ivano-Frankivsk', 'de': 'Iwano-Frankiwsk'},
    'Ужгород': {'en': 'Uzhhorod', 'pl': 'Użgorod', 'fr': 'Oujhorod', 'de': 'Uschhorod'},
    'Рівне': {'en': 'Rivne', 'pl': 'Równe', 'fr': 'Rivne', 'de': 'Riwne'},
    'Луцьк': {'en': 'Lutsk', 'pl': 'Łuck', 'fr': 'Loutsk', 'de': 'Luzk'}
}

def get_city_name(city_uk: str, lang: str = 'uk') -> str:
    """Возвращает название города на указанном языке"""
    if lang == 'uk':
        return city_uk
    if city_uk in CITY_TRANSLATIONS and lang in CITY_TRANSLATIONS[city_uk]:
        return CITY_TRANSLATIONS[city_uk][lang]
    return city_uk  

CITIES = [
    'Київ',
    'Харків',
    'Одеса',
    'Дніпро',
    'Донецьк',
    'Запоріжжя',
    'Львів',
    'Кривий Ріг',
    'Миколаїв',
    'Маріуполь',
    'Луганськ',
    'Вінниця',
    'Херсон',
    'Полтава',
    'Чернігів',
    'Черкаси',
    'Хмельницький',
    'Житомир',
    'Суми',
    'Рівне',
    'Івано-Франківськ',
    'Тернопіль',
    'Луцьк',
    'Ужгород',
    'Кам\'янець-Подільський',
    'Дрогобич',
    'Біла Церква',
    'Нікополь',
    'Бердянськ',
    'Павлоград',
    'Кременчук',
    'Мелітополь',
    'Керч',
    'Краматорськ',
    'Слов\'янськ',
    'Бровари',
    'Ірпінь',
    'Буча',
]

REGIONS = [
    'Київська область',
    'Харківська область',
    'Одеська область',
    'Дніпропетровська область',
    'Донецька область',
    'Запорізька область',
    'Львівська область',
    'Миколаївська область',
    'Вінницька область',
    'Херсонська область',
    'Полтавська область',
    'Чернігівська область',
    'Черкаська область',
    'Хмельницька область',
    'Житомирська область',
    'Сумська область',
    'Рівненська область',
    'Івано-Франківська область',
    'Тернопільська область',
    'Волинська область',
    'Закарпатська область',
]

LOCATIONS = sorted(set(CITIES + REGIONS)) 