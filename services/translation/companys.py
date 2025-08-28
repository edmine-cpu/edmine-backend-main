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
    return 'uk'  # дефолт

async def auto_translate_descriptions(
    description_uk: Optional[str] = None,
    description_en: Optional[str] = None,
    description_pl: Optional[str] = None,
    description_fr: Optional[str] = None,
    description_de: Optional[str] = None
) -> Dict[str, Optional[str]]:

    result = {
        'description_uk': description_uk,
        'description_en': description_en,
        'description_pl': description_pl,
        'description_fr': description_fr,
        'description_de': description_de,
        'auto_translated_fields': []
    }

    primary_lang = detect_primary_language_description(
        description_uk, description_en, description_pl, description_fr, description_de
    )
    primary_text = result[f'description_{primary_lang}']

    if not primary_text or not primary_text.strip():
        return result  # нечего переводить

    for lang in SUPPORTED_LANGUAGES:
        if lang != primary_lang:
            field_name = f'description_{lang}'
            if not result[field_name] or not result[field_name].strip():
                try:
                    translator = GoogleTranslator(source=LANGUAGE_MAPPING[primary_lang], target=LANGUAGE_MAPPING[lang])
                    translated = translator.translate(primary_text)
                    result[field_name] = translated
                    result['auto_translated_fields'].append(field_name)
                    logger.info(f"Translated description from {primary_lang} to {lang}")
                except Exception as e:
                    logger.error(f"Translation failed from {primary_lang} to {lang}: {e}")

    return result
