"""
Миграция для добавления многоязычных полей в таблицу компаний
"""

async def upgrade_company_table():
    """Добавляет многоязычные поля в таблицу компаний"""
    from tortoise import Tortoise
    
    connection = Tortoise.get_connection("default")
    
    # Добавляем новые поля для названий на разных языках
    await connection.execute_query("""
        ALTER TABLE company 
        ADD COLUMN name_uk VARCHAR(64),
        ADD COLUMN name_en VARCHAR(64),
        ADD COLUMN name_pl VARCHAR(64),
        ADD COLUMN name_fr VARCHAR(64),
        ADD COLUMN name_de VARCHAR(64)
    """)
    
    # Добавляем новые поля для слагов на разных языках
    await connection.execute_query("""
        ALTER TABLE company 
        ADD COLUMN slug_uk VARCHAR(128),
        ADD COLUMN slug_en VARCHAR(128),
        ADD COLUMN slug_pl VARCHAR(128),
        ADD COLUMN slug_fr VARCHAR(128),
        ADD COLUMN slug_de VARCHAR(128)
    """)
    
    # Добавляем поля для отслеживания переводов и времени
    await connection.execute_query("""
        ALTER TABLE company 
        ADD COLUMN auto_translated_fields JSON,
        ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    """)
    
    # Копируем существующие названия в поле name_uk
    await connection.execute_query("""
        UPDATE company SET name_uk = name WHERE name_uk IS NULL
    """)
    
    print("✅ Миграция таблицы компаний завершена")

if __name__ == "__main__":
    import asyncio
    from tortoise import Tortoise
    from config import TORTOISE_ORM
    
    async def run_migration():
        await Tortoise.init(config=TORTOISE_ORM)
        await upgrade_company_table()
        await Tortoise.close_connections()
        
    asyncio.run(run_migration())
