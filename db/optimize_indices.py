"""
Скрипт для создания оптимизированных индексов базы данных
"""
import asyncio
from tortoise import Tortoise

async def create_performance_indices():
    """Создание индексов для оптимизации производительности"""
    
    # Подключаемся к базе данных
    from tortoise_config import TORTOISE_CONFIG
    await Tortoise.init(config=TORTOISE_CONFIG)
    
    connection = Tortoise.get_connection("default")
    
    # Индексы для таблицы заявок (bids)
    bid_indices = [
        # Индекс для быстрого поиска по тексту
        "CREATE INDEX IF NOT EXISTS idx_bid_title_search ON bid (title_uk, title_en);",
        "CREATE INDEX IF NOT EXISTS idx_bid_description_search ON bid (description_uk, description_en);",
        
        # Композитные индексы для фильтрации
        "CREATE INDEX IF NOT EXISTS idx_bid_category_country ON bid (categories, country_id);",
        "CREATE INDEX IF NOT EXISTS idx_bid_date_status ON bid (created_at DESC, status);",
        
        # Индексы для слагов
        "CREATE INDEX IF NOT EXISTS idx_bid_slugs ON bid (slug_uk, slug_en, slug_pl, slug_fr, slug_de);",
        
        # Индекс для автора
        "CREATE INDEX IF NOT EXISTS idx_bid_author ON bid (user_id);",
    ]
    
    # Индексы для таблицы компаний (companies)
    company_indices = [
        # Индекс для поиска по названию
        "CREATE INDEX IF NOT EXISTS idx_company_name_search ON companies (name, name_uk, name_en);",
        "CREATE INDEX IF NOT EXISTS idx_company_description_search ON companies (description_uk, description_en);",
        
        # Индекс для слага
        "CREATE INDEX IF NOT EXISTS idx_company_slug ON companies (slug_name);",
        
        # Композитные индексы
        "CREATE INDEX IF NOT EXISTS idx_company_location ON companies (country, city);",
        "CREATE INDEX IF NOT EXISTS idx_company_owner ON companies (owner_id);",
        
        # Индекс для категорий
        "CREATE INDEX IF NOT EXISTS idx_company_categories ON companies (categories);",
    ]
    
    # Индексы для пользователей
    user_indices = [
        # Быстрый поиск по email и никнейму
        "CREATE INDEX IF NOT EXISTS idx_user_email ON users (email);",
        "CREATE INDEX IF NOT EXISTS idx_user_nickname ON users (nickname);",
        
        # Индекс для локации
        "CREATE INDEX IF NOT EXISTS idx_user_location ON users (country_id, city_id);",
    ]
    
    # Индексы для чатов
    chat_indices = [
        # Быстрый поиск чатов пользователя
        "CREATE INDEX IF NOT EXISTS idx_chat_participants ON chats (user1_id, user2_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_updated ON chats (updated_at DESC);",
    ]
    
    # Выполняем создание всех индексов
    all_indices = bid_indices + company_indices + user_indices + chat_indices
    
    print("🚀 Создание оптимизированных индексов...")
    
    for i, query in enumerate(all_indices, 1):
        try:
            await connection.execute_query(query)
            print(f"✅ [{i}/{len(all_indices)}] Индекс создан: {query.split()[5] if len(query.split()) > 5 else 'unknown'}")
        except Exception as e:
    
    print(f"🎯 Создание индексов завершено: {len(all_indices)} индексов")
    
    # Дополнительные оптимизации SQLite
    sqlite_optimizations = [
        "PRAGMA journal_mode = WAL;",  # Write-Ahead Logging для лучшей производительности
        "PRAGMA synchronous = NORMAL;",  # Баланс между безопасностью и скоростью
        "PRAGMA cache_size = 10000;",  # Увеличиваем кеш до 10MB
        "PRAGMA temp_store = MEMORY;",  # Временные таблицы в памяти
        "PRAGMA mmap_size = 268435456;",  # Memory-mapped I/O (256MB)
    ]
    
    print("\n⚡ Применение оптимизаций SQLite...")
    for optimization in sqlite_optimizations:
        try:
            await connection.execute_query(optimization)
            print(f"✅ {optimization}")
        except Exception as e:
    
    await Tortoise.close_connections()
    print("\n🎉 Оптимизация базы данных завершена!")

if __name__ == "__main__":
    asyncio.run(create_performance_indices())
