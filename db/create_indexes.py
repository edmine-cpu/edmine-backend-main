"""
Скрипт для создания оптимизированных индексов базы данных
Запускать после настройки основной схемы
"""

import asyncio
from tortoise import Tortoise
from config import DATABASE_URL


async def create_performance_indexes():
    """Создает индексы для улучшения производительности"""
    
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["models.user", "models.actions", "models.places", "models.categories", "models.chat"]}
    )
    
    connection = Tortoise.get_connection("default")
    
    print("🚀 Создание индексов для оптимизации производительности...")
    
    # Индексы для таблицы bids (заявки)
    bid_indexes = [
        # Основные фильтры
        "CREATE INDEX IF NOT EXISTS idx_bids_created_at ON bids (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_bids_country_id ON bids (country_id);",
        "CREATE INDEX IF NOT EXISTS idx_bids_city ON bids (city);",
        "CREATE INDEX IF NOT EXISTS idx_bids_author_id ON bids (author_id);",
        
        # JSON индексы для категорий (PostgreSQL)
        "CREATE INDEX IF NOT EXISTS idx_bids_categories ON bids USING GIN (categories);",
        "CREATE INDEX IF NOT EXISTS idx_bids_under_categories ON bids USING GIN (under_categories);",
        
        # Полнотекстовый поиск (PostgreSQL)
        "CREATE INDEX IF NOT EXISTS idx_bids_search_uk ON bids USING GIN (to_tsvector('russian', COALESCE(title_uk, '') || ' ' || COALESCE(description_uk, '')));",
        "CREATE INDEX IF NOT EXISTS idx_bids_search_en ON bids USING GIN (to_tsvector('english', COALESCE(title_en, '') || ' ' || COALESCE(description_en, '')));",
        
        # Составные индексы для популярных комбинаций фильтров
        "CREATE INDEX IF NOT EXISTS idx_bids_country_created ON bids (country_id, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_bids_city_created ON bids (city, created_at DESC);",
        
        # Индексы для текстового поиска (fallback для SQLite)
        "CREATE INDEX IF NOT EXISTS idx_bids_title_uk ON bids (title_uk);",
        "CREATE INDEX IF NOT EXISTS idx_bids_title_en ON bids (title_en);",
    ]
    
    # Индексы для таблицы companies (компании)
    company_indexes = [
        # Основные фильтры
        "CREATE INDEX IF NOT EXISTS idx_companies_name ON companies (name);",
        "CREATE INDEX IF NOT EXISTS idx_companies_country ON companies (country);",
        "CREATE INDEX IF NOT EXISTS idx_companies_city ON companies (city);",
        "CREATE INDEX IF NOT EXISTS idx_companies_owner_id ON companies (owner_id);",
        "CREATE INDEX IF NOT EXISTS idx_companies_slug_name ON companies (slug_name);",
        
        # Составные индексы
        "CREATE INDEX IF NOT EXISTS idx_companies_country_city ON companies (country, city);",
        
        # Полнотекстовый поиск
        "CREATE INDEX IF NOT EXISTS idx_companies_search ON companies USING GIN (to_tsvector('russian', COALESCE(name, '') || ' ' || COALESCE(description_uk, '')));",
    ]
    
    # Индексы для таблицы blog_articles (блог)
    blog_indexes = [
        # Основные фильтры
        "CREATE INDEX IF NOT EXISTS idx_blog_published_created ON blog_articles (is_published, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_blog_author_id ON blog_articles (author_id);",
        
        # Слаги для разных языков
        "CREATE INDEX IF NOT EXISTS idx_blog_slug_uk ON blog_articles (slug_uk);",
        "CREATE INDEX IF NOT EXISTS idx_blog_slug_en ON blog_articles (slug_en);",
        "CREATE INDEX IF NOT EXISTS idx_blog_slug_pl ON blog_articles (slug_pl);",
        
        # Поиск по заголовкам
        "CREATE INDEX IF NOT EXISTS idx_blog_title_uk ON blog_articles (title_uk);",
        "CREATE INDEX IF NOT EXISTS idx_blog_title_en ON blog_articles (title_en);",
    ]
    
    # Индексы для таблицы users (пользователи)
    user_indexes = [
        # Уникальные поля (если еще не созданы)
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users (email);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);",
        "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users (created_at);",
        "CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users (is_verified);",
    ]
    
    # Индексы для таблицы categories (категории)
    category_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories (parent_id);",
        "CREATE INDEX IF NOT EXISTS idx_categories_name_uk ON categories (name_uk);",
        "CREATE INDEX IF NOT EXISTS idx_categories_slug_uk ON categories (slug_uk);",
    ]
    
    # Индексы для таблицы countries (страны)
    country_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_countries_name_en ON countries (name_en);",
        "CREATE INDEX IF NOT EXISTS idx_countries_name_uk ON countries (name_uk);",
        "CREATE INDEX IF NOT EXISTS idx_countries_code ON countries (code);",
    ]
    
    # Индексы для таблицы cities (города)
    city_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_cities_country_id ON cities (country_id);",
        "CREATE INDEX IF NOT EXISTS idx_cities_name_en ON cities (name_en);",
        "CREATE INDEX IF NOT EXISTS idx_cities_name_uk ON cities (name_uk);",
        "CREATE INDEX IF NOT EXISTS idx_cities_country_name ON cities (country_id, name_en);",
    ]
    
    all_indexes = (
        bid_indexes + 
        company_indexes + 
        blog_indexes + 
        user_indexes + 
        category_indexes + 
        country_indexes + 
        city_indexes
    )
    
    # Создаем индексы
    success_count = 0
    error_count = 0
    
    for index_sql in all_indexes:
        try:
            await connection.execute_query(index_sql)
            index_name = index_sql.split()[5] if "IF NOT EXISTS" in index_sql else "unknown"
            print(f"✅ Создан индекс: {index_name}")
            success_count += 1
        except Exception as e:
            error_count += 1
    
    print(f"\n📊 Итоги:")
    print(f"✅ Успешно создано индексов: {success_count}")
    print(f"❌ Ошибок: {error_count}")
    
    # Дополнительные команды для PostgreSQL
    if "postgresql" in DATABASE_URL.lower():
        print("\n🐘 Выполнение команд для PostgreSQL...")
        
        postgres_commands = [
            "ANALYZE;",
            
            # Настройки для лучшей производительности поиска
            "CREATE EXTENSION IF NOT EXISTS pg_trgm;",  # Для улучшения LIKE поиска
            "CREATE EXTENSION IF NOT EXISTS btree_gin;",  # Для составных GIN индексов
        ]
        
        for cmd in postgres_commands:
            try:
                await connection.execute_query(cmd)
                print(f"✅ Выполнено: {cmd}")
            except Exception as e:
                print(f"⚠️  Предупреждение: {cmd} - {e}")
    
    await Tortoise.close_connections()
    print("\n🎉 Оптимизация базы данных завершена!")


async def analyze_table_performance():
    """Анализирует производительность запросов"""
    
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["models.user", "models.actions", "models.places", "models.categories", "models.chat"]}
    )
    
    connection = Tortoise.get_connection("default")
    
    print("📈 Анализ производительности таблиц...")
    
    # Получаем размеры таблиц
    try:
        if "postgresql" in DATABASE_URL.lower():
            size_query = """
            SELECT 
                schemaname,
                tablename,
                attname,
                n_distinct,
                correlation
            FROM pg_stats 
            WHERE schemaname = 'public' 
            AND tablename IN ('bids', 'companies', 'blog_articles', 'users');
            """
            
            stats = await connection.execute_query(size_query)
            print("📊 Статистика колонок:")
            for row in stats[1]:  # [1] содержит данные
                print(f"   {row[1]}.{row[2]}: distinct={row[3]}, correlation={row[4]}")
    
    except Exception as e:
        print(f"⚠️  Не удалось получить статистику: {e}")
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    print("🔧 Запуск оптимизации базы данных...")
    
    # Создаем индексы
    asyncio.run(create_performance_indexes())
    
    # Анализируем производительность
    asyncio.run(analyze_table_performance())
    
    print("\n💡 Рекомендации:")
    print("1. Регулярно запускайте ANALYZE для обновления статистики")
    print("2. Мониторьте медленные запросы в логах PostgreSQL")
    print("3. Рассмотрите возможность партиционирования больших таблиц")
    print("4. Настройте Redis для кэширования популярных запросов")
    print("5. Используйте CDN для статических файлов")
