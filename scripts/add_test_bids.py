"""
Скрипт для добавления тестовых бидов в БД с валидными связями
"""
import asyncio
import secrets
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from dotenv import load_dotenv
from models.actions import Bid
from models.user import User
from models.places import Country, City
from models.categories import Category, UnderCategory


async def init_db():
    """Инициализация подключения к БД"""
    load_dotenv()
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    await Tortoise.init(
        db_url=f"postgres://postgres:{DB_PASSWORD}@0.0.0.0:5432/makeasap_dev",
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


async def get_existing_data():
    """Получить существующие ID для связей"""
    # Получаем первые доступные объекты
    users = await User.all().limit(5)
    countries = await Country.all().limit(5)
    cities = await City.all().limit(5)
    categories = await Category.all().limit(5)
    undercategories = await UnderCategory.all().limit(5)

    if not users:
        print("⚠️  Нет пользователей в БД! Создайте хотя бы одного пользователя.")
        return None

    if not countries:
        print("⚠️  Нет стран в БД!")
        return None

    if not cities:
        print("⚠️  Нет городов в БД!")
        return None

    if not categories:
        print("⚠️  Нет категорий в БД!")
        return None

    if not undercategories:
        print("⚠️  Нет подкатегорий в БД!")
        return None

    return {
        "users": users,
        "countries": countries,
        "cities": cities,
        "categories": categories,
        "undercategories": undercategories
    }


async def create_test_bids():
    """Создание тестовых бидов"""
    await init_db()

    # Получаем существующие данные
    data = await get_existing_data()
    if not data:
        print("❌ Не удалось получить данные для создания бидов")
        await Tortoise.close_connections()
        return

    print("✅ Найдены данные для создания бидов:")
    print(f"   - Пользователей: {len(data['users'])}")
    print(f"   - Стран: {len(data['countries'])}")
    print(f"   - Городов: {len(data['cities'])}")
    print(f"   - Категорий: {len(data['categories'])}")
    print(f"   - Подкатегорий: {len(data['undercategories'])}")

    # Тестовые данные на разных языках
    test_bids_data = [
        {
            "main_language": "uk",
            "title_uk": "Розробка сайту на React",
            "description_uk": "Потрібен досвідчений розробник для створення сучасного веб-додатку на React. Бюджет гнучкий.",
            "budget": "3000",
            "budget_type": "fixed"
        },
        {
            "main_language": "en",
            "title_en": "Logo Design for Startup",
            "description_en": "Looking for a creative designer to create a modern logo for our tech startup. Quick turnaround needed.",
            "budget": "500",
            "budget_type": "fixed"
        },
        {
            "main_language": "pl",
            "title_pl": "Tłumaczenie dokumentów technicznych",
            "description_pl": "Potrzebny tłumacz techniczny z doświadczeniem w IT. Około 50 stron dokumentacji.",
            "budget": "800",
            "budget_type": "hourly"
        },
        {
            "main_language": "uk",
            "title_uk": "SEO оптимізація інтернет-магазину",
            "description_uk": "Шукаємо SEO спеціаліста для просування інтернет-магазину. Досвід у e-commerce обов'язковий.",
            "budget": "2500",
            "budget_type": "monthly"
        },
        {
            "main_language": "en",
            "title_en": "Mobile App Development (iOS)",
            "description_en": "Need experienced iOS developer for fitness tracking app. Must have portfolio with similar projects.",
            "budget": "5000",
            "budget_type": "fixed"
        },
        {
            "main_language": "de",
            "title_de": "Datenbankoptimierung PostgreSQL",
            "description_de": "Suche einen Experten für PostgreSQL-Optimierung. Große Datenbank mit Performance-Problemen.",
            "budget": "1500",
            "budget_type": "fixed"
        },
        {
            "main_language": "fr",
            "title_fr": "Rédaction de contenu web",
            "description_fr": "Recherche rédacteur web expérimenté pour créer du contenu SEO. 20 articles par mois.",
            "budget": "1200",
            "budget_type": "monthly"
        },
        {
            "main_language": "uk",
            "title_uk": "Налаштування серверу Linux",
            "description_uk": "Потрібна допомога з налаштуванням VPS серверу. Ubuntu 22.04, Nginx, Docker.",
            "budget": "400",
            "budget_type": "fixed"
        },
    ]

    created_count = 0

    for i, bid_data in enumerate(test_bids_data):
        try:
            # Берем случайные связи
            user = data["users"][i % len(data["users"])]
            country = data["countries"][i % len(data["countries"])]
            city = data["cities"][i % len(data["cities"])]
            category = data["categories"][i % len(data["categories"])]
            undercategory = data["undercategories"][i % len(data["undercategories"])]

            # Создаем слаги
            main_lang = bid_data["main_language"]
            title_field = f"title_{main_lang}"
            title = bid_data.get(title_field, "Test Bid")

            # Простой slug из title
            slug_base = title.lower().replace(" ", "-")[:50]

            # Создаем бид
            bid = await Bid.create(
                main_language=bid_data["main_language"],
                title_uk=bid_data.get("title_uk"),
                title_en=bid_data.get("title_en"),
                title_pl=bid_data.get("title_pl"),
                title_fr=bid_data.get("title_fr"),
                title_de=bid_data.get("title_de"),
                description_uk=bid_data.get("description_uk"),
                description_en=bid_data.get("description_en"),
                description_pl=bid_data.get("description_pl"),
                description_fr=bid_data.get("description_fr"),
                description_de=bid_data.get("description_de"),
                **{f"slug_{main_lang}": f"{slug_base}-{i+1}"},
                categories=[category.id],
                under_categories=[undercategory.id],
                author=user,
                country=country,
                city=city,
                budget=bid_data["budget"],
                budget_type=bid_data.get("budget_type", "fixed"),
                delete_token=secrets.token_urlsafe(32),
                auto_translated_fields=[]
            )

            created_count += 1
            print(f"✅ Создан бид #{created_count}: {title} (ID: {bid.id}, язык: {main_lang})")

        except Exception as e:

    print(f"\n🎉 Создано {created_count} из {len(test_bids_data)} тестовых бидов")

    # Закрываем соединение
    await Tortoise.close_connections()


if __name__ == "__main__":
    print("🚀 Запуск скрипта добавления тестовых бидов...\n")
    asyncio.run(create_test_bids())
