from deep_translator import GoogleTranslator
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

LANGUAGE_MAPPING = {
    'uk': 'uk', 
    'en': 'en',    
    'pl': 'pl',  
    'fr': 'fr',  
    'de': 'de'   
}

SUPPORTED_LANGUAGES = ['uk', 'en', 'pl', 'fr', 'de']

def detect_primary_language(title_uk: str = None, title_en: str = None, title_pl: str = None, title_fr: str = None, title_de: str = None,
                          description_uk: str = None, description_en: str = None, description_pl: str = None, description_fr: str = None, description_de: str = None) -> str:
    if title_uk and title_uk.strip():
        return 'uk'
    elif title_en and title_en.strip():
        return 'en'
    elif title_pl and title_pl.strip():
        return 'pl'
    elif title_fr and title_fr.strip():
        return 'fr'
    elif title_de and title_de.strip():
        return 'de'
    
    if description_uk and description_uk.strip():
        return 'uk'
    elif description_en and description_en.strip():
        return 'en'
    elif description_pl and description_pl.strip():
        return 'pl'
    elif description_fr and description_fr.strip():
        return 'fr'
    elif description_de and description_de.strip():
        return 'de'
    
    return 'uk'

async def translate_text(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    if not text or not text.strip():
        return None
    
    if source_lang == target_lang:
        return text
    
    try:
        source_code = LANGUAGE_MAPPING.get(source_lang, source_lang)
        target_code = LANGUAGE_MAPPING.get(target_lang, target_lang)
        
        translator = GoogleTranslator(source=source_code, target=target_code)
        result = translator.translate(text)
        
        logger.info(f"Translated text from {source_lang} to {target_lang}")
        return result
        
    except Exception as e:
        logger.error(f"Translation failed from {source_lang} to {target_lang}: {e}")
        return None

async def auto_translate_bid_fields(title_uk: str = None, title_en: str = None, title_pl: str = None, title_fr: str = None, title_de: str = None,
                                  description_uk: str = None, description_en: str = None, description_pl: str = None, description_fr: str = None, description_de: str = None) -> Dict[str, str]:
    result = {
        'title_uk': title_uk,
        'title_en': title_en, 
        'title_pl': title_pl,
        'title_fr': title_fr,
        'title_de': title_de,
        'description_uk': description_uk,
        'description_en': description_en,
        'description_pl': description_pl,
        'description_fr': description_fr,
        'description_de': description_de,
        'auto_translated_fields': []  
    }
    
    primary_lang = detect_primary_language(title_uk, title_en, title_pl, title_fr, title_de, description_uk, description_en, description_pl, description_fr, description_de)
    
    primary_title = result[f'title_{primary_lang}']
    primary_description = result[f'description_{primary_lang}']
    
    if primary_title and primary_title.strip():
        for lang in SUPPORTED_LANGUAGES:
            if lang != primary_lang:
                field_name = f'title_{lang}'
                if not result[field_name] or not result[field_name].strip():
                    translated = await translate_text(primary_title, primary_lang, lang)
                    if translated:
                        result[field_name] = translated
                        result['auto_translated_fields'].append(field_name)
    
    if primary_description and primary_description.strip():
        for lang in SUPPORTED_LANGUAGES:
            if lang != primary_lang:
                field_name = f'description_{lang}'
                if not result[field_name] or not result[field_name].strip():
                    translated = await translate_text(primary_description, primary_lang, lang)
                    if translated:
                        result[field_name] = translated
                        result['auto_translated_fields'].append(field_name)
    
    return result

async def auto_translate_company_fields(name_uk: str = None, name_en: str = None, name_pl: str = None, name_fr: str = None, name_de: str = None,
                                       description_uk: str = None, description_en: str = None, description_pl: str = None, description_fr: str = None, description_de: str = None) -> Dict[str, str]:
    result = {
        'company_name_uk': name_uk,
        'company_name_en': name_en, 
        'company_name_pl': name_pl,
        'company_name_fr': name_fr,
        'company_name_de': name_de,
        'company_description_uk': description_uk,
        'company_description_en': description_en,
        'company_description_pl': description_pl,
        'company_description_fr': description_fr,
        'company_description_de': description_de,
        'auto_translated_fields': []  
    }
    
    primary_lang_name = detect_primary_language(name_uk, name_en, name_pl, name_fr, name_de)
    primary_lang_desc = detect_primary_language(description_uk, description_en, description_pl, description_fr, description_de)
    
    if primary_lang_name:
        primary_name = result[f'company_name_{primary_lang_name}']
        if primary_name and primary_name.strip():
            for lang in SUPPORTED_LANGUAGES:
                if lang != primary_lang_name:
                    field_name = f'company_name_{lang}'
                    if not result[field_name] or not result[field_name].strip():
                        translated = await translate_text(primary_name, primary_lang_name, lang)
                        if translated:
                            result[field_name] = translated
                            result['auto_translated_fields'].append(field_name)
    
    if primary_lang_desc:
        primary_desc = result[f'company_description_{primary_lang_desc}']
        if primary_desc and primary_desc.strip():
            for lang in SUPPORTED_LANGUAGES:
                if lang != primary_lang_desc:
                    field_name = f'company_description_{lang}'
                    if not result[field_name] or not result[field_name].strip():
                        translated = await translate_text(primary_desc, primary_lang_desc, lang)
                        if translated:
                            result[field_name] = translated
                            result['auto_translated_fields'].append(field_name)
    
    return result

def is_field_auto_translated(field_name: str, auto_translated_fields: list) -> bool:
    return field_name in auto_translated_fields

def get_translation_marker(lang: str) -> str:
    markers = {
        'uk': '(перекладено)',
        'en': '(translated)', 
        'pl': '(przetłumaczone)'
    }
    return markers.get(lang, '(translated)') 