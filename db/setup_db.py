import asyncio
from tortoise import Tortoise

async def setup_db():
    await Tortoise.init(
        db_url='postgres://postgres:WordPass_!forPostgres_%40@localhost:5432/makeasap',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()
    await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(setup_db())
