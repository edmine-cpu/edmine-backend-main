import re
import unicodedata
from typing import Dict, Optional
from deep_translator import GoogleTranslator


def transliterate_uk_to_en(text: str) -> str:
    """Транслитерация украинского текста в латиницу"""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e', 'є': 'ie',
        'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'y', 'к': 'k', 'л': 'l',
        'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ь': '',
        'ю': 'yu', 'я': 'ya', ' ': '-', "'": ''
    }
    
    result = ''
    for char in text.lower():
        result += translit_map.get(char, char)
    
    return result


def generate_slug(text: str, lang: str = 'uk', max_length: int = 100) -> str:
    """Генерирует SEO-дружественный slug из текста"""
    if not text:
        return ''
    
    # Удаляем HTML теги
    text = re.sub(r'<[^>]+>', '', text)
    
    # Приводим к нижнему регистру
    text = text.lower().strip()
    
    if lang == 'uk':
        # Для украинского - транслитерация
        slug = transliterate_uk_to_en(text)
    else:
        # Для других языков - стандартная обработка
        slug = unicodedata.normalize('NFKD', text)
        slug = slug.encode('ascii', 'ignore').decode('ascii')
    
    # Заменяем пробелы и спецсимволы на дефисы
    slug = re.sub(r'[^a-z0-9\-]', '-', slug)
    
    # Убираем множественные дефисы
    slug = re.sub(r'-+', '-', slug)
    
    # Убираем дефисы в начале и конце
    slug = slug.strip('-')
    
    # Ограничиваем длину
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug or 'untitled'


async def generate_bid_slugs(title_uk: str = '', title_en: str = '', title_pl: str = '', title_fr: str = '', title_de: str = '', bid_id: int = None) -> Dict[str, str]:
    """Генерирует slug'и для заявки на всех языках"""
    slugs = {}
    
    # Генерируем slug для каждого языка из соответствующего заголовка
    if title_uk:
        slugs['slug_uk'] = generate_slug(title_uk, 'uk')
    if title_en:
        slugs['slug_en'] = generate_slug(title_en, 'en')
    if title_pl:
        slugs['slug_pl'] = generate_slug(title_pl, 'pl')
    if title_fr:
        slugs['slug_fr'] = generate_slug(title_fr, 'fr')
    if title_de:
        slugs['slug_de'] = generate_slug(title_de, 'de')
    
    # Если есть ID, добавляем его в конец
    if bid_id:
        for lang in ['uk', 'en', 'pl', 'fr', 'de']:
            if f'slug_{lang}' in slugs:
                slugs[f'slug_{lang}'] = f"{slugs[f'slug_{lang}']}-{bid_id}"
    
    return slugs


async def generate_category_slugs(name_uk: str = '', name_en: str = '', name_pl: str = '', name_fr: str = '', name_de: str = '') -> Dict[str, str]:
    """Генерирует slug'и для категории на всех языках"""
    slugs = {}
    
    if name_uk:
        slugs['slug_uk'] = generate_slug(name_uk, 'uk')
    if name_en:
        slugs['slug_en'] = generate_slug(name_en, 'en')
    if name_pl:
        slugs['slug_pl'] = generate_slug(name_pl, 'pl')
    if name_fr:
        slugs['slug_fr'] = generate_slug(name_fr, 'fr')
    if name_de:
        slugs['slug_de'] = generate_slug(name_de, 'de')
    
    return slugs


async def generate_user_slugs(name: str, user_id: int, company_name_uk: str = '', company_name_en: str = '', company_name_pl: str = '', company_name_fr: str = '', company_name_de: str = '') -> Dict[str, str]:
    """Генерирует slug'и для пользователя/компании на всех языках"""
    slugs = {}
    
    # Используем название компании если есть, иначе имя пользователя
    base_name_uk = company_name_uk or name
    base_name_en = company_name_en or name
    base_name_pl = company_name_pl or name
    base_name_fr = company_name_fr or name
    base_name_de = company_name_de or name
    
    slugs['slug_uk'] = f"{generate_slug(base_name_uk, 'uk')}-{user_id}"
    slugs['slug_en'] = f"{generate_slug(base_name_en, 'en')}-{user_id}"
    slugs['slug_pl'] = f"{generate_slug(base_name_pl, 'pl')}-{user_id}"
    slugs['slug_fr'] = f"{generate_slug(base_name_fr, 'fr')}-{user_id}"
    slugs['slug_de'] = f"{generate_slug(base_name_de, 'de')}-{user_id}"
    
    return slugs


async def generate_company_slugs(name_uk: str = '', name_en: str = '', name_pl: str = '', name_fr: str = '', name_de: str = '', company_id: int = None) -> Dict[str, str]:
    """Генерирует slug'и для компании на всех языках"""
    slugs = {}
    
    # Генерируем slug для каждого языка из соответствующего названия
    if name_uk:
        slugs['slug_uk'] = generate_slug(name_uk, 'uk')
    if name_en:
        slugs['slug_en'] = generate_slug(name_en, 'en')
    if name_pl:
        slugs['slug_pl'] = generate_slug(name_pl, 'pl')
    if name_fr:
        slugs['slug_fr'] = generate_slug(name_fr, 'fr')
    if name_de:
        slugs['slug_de'] = generate_slug(name_de, 'de')
    
    # Если есть ID, добавляем его в конец
    if company_id:
        for lang in ['uk', 'en', 'pl', 'fr', 'de']:
            if f'slug_{lang}' in slugs:
                slugs[f'slug_{lang}'] = f"{slugs[f'slug_{lang}']}-{company_id}"
    
    return slugs 