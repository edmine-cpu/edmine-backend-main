from deep_translator import GoogleTranslator
from typing import Optional, Dict
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

def detect_primary_language_description(description_uk=None, description_en=None, description_pl=None,
                                        description_fr=None, description_de=None) -> str:
    for lang, desc in [('uk', description_uk), ('en', description_en), ('pl', description_pl),
                       ('fr', description_fr), ('de', description_de)]:
        if desc and desc.strip():
            return lang
    return 'en'  

async def auto_translate_company_fields(
    name: Optional[str] = None,
    name_uk: Optional[str] = None,
    name_en: Optional[str] = None,
    name_pl: Optional[str] = None,
    name_fr: Optional[str] = None,
    name_de: Optional[str] = None,
    description_uk: Optional[str] = None,
    description_en: Optional[str] = None,
    description_pl: Optional[str] = None,
    description_fr: Optional[str] = None,
    description_de: Optional[str] = None
) -> Dict[str, Optional[str]]:

    result = {
        'name': name,
        'name_uk': name_uk or name,  
        'name_en': name_en,
        'name_pl': name_pl,
        'name_fr': name_fr,
        'name_de': name_de,
        'description_uk': description_uk,
        'description_en': description_en,
        'description_pl': description_pl,
        'description_fr': description_fr,
        'description_de': description_de,
        'auto_translated_fields': []
    }

    from .utils import translate_text_batch_with_semaphore
    texts_to_translate = []
    
    primary_name_lang = 'uk'
    primary_name = result['name_uk']
    
    if primary_name and primary_name.strip():
        for lang in SUPPORTED_LANGUAGES:
            if lang != primary_name_lang:
                field_name = f'name_{lang}'
                if not result[field_name] or not result[field_name].strip():
                    texts_to_translate.append({
                        'field_name': field_name,
                        'text': primary_name,
                        'source_lang': primary_name_lang,
                        'target_lang': lang
                    })
    
    primary_desc_lang = detect_primary_language_description(
        description_uk, description_en, description_pl, description_fr, description_de
    )
    primary_desc = result[f'description_{primary_desc_lang}']

    if primary_desc and primary_desc.strip():
        for lang in SUPPORTED_LANGUAGES:
            if lang != primary_desc_lang:
                field_name = f'description_{lang}'
                if not result[field_name] or not result[field_name].strip():
                    texts_to_translate.append({
                        'field_name': field_name,
                        'text': primary_desc,
                        'source_lang': primary_desc_lang,
                        'target_lang': lang
                    })
    
    if texts_to_translate:
        translation_results = await translate_text_batch_with_semaphore(texts_to_translate, max_concurrent=3)
        
        for field_name, translated_text in translation_results.items():
            if translated_text and translated_text.strip():
                result[field_name] = translated_text
                result['auto_translated_fields'].append(field_name)

    return result

async def auto_translate_descriptions(
    description_uk: Optional[str] = None,
    description_en: Optional[str] = None,
    description_pl: Optional[str] = None,
    description_fr: Optional[str] = None,
    description_de: Optional[str] = None
) -> Dict[str, Optional[str]]:
    return await auto_translate_company_fields(
        name=None,
        description_uk=description_uk,
        description_en=description_en,
        description_pl=description_pl,
        description_fr=description_fr,
        description_de=description_de
    )
