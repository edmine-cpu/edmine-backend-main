from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    await db.execute_script('''
        ALTER TABLE category DROP COLUMN IF EXISTS name_ru;
        
        UPDATE category SET name_uk = 'Сантехніка' WHERE name = 'plumbing';
        UPDATE category SET name_uk = 'Електрика' WHERE name = 'electrical';
        UPDATE category SET name_uk = 'Ремонт' WHERE name = 'repair';
        UPDATE category SET name_uk = 'Прибирання' WHERE name = 'cleaning';
        UPDATE category SET name_uk = 'Інше' WHERE name = 'other';
        
        ALTER TABLE category ALTER COLUMN name_uk SET NOT NULL;
    ''')
    return 'Updated categories to Ukrainian and removed Russian language'

async def downgrade(db: BaseDBAsyncClient) -> str:
    await db.execute_script('''
        ALTER TABLE category ADD COLUMN name_ru VARCHAR(64);
        ALTER TABLE category ALTER COLUMN name_uk DROP NOT NULL;
    ''')
    return 'Restored Russian language support' 