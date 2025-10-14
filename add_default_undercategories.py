from tortoise import Tortoise, run_async
from models import Category, UnderCategory

categories_data = [
    {
        'name': 'web_development',
        'name_uk': 'Веб-розробка',
        'name_en': 'Web Development',
        'name_pl': 'Tworzenie stron WWW',
        'name_fr': 'Développement Web',
        'name_de': 'Webentwicklung',
        'undercategories': [
            {'name_uk': 'Frontend розробка', 'name_en': 'Frontend Development', 'name_pl': 'Frontend', 'name_fr': 'Développement Frontend', 'name_de': 'Frontend-Entwicklung'},
            {'name_uk': 'Backend розробка', 'name_en': 'Backend Development', 'name_pl': 'Backend', 'name_fr': 'Développement Backend', 'name_de': 'Backend-Entwicklung'},
            {'name_uk': 'Повна розробка сайту', 'name_en': 'Full-stack Development', 'name_pl': 'Full-stack', 'name_fr': 'Développement Full-stack', 'name_de': 'Full-Stack-Entwicklung'}
        ]
    },
    {
        'name': 'mobile_development',
        'name_uk': 'Мобільна розробка',
        'name_en': 'Mobile Development',
        'name_pl': 'Tworzenie aplikacji mobilnych',
        'name_fr': 'Développement Mobile',
        'name_de': 'Mobile Entwicklung',
        'undercategories': [
            {'name_uk': 'iOS додатки', 'name_en': 'iOS Apps', 'name_pl': 'Aplikacje iOS', 'name_fr': 'Applications iOS', 'name_de': 'iOS Apps'},
            {'name_uk': 'Android додатки', 'name_en': 'Android Apps', 'name_pl': 'Aplikacje Android', 'name_fr': 'Applications Android', 'name_de': 'Android Apps'},
            {'name_uk': 'Кросплатформені додатки', 'name_en': 'Cross-platform Apps', 'name_pl': 'Aplikacje cross-platform', 'name_fr': 'Applications multiplateformes', 'name_de': 'Cross-Plattform-Apps'}
        ]
    },
    {
        'name': 'graphic_design',
        'name_uk': 'Графічний дизайн',
        'name_en': 'Graphic Design',
        'name_pl': 'Projektowanie graficzne',
        'name_fr': 'Design Graphique',
        'name_de': 'Grafikdesign',
        'undercategories': [
            {'name_uk': 'Логотипи та брендинг', 'name_en': 'Logos & Branding', 'name_pl': 'Logotypy i branding', 'name_fr': 'Logos et Branding', 'name_de': 'Logos & Branding'},
            {'name_uk': 'Ілюстрації', 'name_en': 'Illustrations', 'name_pl': 'Ilustracje', 'name_fr': 'Illustrations', 'name_de': 'Illustrationen'},
            {'name_uk': 'Дизайн соцмереж', 'name_en': 'Social Media Design', 'name_pl': 'Projektowanie social media', 'name_fr': 'Design des réseaux sociaux', 'name_de': 'Social Media Design'}
        ]
    },
    {
        'name': 'digital_marketing',
        'name_uk': 'Цифровий маркетинг',
        'name_en': 'Digital Marketing',
        'name_pl': 'Marketing cyfrowy',
        'name_fr': 'Marketing Numérique',
        'name_de': 'Digital Marketing',
        'undercategories': [
            {'name_uk': 'SEO оптимізація', 'name_en': 'SEO', 'name_pl': 'SEO', 'name_fr': 'SEO', 'name_de': 'SEO'},
            {'name_uk': 'SMM', 'name_en': 'Social Media Marketing', 'name_pl': 'Marketing w social media', 'name_fr': 'Marketing des réseaux sociaux', 'name_de': 'Social Media Marketing'},
            {'name_uk': 'Email маркетинг', 'name_en': 'Email Marketing', 'name_pl': 'Email marketing', 'name_fr': 'Marketing par email', 'name_de': 'E-Mail Marketing'}
        ]
    },
    {
        'name': 'writing',
        'name_uk': 'Написання текстів',
        'name_en': 'Writing',
        'name_pl': 'Pisanie tekstów',
        'name_fr': 'Rédaction',
        'name_de': 'Schreiben',
        'undercategories': [
            {'name_uk': 'Статті та блоги', 'name_en': 'Articles & Blogs', 'name_pl': 'Artykuły i blogi', 'name_fr': 'Articles & Blogs', 'name_de': 'Artikel & Blogs'},
            {'name_uk': 'Копірайтинг', 'name_en': 'Copywriting', 'name_pl': 'Copywriting', 'name_fr': 'Rédaction publicitaire', 'name_de': 'Werbetexten'},
            {'name_uk': 'Технічна документація', 'name_en': 'Technical Writing', 'name_pl': 'Dokumentacja techniczna', 'name_fr': 'Rédaction technique', 'name_de': 'Technische Dokumentation'}
        ]
    },
    {
        'name': 'translation',
        'name_uk': 'Переклади',
        'name_en': 'Translation',
        'name_pl': 'Tłumaczenia',
        'name_fr': 'Traduction',
        'name_de': 'Übersetzung',
        'undercategories': [
            {'name_uk': 'Технічний переклад', 'name_en': 'Technical Translation', 'name_pl': 'Tłumaczenia techniczne', 'name_fr': 'Traduction technique', 'name_de': 'Technische Übersetzung'},
            {'name_uk': 'Літературний переклад', 'name_en': 'Literary Translation', 'name_pl': 'Tłumaczenia literackie', 'name_fr': 'Traduction littéraire', 'name_de': 'Literarische Übersetzung'},
            {'name_uk': 'Сайт та додатки', 'name_en': 'Website & App Translation', 'name_pl': 'Tłumaczenia stron i aplikacji', 'name_fr': 'Traduction de sites et apps', 'name_de': 'Website & App Übersetzung'}
        ]
    },
    {
        'name': 'video_editing',
        'name_uk': 'Відеомонтаж',
        'name_en': 'Video Editing',
        'name_pl': 'Montaż wideo',
        'name_fr': 'Montage Vidéo',
        'name_de': 'Videobearbeitung',
        'undercategories': [
            {'name_uk': 'Реклама та промо', 'name_en': 'Ads & Promo', 'name_pl': 'Reklamy i promo', 'name_fr': 'Publicités & Promo', 'name_de': 'Werbung & Promo'},
            {'name_uk': 'Монтаж YouTube', 'name_en': 'YouTube Editing', 'name_pl': 'Montaż YouTube', 'name_fr': 'Montage YouTube', 'name_de': 'YouTube-Bearbeitung'},
            {'name_uk': 'Анімація', 'name_en': 'Animation', 'name_pl': 'Animacja', 'name_fr': 'Animation', 'name_de': 'Animation'}
        ]
    },
    {
        'name': 'seo',
        'name_uk': 'SEO',
        'name_en': 'SEO',
        'name_pl': 'SEO',
        'name_fr': 'SEO',
        'name_de': 'SEO',
        'undercategories': [
            {'name_uk': 'Оптимізація сайтів', 'name_en': 'Website Optimization', 'name_pl': 'Optymalizacja stron', 'name_fr': 'Optimisation de sites web', 'name_de': 'Website-Optimierung'},
            {'name_uk': 'Лінкбілдінг', 'name_en': 'Link Building', 'name_pl': 'Link building', 'name_fr': 'Link Building', 'name_de': 'Linkbuilding'},
            {'name_uk': 'Контент стратегія', 'name_en': 'Content Strategy', 'name_pl': 'Strategia treści', 'name_fr': 'Stratégie de contenu', 'name_de': 'Content-Strategie'}
        ]
    },
    {
        'name': 'virtual_assistant',
        'name_uk': 'Віртуальний асистент',
        'name_en': 'Virtual Assistant',
        'name_pl': 'Wirtualny Asystent',
        'name_fr': 'Assistant Virtuel',
        'name_de': 'Virtueller Assistent',
        'undercategories': [
            {'name_uk': 'Адміністративна підтримка', 'name_en': 'Administrative Support', 'name_pl': 'Wsparcie administracyjne', 'name_fr': 'Support administratif', 'name_de': 'Administrative Unterstützung'},
            {'name_uk': 'Обробка електронної пошти', 'name_en': 'Email Handling', 'name_pl': 'Obsługa e-maili', 'name_fr': 'Gestion des e-mails', 'name_de': 'E-Mail-Verwaltung'},
            {'name_uk': 'Управління календарем', 'name_en': 'Calendar Management', 'name_pl': 'Zarządzanie kalendarzem', 'name_fr': 'Gestion du calendrier', 'name_de': 'Kalenderverwaltung'}
        ]
    },
    {
        'name': 'ui_ux_design',
        'name_uk': 'UI/UX дизайн',
        'name_en': 'UI/UX Design',
        'name_pl': 'Projektowanie UI/UX',
        'name_fr': 'Design UI/UX',
        'name_de': 'UI/UX-Design',
        'undercategories': [
            {'name_uk': 'UI дизайн', 'name_en': 'UI Design', 'name_pl': 'Projektowanie UI', 'name_fr': 'Design UI', 'name_de': 'UI Design'},
            {'name_uk': 'UX дослідження', 'name_en': 'UX Research', 'name_pl': 'Badania UX', 'name_fr': 'Recherche UX', 'name_de': 'UX-Forschung'},
            {'name_uk': 'Прототипування', 'name_en': 'Prototyping', 'name_pl': 'Prototypowanie', 'name_fr': 'Prototypage', 'name_de': 'Prototyping'}
        ]
    },
]


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

    # Очистка старых данных
    deleted_uc = await UnderCategory.all().delete()
    deleted_c = await Category.all().delete()
    print(f"🗑 Удалено {deleted_c} категорий и {deleted_uc} подкатегорий")

    # Добавление новых категорий и подкатегорий с полными переводами
    for cat_data in categories_data:
        category, _ = await Category.get_or_create(
            name=cat_data['name'],
            defaults={
                'name_uk': cat_data['name_uk'],
                'name_en': cat_data['name_en'],
                'name_pl': cat_data['name_pl'],
                'name_fr': cat_data['name_fr'],
                'name_de': cat_data['name_de'],
            }
        )
        print(f"✅ Добавлена категория: {category.name_en}")

        for uc in cat_data['undercategories']:
            undercategory, _ = await UnderCategory.get_or_create(
                full_category=category,
                name_uk=uc['name_uk'],
                name_en=uc['name_en'],
                name_pl=uc['name_pl'],
                name_fr=uc['name_fr'],
                name_de=uc['name_de'],
            )
            print(f"   ➕ Подкатегория: {undercategory.name_en}")

    print("🎉 Все категории и подкатегории успешно добавлены!")
    await Tortoise.close_connections()

if __name__ == '__main__':
    run_async(init())
