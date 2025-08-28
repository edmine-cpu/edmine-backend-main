from tortoise import Tortoise, run_async
from models import Category

async def init():
    await Tortoise.init(
        db_url='postgres://postgres:Ns290872erh@localhost:5432/makeasap',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

    # Список категорий с переводами
    categories = [
        {'name': 'plumbing', 'name_uk': 'Сантехніка', 'name_en': 'Plumbing', 'name_pl': 'Hydraulika'},
        {'name': 'electrical', 'name_uk': 'Електрика', 'name_en': 'Electrical', 'name_pl': 'Elektryka'},
        {'name': 'repair', 'name_uk': 'Ремонт', 'name_en': 'Repair', 'name_pl': 'Naprawa'},
        {'name': 'cleaning', 'name_uk': 'Прибирання', 'name_en': 'Cleaning', 'name_pl': 'Sprzątanie'},
        {'name': 'other', 'name_uk': 'Інше', 'name_en': 'Other', 'name_pl': 'Inne'}
    ]

    await Category.all().delete()  # Очистка существующих категорий

    for cat in categories:
        await Category.get_or_create(
            name=cat['name'],
            defaults={
                'name_uk': cat['name_uk'],
                'name_en': cat['name_en'],
                'name_pl': cat['name_pl'],
            }
        )

    await Tortoise.close_connections()

if __name__ == '__main__':
    run_async(init())
