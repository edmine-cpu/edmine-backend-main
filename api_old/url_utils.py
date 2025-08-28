import re
from typing import Dict, Optional
from models.categories import Category, UnderCategory

# Маппинг URL slug'ов для категорий
CATEGORY_SLUGS = {
    'uk': {
        'plumbing': 'santekhnika',
        'electrical': 'elektrika', 
        'repair': 'remont',
        'cleaning': 'pribirannia',
        'other': 'inshe'
    },
    'en': {
        'plumbing': 'plumbing',
        'electrical': 'electrical',
        'repair': 'repair', 
        'cleaning': 'cleaning',
        'other': 'other'
    },
    'pl': {
        'plumbing': 'hydraulika',
        'electrical': 'elektryka',
        'repair': 'naprawa',
        'cleaning': 'sprzatanie', 
        'other': 'inne'
    }
}

# Обратный маппинг - из slug'а в название категории
SLUG_TO_CATEGORY = {}
for lang, categories in CATEGORY_SLUGS.items():
    SLUG_TO_CATEGORY[lang] = {slug: category for category, slug in categories.items()}


def generate_slug(text: str) -> str:
    """Генерирует URL slug из текста"""
    # Маппинг украинских символов
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie', 
        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 
        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '', 
        'ю': 'yu', 'я': 'ya'
    }
    
    text = text.lower()
    # Транслитерация
    for uk_char, en_char in translit_map.items():
        text = text.replace(uk_char, en_char)
    
    # Удаляем все кроме букв, цифр и дефисов, заменяем пробелы на дефисы
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = text.strip('-')
    
    return text


def get_category_slug(category_name: str, lang: str) -> str:
    """Получает URL slug для категории"""
    return CATEGORY_SLUGS.get(lang, {}).get(category_name, category_name)


def get_category_from_slug(slug: str, lang: str) -> Optional[str]:
    """Получает название категории из URL slug'а"""
    return SLUG_TO_CATEGORY.get(lang, {}).get(slug)


async def get_subcategory_slug(subcategory_id: int, lang: str) -> Optional[str]:
    """Генерирует slug для подкатегории"""
    try:
        subcategory = await UnderCategory.get(id=subcategory_id)
        if lang == 'uk':
            text = subcategory.name_uk
        elif lang == 'en':
            text = subcategory.name_en
        elif lang == 'pl':
            text = subcategory.name_pl
        else:
            text = subcategory.name_uk
        
        if text:
            return generate_slug(text)
        return None
    except:
        return None


async def get_subcategory_from_slug(category_name: str, slug: str, lang: str) -> Optional[int]:
    """Получает ID подкатегории из slug'а"""
    try:
        # Сначала находим категорию
        category = await Category.get(name=category_name)
        
        # Получаем все подкатегории этой категории
        subcategories = await UnderCategory.filter(full_category=category)
        
        for subcat in subcategories:
            if lang == 'uk':
                text = subcat.name_uk
            elif lang == 'en':
                text = subcat.name_en  
            elif lang == 'pl':
                text = subcat.name_pl
            else:
                text = subcat.name_uk
                
            if text and generate_slug(text) == slug:
                return subcat.id
        
        return None
    except:
        return None


def build_catalog_url(lang: str, category: Optional[str] = None, subcategory: Optional[str] = None) -> str:
    """Строит URL каталога с категорией и подкатегорией"""
    url = f"/{lang}"
    
    if category:
        category_slug = get_category_slug(category, lang)
        url += f"/{category_slug}"
        
        if subcategory:
            url += f"/{subcategory}"
    else:
        url += "/catalog"
    
    return url


def parse_catalog_url(path: str) -> Dict[str, Optional[str]]:
    """Парсит URL каталога и извлекает язык, категорию и подкатегорию"""
    parts = [p for p in path.split('/') if p]
    
    result = {
        'lang': None,
        'category': None,
        'subcategory': None
    }
    
    if len(parts) >= 1:
        result['lang'] = parts[0]
    
    if len(parts) >= 2 and parts[1] != 'catalog':
        # Пытаемся найти категорию по slug'у
        category = get_category_from_slug(parts[1], result['lang'])
        if category:
            result['category'] = category
            
            if len(parts) >= 3:
                result['subcategory'] = parts[2]
    
    return result 