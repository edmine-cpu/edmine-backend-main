"""
Скрипт для заполнения базы данных тестовыми данными
Использует: pydantic-settings для конфигурации
Запуск: python seed_database.py [options]
"""
import asyncio
import sys
from typing import List, Dict
import argparse
from tortoise import Tortoise
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from settings import settings
from models.categories import Category, UnderCategory
from models.places import Country, City
from api_old.slug_utils import generate_slug

console = Console()


# ==================== ДАННЫЕ ДЛЯ ЗАПОЛНЕНИЯ ====================

CATEGORIES_DATA = [
    {
        'name': 'web_development',
        'name_uk': 'Веб-розробка',
        'name_en': 'Web Development',
        'name_pl': 'Tworzenie stron WWW',
        'name_fr': 'Développement Web',
        'name_de': 'Webentwicklung',
        'undercategories': [
            {'name_uk': 'Frontend розробка', 'name_en': 'Frontend Development', 'name_pl': 'Frontend', 'name_fr': 'Développement Frontend', 'name_de': 'Frontend-Entwicklung'},
            {'name_uk': 'Backend розробка', 'name_en': 'Backend Development', 'name_pl': 'Backend', 'name_fr': 'Développement Backend', 'name_de': 'Backend-Entwicklung'},
            {'name_uk': 'Повна розробка сайту', 'name_en': 'Full-stack Development', 'name_pl': 'Full-stack', 'name_fr': 'Développement Full-stack', 'name_de': 'Full-Stack-Entwicklung'}
        ]
    },
    {
        'name': 'mobile_development',
        'name_uk': 'Мобільна розробка',
        'name_en': 'Mobile Development',
        'name_pl': 'Tworzenie aplikacji mobilnych',
        'name_fr': 'Développement Mobile',
        'name_de': 'Mobile Entwicklung',
        'undercategories': [
            {'name_uk': 'iOS додатки', 'name_en': 'iOS Apps', 'name_pl': 'Aplikacje iOS', 'name_fr': 'Applications iOS', 'name_de': 'iOS Apps'},
            {'name_uk': 'Android додатки', 'name_en': 'Android Apps', 'name_pl': 'Aplikacje Android', 'name_fr': 'Applications Android', 'name_de': 'Android Apps'},
            {'name_uk': 'Кросплатформені додатки', 'name_en': 'Cross-platform Apps', 'name_pl': 'Aplikacje cross-platform', 'name_fr': 'Applications multiplateformes', 'name_de': 'Cross-Plattform-Apps'}
        ]
    },
    {
        'name': 'graphic_design',
        'name_uk': 'Графічний дизайн',
        'name_en': 'Graphic Design',
        'name_pl': 'Projektowanie graficzne',
        'name_fr': 'Design Graphique',
        'name_de': 'Grafikdesign',
        'undercategories': [
            {'name_uk': 'Логотипи та брендинг', 'name_en': 'Logos & Branding', 'name_pl': 'Logotypy i branding', 'name_fr': 'Logos et Branding', 'name_de': 'Logos & Branding'},
            {'name_uk': 'Ілюстрації', 'name_en': 'Illustrations', 'name_pl': 'Ilustracje', 'name_fr': 'Illustrations', 'name_de': 'Illustrationen'},
            {'name_uk': 'Дизайн соцмереж', 'name_en': 'Social Media Design', 'name_pl': 'Projektowanie social media', 'name_fr': 'Design des réseaux sociaux', 'name_de': 'Social Media Design'}
        ]
    },
    {
        'name': 'digital_marketing',
        'name_uk': 'Цифровий маркетинг',
        'name_en': 'Digital Marketing',
        'name_pl': 'Marketing cyfrowy',
        'name_fr': 'Marketing Numérique',
        'name_de': 'Digital Marketing',
        'undercategories': [
            {'name_uk': 'SEO оптимізація', 'name_en': 'SEO', 'name_pl': 'SEO', 'name_fr': 'SEO', 'name_de': 'SEO'},
            {'name_uk': 'SMM', 'name_en': 'Social Media Marketing', 'name_pl': 'Marketing w social media', 'name_fr': 'Marketing des réseaux sociaux', 'name_de': 'Social Media Marketing'},
            {'name_uk': 'Email маркетинг', 'name_en': 'Email Marketing', 'name_pl': 'Email marketing', 'name_fr': 'Marketing par email', 'name_de': 'E-Mail Marketing'}
        ]
    },
    {
        'name': 'writing',
        'name_uk': 'Написання текстів',
        'name_en': 'Writing',
        'name_pl': 'Pisanie tekstów',
        'name_fr': 'Rédaction',
        'name_de': 'Schreiben',
        'undercategories': [
            {'name_uk': 'Статті та блоги', 'name_en': 'Articles & Blogs', 'name_pl': 'Artykuły i blogi', 'name_fr': 'Articles & Blogs', 'name_de': 'Artikel & Blogs'},
            {'name_uk': 'Копірайтинг', 'name_en': 'Copywriting', 'name_pl': 'Copywriting', 'name_fr': 'Rédaction publicitaire', 'name_de': 'Werbetexten'},
            {'name_uk': 'Технічна документація', 'name_en': 'Technical Writing', 'name_pl': 'Dokumentacja techniczna', 'name_fr': 'Rédaction technique', 'name_de': 'Technische Dokumentation'}
        ]
    },
    {
        'name': 'translation',
        'name_uk': 'Переклади',
        'name_en': 'Translation',
        'name_pl': 'Tłumaczenia',
        'name_fr': 'Traduction',
        'name_de': 'Übersetzung',
        'undercategories': [
            {'name_uk': 'Технічний переклад', 'name_en': 'Technical Translation', 'name_pl': 'Tłumaczenia techniczne', 'name_fr': 'Traduction technique', 'name_de': 'Technische Übersetzung'},
            {'name_uk': 'Літературний переклад', 'name_en': 'Literary Translation', 'name_pl': 'Tłumaczenia literackie', 'name_fr': 'Traduction littéraire', 'name_de': 'Literarische Übersetzung'},
            {'name_uk': 'Сайт та додатки', 'name_en': 'Website & App Translation', 'name_pl': 'Tłumaczenia stron i aplikacji', 'name_fr': 'Traduction de sites et apps', 'name_de': 'Website & App Übersetzung'}
        ]
    },
    {
        'name': 'video_editing',
        'name_uk': 'Відеомонтаж',
        'name_en': 'Video Editing',
        'name_pl': 'Montaż wideo',
        'name_fr': 'Montage Vidéo',
        'name_de': 'Videobearbeitung',
        'undercategories': [
            {'name_uk': 'Реклама та промо', 'name_en': 'Ads & Promo', 'name_pl': 'Reklamy i promo', 'name_fr': 'Publicités & Promo', 'name_de': 'Werbung & Promo'},
            {'name_uk': 'Монтаж YouTube', 'name_en': 'YouTube Editing', 'name_pl': 'Montaż YouTube', 'name_fr': 'Montage YouTube', 'name_de': 'YouTube-Bearbeitung'},
            {'name_uk': 'Анімація', 'name_en': 'Animation', 'name_pl': 'Animacja', 'name_fr': 'Animation', 'name_de': 'Animation'}
        ]
    },
    {
        'name': 'seo',
        'name_uk': 'SEO',
        'name_en': 'SEO',
        'name_pl': 'SEO',
        'name_fr': 'SEO',
        'name_de': 'SEO',
        'undercategories': [
            {'name_uk': 'Оптимізація сайтів', 'name_en': 'Website Optimization', 'name_pl': 'Optymalizacja stron', 'name_fr': 'Optimisation de sites web', 'name_de': 'Website-Optimierung'},
            {'name_uk': 'Лінкбілдінг', 'name_en': 'Link Building', 'name_pl': 'Link building', 'name_fr': 'Link Building', 'name_de': 'Linkbuilding'},
            {'name_uk': 'Контент стратегія', 'name_en': 'Content Strategy', 'name_pl': 'Strategia treści', 'name_fr': 'Stratégie de contenu', 'name_de': 'Content-Strategie'}
        ]
    },
    {
        'name': 'virtual_assistant',
        'name_uk': 'Віртуальний асистент',
        'name_en': 'Virtual Assistant',
        'name_pl': 'Wirtualny Asystent',
        'name_fr': 'Assistant Virtuel',
        'name_de': 'Virtueller Assistent',
        'undercategories': [
            {'name_uk': 'Адміністративна підтримка', 'name_en': 'Administrative Support', 'name_pl': 'Wsparcie administracyjne', 'name_fr': 'Support administratif', 'name_de': 'Administrative Unterstützung'},
            {'name_uk': 'Обробка електронної пошти', 'name_en': 'Email Handling', 'name_pl': 'Obsługa e-maili', 'name_fr': 'Gestion des e-mails', 'name_de': 'E-Mail-Verwaltung'},
            {'name_uk': 'Управління календарем', 'name_en': 'Calendar Management', 'name_pl': 'Zarządzanie kalendarzem', 'name_fr': 'Gestion du calendrier', 'name_de': 'Kalenderverwaltung'}
        ]
    },
    {
        'name': 'ui_ux_design',
        'name_uk': 'UI/UX дизайн',
        'name_en': 'UI/UX Design',
        'name_pl': 'Projektowanie UI/UX',
        'name_fr': 'Design UI/UX',
        'name_de': 'UI/UX-Design',
        'undercategories': [
            {'name_uk': 'UI дизайн', 'name_en': 'UI Design', 'name_pl': 'Projektowanie UI', 'name_fr': 'Design UI', 'name_de': 'UI Design'},
            {'name_uk': 'UX дослідження', 'name_en': 'UX Research', 'name_pl': 'Badania UX', 'name_fr': 'Recherche UX', 'name_de': 'UX-Forschung'},
            {'name_uk': 'Прототипування', 'name_en': 'Prototyping', 'name_pl': 'Prototypowanie', 'name_fr': 'Prototypage', 'name_de': 'Prototyping'}
        ]
    },
]

COUNTRIES_DATA = [
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

CITIES_DATA = {
    'Україна': [
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
    ],
    'Польща': [
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
    ],
    'Франція': [
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
    ],
    'Німеччина': [
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
}


# ==================== ФУНКЦИИ ЗАПОЛНЕНИЯ ====================

async def init_db():
    """Инициализация подключения к БД"""
    await Tortoise.init(
        db_url=await settings.database_url,
        modules={
            "models": [
                "models.user",
                "models.actions",
                "models.categories",
                "models.places",
                "models.chat",
                "models.password_reset",
            ]
        }
    )
    await Tortoise.generate_schemas()


async def close_db():
    """Закрытие подключения к БД"""
    await Tortoise.close_connections()


async def seed_categories(clear: bool = False) -> Dict[str, int]:
    """Заполнение категорий и подкатегорий"""

    if clear:
        deleted_uc = await UnderCategory.all().delete()
        deleted_c = await Category.all().delete()
        console.print(f"[yellow]🗑  Удалено {deleted_c} категорий и {deleted_uc} подкатегорий[/yellow]")

    categories_count = 0
    undercategories_count = 0

    for cat_data in CATEGORIES_DATA:
        # Создаем категорию
        category, created = await Category.get_or_create(
            name=cat_data['name'],
            defaults={
                'name_uk': cat_data['name_uk'],
                'name_en': cat_data['name_en'],
                'name_pl': cat_data['name_pl'],
                'name_fr': cat_data['name_fr'],
                'name_de': cat_data['name_de'],
                'slug_uk': generate_slug(cat_data['name_uk'], 'uk'),
                'slug_en': generate_slug(cat_data['name_en'], 'en'),
                'slug_pl': generate_slug(cat_data['name_pl'], 'pl'),
                'slug_fr': generate_slug(cat_data['name_fr'], 'fr'),
                'slug_de': generate_slug(cat_data['name_de'], 'de'),
            }
        )
        if created:
            categories_count += 1
            console.print(f"[green]  ✓ Категория: {category.name_en}[/green]")

        # Создаем подкатегории
        for uc_data in cat_data['undercategories']:
            undercategory, created = await UnderCategory.get_or_create(
                full_category=category,
                name_uk=uc_data['name_uk'],
                name_en=uc_data['name_en'],
                defaults={
                    'name_pl': uc_data['name_pl'],
                    'name_fr': uc_data['name_fr'],
                    'name_de': uc_data['name_de'],
                    'slug_uk': generate_slug(uc_data['name_uk'], 'uk'),
                    'slug_en': generate_slug(uc_data['name_en'], 'en'),
                    'slug_pl': generate_slug(uc_data['name_pl'], 'pl'),
                    'slug_fr': generate_slug(uc_data['name_fr'], 'fr'),
                    'slug_de': generate_slug(uc_data['name_de'], 'de'),
                }
            )
            if created:
                undercategories_count += 1
                console.print(f"[dim]    • Подкатегория: {undercategory.name_en}[/dim]")

    return {
        'categories': categories_count,
        'undercategories': undercategories_count
    }


async def seed_locations(clear: bool = False) -> Dict[str, int]:
    """Заполнение стран и городов"""

    if clear:
        deleted_cities = await City.all().delete()
        deleted_countries = await Country.all().delete()
        console.print(f"[yellow]🗑  Удалено {deleted_countries} стран и {deleted_cities} городов[/yellow]")

    countries_count = 0
    cities_count = 0
    countries_map = {}

    # Создаем страны
    for country_data in COUNTRIES_DATA:
        country, created = await Country.get_or_create(
            name_en=country_data['name_en'],
            defaults={
                'name_uk': country_data['name_uk'],
                'name_pl': country_data['name_pl'],
                'name_fr': country_data['name_fr'],
                'name_de': country_data['name_de'],
                'slug_uk': generate_slug(country_data['name_uk'], 'uk'),
                'slug_en': generate_slug(country_data['name_en'], 'en'),
                'slug_pl': generate_slug(country_data['name_pl'], 'pl'),
                'slug_fr': generate_slug(country_data['name_fr'], 'fr'),
                'slug_de': generate_slug(country_data['name_de'], 'de'),
            }
        )
        if created:
            countries_count += 1
            console.print(f"[green]  ✓ Страна: {country.name_en}[/green]")
        countries_map[country_data['name_uk']] = country

    # Создаем города
    for country_name_uk, cities in CITIES_DATA.items():
        country = countries_map.get(country_name_uk)
        if not country:
            continue

        for city_data in cities:
            city, created = await City.get_or_create(
                country=country,
                name_uk=city_data['uk'],
                name_en=city_data['en'],
                defaults={
                    'name_pl': city_data['pl'],
                    'name_fr': city_data['fr'],
                    'name_de': city_data['de'],
                    'slug_uk': generate_slug(city_data['uk'], 'uk'),
                    'slug_en': generate_slug(city_data['en'], 'en'),
                    'slug_pl': generate_slug(city_data['pl'], 'pl'),
                    'slug_fr': generate_slug(city_data['fr'], 'fr'),
                    'slug_de': generate_slug(city_data['de'], 'de'),
                }
            )
            if created:
                cities_count += 1
                console.print(f"[dim]    • Город: {city.name_en}[/dim]")

    return {
        'countries': countries_count,
        'cities': cities_count
    }


# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================

async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Заполнение базы данных тестовыми данными')
    parser.add_argument('--all', action='store_true', help='Заполнить все данные')
    parser.add_argument('--categories', action='store_true', help='Заполнить категории и подкатегории')
    parser.add_argument('--locations', action='store_true', help='Заполнить страны и города')
    parser.add_argument('--clear', action='store_true', help='Очистить данные перед заполнением')

    args = parser.parse_args()

    # Если не указаны флаги, показываем справку
    if not (args.all or args.categories or args.locations):
        parser.print_help()
        console.print("\n[yellow]Используйте флаги для указания что заполнять[/yellow]")
        return

    console.print(Panel.fit(
        "[bold cyan]🌱 Заполнение базы данных тестовыми данными[/bold cyan]",
        border_style="cyan"
    ))

    console.print(f"\n[dim]База данных: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}[/dim]\n")

    try:
        # Инициализация БД
        with console.status("[bold green]Подключение к БД...") as status:
            await init_db()
            console.print("[green]✓ Подключение установлено[/green]\n")

        results = {}

        # Заполнение категорий
        if args.all or args.categories:
            console.print("[bold]📁 Заполнение категорий и подкатегорий...[/bold]")
            results['categories'] = await seed_categories(clear=args.clear)
            console.print(f"[green]✓ Добавлено: {results['categories']['categories']} категорий, "
                         f"{results['categories']['undercategories']} подкатегорий[/green]\n")

        # Заполнение локаций
        if args.all or args.locations:
            console.print("[bold]🌍 Заполнение стран и городов...[/bold]")
            results['locations'] = await seed_locations(clear=args.clear)
            console.print(f"[green]✓ Добавлено: {results['locations']['countries']} стран, "
                         f"{results['locations']['cities']} городов[/green]\n")

        # Итоговая таблица
        table = Table(title="Результаты заполнения", show_header=True, header_style="bold magenta")
        table.add_column("Тип данных", style="cyan")
        table.add_column("Количество", justify="right", style="green")

        if 'categories' in results:
            table.add_row("Категории", str(results['categories']['categories']))
            table.add_row("Подкатегории", str(results['categories']['undercategories']))

        if 'locations' in results:
            table.add_row("Страны", str(results['locations']['countries']))
            table.add_row("Города", str(results['locations']['cities']))

        console.print(table)
        console.print("\n[bold green]🎉 Успешно завершено![/bold green]")

    except Exception as e:
        console.print(f"\n[bold red]❌ Ошибка: {e}[/bold red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)
    finally:
        await close_db()


if __name__ == '__main__':
    asyncio.run(main())
