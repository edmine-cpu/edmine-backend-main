"""
Скрипт для мониторинга производительности базы данных
"""
import asyncio
import time
from tortoise import Tortoise

async def performance_benchmark():
    """Бенчмарк производительности основных операций"""
    
    from tortoise_config import TORTOISE_CONFIG
    await Tortoise.init(config=TORTOISE_CONFIG)
    
    connection = Tortoise.get_connection("default")
    
    print("🔍 Анализ производительности базы данных")
    print("=" * 50)
    
    # Тест 1: Анализ количества записей
    start_time = time.time()
    
    queries = [
        ("Заявки", "SELECT COUNT(*) FROM bid"),
        ("Компании", "SELECT COUNT(*) FROM companies"),
        ("Пользователи", "SELECT COUNT(*) FROM users"),
        ("Чаты", "SELECT COUNT(*) FROM chats"),
    ]
    
    for name, query in queries:
        try:
            result = await connection.execute_query_dict(query)
            count = list(result[0].values())[0] if result else 0
            print(f"📊 {name}: {count:,} записей")
        except Exception as e:
            print(f"❌ Ошибка подсчета {name}: {e}")
    
    analysis_time = time.time() - start_time
    print(f"⏱️  Анализ выполнен за: {analysis_time:.3f}s")
    print()
    
    # Тест 2: Производительность поиска заявок
    print("🔍 Тест производительности поиска заявок")
    
    search_tests = [
        ("Поиск без индексов", "SELECT * FROM bid WHERE title_uk LIKE '%веб%' LIMIT 10"),
        ("Поиск по ID", "SELECT * FROM bid WHERE id < 100 LIMIT 10"),
        ("Поиск по дате", "SELECT * FROM bid WHERE created_at > datetime('now', '-30 days') LIMIT 10"),
        ("Поиск по автору", "SELECT * FROM bid WHERE user_id = 1 LIMIT 10"),
    ]
    
    for test_name, query in search_tests:
        start_time = time.time()
        try:
            result = await connection.execute_query_dict(query)
            query_time = time.time() - start_time
            count = len(result) if result else 0
            print(f"⚡ {test_name}: {query_time:.3f}s ({count} результатов)")
        except Exception as e:
            print(f"❌ {test_name}: Ошибка - {e}")
    
    print()
    
    # Тест 3: Производительность поиска компаний
    print("🔍 Тест производительности поиска компаний")
    
    company_tests = [
        ("Поиск по названию", "SELECT * FROM companies WHERE name LIKE '%тест%' LIMIT 10"),
        ("Поиск по ID", "SELECT * FROM companies WHERE id < 50 LIMIT 10"),
        ("Поиск по слагу", "SELECT * FROM companies WHERE slug_name LIKE 'test%' LIMIT 10"),
        ("Поиск по владельцу", "SELECT * FROM companies WHERE owner_id = 1 LIMIT 10"),
    ]
    
    for test_name, query in company_tests:
        start_time = time.time()
        try:
            result = await connection.execute_query_dict(query)
            query_time = time.time() - start_time
            count = len(result) if result else 0
            print(f"⚡ {test_name}: {query_time:.3f}s ({count} результатов)")
        except Exception as e:
            print(f"❌ {test_name}: Ошибка - {e}")
    
    print()
    
    # Тест 4: Анализ индексов
    print("📈 Анализ индексов")
    try:
        indices_result = await connection.execute_query_dict(
            "SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        print(f"✅ Активных индексов: {len(indices_result)}")
        for idx in indices_result[:5]:  # Показываем первые 5
            print(f"   📍 {idx['name']}")
        if len(indices_result) > 5:
            print(f"   ... и еще {len(indices_result) - 5}")
    except Exception as e:
        print(f"❌ Ошибка анализа индексов: {e}")
    
    print()
    
    # Тест 5: Размер базы данных
    print("💾 Анализ размера базы данных")
    try:
        # Получаем размер файла базы данных
        import os
        db_path = "db/database.db"  # Путь к файлу БД
        if os.path.exists(db_path):
            size_bytes = os.path.getsize(db_path)
            size_mb = size_bytes / (1024 * 1024)
            print(f"📁 Размер файла БД: {size_mb:.2f} MB ({size_bytes:,} байт)")
        else:
            print("📁 Файл базы данных не найден")
            
        # Анализ размера таблиц (приблизительный)
        table_analysis = await connection.execute_query_dict("""
            SELECT 
                name,
                (SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=m.name) as index_count
            FROM sqlite_master m 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        print("📊 Анализ таблиц:")
        for table in table_analysis:
            print(f"   🗂️  {table['name']}: {table['index_count']} индексов")
            
    except Exception as e:
        print(f"❌ Ошибка анализа размера: {e}")
    
    print()
    
    # Рекомендации по оптимизации
    print("💡 Рекомендации по оптимизации:")
    print("   1. Регулярно запускайте VACUUM для сжатия базы данных")
    print("   2. Используйте EXPLAIN QUERY PLAN для анализа медленных запросов")
    print("   3. Рассмотрите партиционирование для больших таблиц")
    print("   4. Мониторьте индексы - удаляйте неиспользуемые")
    print("   5. Используйте пагинацию для больших результатов")
    
    await Tortoise.close_connections()
    print("\n✅ Анализ производительности завершен!")

if __name__ == "__main__":
    asyncio.run(performance_benchmark())
