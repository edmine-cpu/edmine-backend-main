from tortoise import BaseDBAsyncClient

async def upgrade(db: BaseDBAsyncClient) -> str:
    await db.execute_script('''
        ALTER TABLE category ADD COLUMN name_uk VARCHAR(64);
        
        UPDATE category SET name_uk = 'Сантехніка' WHERE name = 'plumbing';
        UPDATE category SET name_uk = 'Електрика' WHERE name = 'electrical';
        UPDATE category SET name_uk = 'Ремонт' WHERE name = 'repair';
        UPDATE category SET name_uk = 'Прибирання' WHERE name = 'cleaning';
        UPDATE category SET name_uk = 'Інше' WHERE name = 'other';
    ''')
    return 'Added name_uk field to Category model and updated existing categories'

async def downgrade(db: BaseDBAsyncClient) -> str:
    await db.execute_script('ALTER TABLE category DROP COLUMN name_uk;')
    return 'Removed name_uk field from Category model' 