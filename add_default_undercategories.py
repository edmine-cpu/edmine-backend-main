from tortoise import Tortoise, run_async
from models import Category, UnderCategory

async def init_undercategories():
    await Tortoise.init(
        db_url='postgres://postgres:Ns290872erh@localhost:5432/makeasap',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

    await UnderCategory.all().delete()  # Очистка старых

    categories = await Category.all()

    for category in categories:
        for i in range(1, 4):
            print(i)
            await Tortoise.generate_schemas()
            await UnderCategory.get_or_create(
                full_category=category,
                name_uk=f"{category.name_uk} підкатегорія {i}",
                name_en=f"{category.name_en} subcategory {i}",
                name_pl=f"{category.name_pl} podkategoria {i}"
            )

    print("✅ Підкатегорії з перекладом додано.")
    await Tortoise.close_connections()

if __name__ == '__main__':
    run_async(init_undercategories())
