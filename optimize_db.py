#!/usr/bin/env python3
"""
Быстрый скрипт для оптимизации базы данных
Запуск: python optimize_db.py
"""
import asyncio
import os
import sys

# Добавляем корневую папку в PATH для импортов
sys.path.insert(0, os.path.dirname(__file__))

async def main():
    """Главная функция оптимизации"""
    
    print("🚀 Запуск оптимизации базы данных EdMine")
    print("=" * 50)
    
    try:
        # Запускаем создание индексов
        print("📈 Этап 1: Создание оптимизированных индексов...")
        from db.optimize_indices import create_performance_indices
        await create_performance_indices()
        
        print("\n" + "=" * 50)
        
        # Запускаем анализ производительности
        print("🔍 Этап 2: Анализ производительности...")
        from db.performance_monitor import performance_benchmark
        await performance_benchmark()
        
        print("\n" + "=" * 50)
        print("🎉 Оптимизация завершена успешно!")
        print("\n💡 Следующие шаги:")
        print("   1. Перезапустите сервер для применения оптимизаций")
        print("   2. Мониторьте производительность в течение недели")
        print("   3. При необходимости запустите VACUUM для сжатия БД")
        
    except Exception as e:
        print(f"❌ Ошибка оптимизации: {e}")
        print("🔧 Убедитесь что:")
        print("   - База данных доступна")
        print("   - Нет активных подключений")
        print("   - Достаточно места на диске")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
