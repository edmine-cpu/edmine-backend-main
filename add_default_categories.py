from tortoise import Tortoise, run_async
from models import Category
import os
from dotenv import load_dotenv

load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")


async def init():
    await Tortoise.init(
        db_url=f'postgres://postgres:{DB_PASSWORD}@localhost:5432/makeasap_dev',
        modules={'models': ['models']}
    )
    await Tortoise.generate_schemas()

    # Список категорий с переводами
    categories = [
        {'name': 'web_development', 'name_uk': 'Веб-розробка', 'name_en': 'Web Development', 'name_pl': 'Tworzenie stron WWW'},
        {'name': 'mobile_development', 'name_uk': 'Мобільна розробка', 'name_en': 'Mobile Development', 'name_pl': 'Tworzenie aplikacji mobilnych'},
        {'name': 'graphic_design', 'name_uk': 'Графічний дизайн', 'name_en': 'Graphic Design', 'name_pl': 'Projektowanie graficzne'},
        {'name': 'digital_marketing', 'name_uk': 'Цифровий маркетинг', 'name_en': 'Digital Marketing', 'name_pl': 'Marketing cyfrowy'},
        {'name': 'writing', 'name_uk': 'Написання текстів', 'name_en': 'Writing', 'name_pl': 'Pisanie tekstów'},
        {'name': 'translation', 'name_uk': 'Переклади', 'name_en': 'Translation', 'name_pl': 'Tłumaczenia'},
        {'name': 'video_editing', 'name_uk': 'Відеомонтаж', 'name_en': 'Video Editing', 'name_pl': 'Montaż wideo'},
        {'name': 'seo', 'name_uk': 'SEO', 'name_en': 'SEO', 'name_pl': 'SEO'},
        {'name': 'virtual_assistant', 'name_uk': 'Віртуальний асистент', 'name_en': 'Virtual Assistant', 'name_pl': 'Wirtualny Asystent'},
        {'name': 'ui_ux_design', 'name_uk': 'UI/UX дизайн', 'name_en': 'UI/UX Design', 'name_pl': 'Projektowanie UI/UX'},
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
