from deep_translator import GoogleTranslator
from typing import Dict, Optional
import logging
import asyncio

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

async def translate_text_batch(texts_to_translate: list) -> Dict[str, str]:
    """
    Асинхронный перевод нескольких текстов одновременно
    """
    async def translate_single(text_info):
        try:
            source_lang = text_info['source_lang']
            target_lang = text_info['target_lang']
            text = text_info['text']
            field_name = text_info['field_name']
            
            if not text or not text.strip() or source_lang == target_lang:
                return field_name, text
            
            source_code = LANGUAGE_MAPPING.get(source_lang, source_lang)
            target_code = LANGUAGE_MAPPING.get(target_lang, target_lang)
            
            translator = GoogleTranslator(source=source_code, target=target_code)
            result = translator.translate(text)
            
            logger.info(f"Translated {field_name} from {source_lang} to {target_lang}")
            return field_name, result
            
        except Exception as e:
            logger.error(f"Translation failed for {text_info['field_name']}: {e}")
            return text_info['field_name'], text_info['text']

    # Создаем задачи для всех переводов
    tasks = []
    for text_info in texts_to_translate:
        task = asyncio.create_task(translate_single(text_info))
        tasks.append(task)
    
    # Выполняем все переводы параллельно
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Формируем результат
    translation_dict = {}
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Translation task failed: {result}")
            continue
        field_name, translated_text = result
        translation_dict[field_name] = translated_text
    
    return translation_dict

async def translate_text_batch_with_semaphore(texts_to_translate: list, max_concurrent: int = 5) -> Dict[str, str]:
    """
    Асинхронный перевод нескольких текстов с ограничением одновременных запросов
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def translate_single(text_info):
        async with semaphore:
            try:
                source_lang = text_info['source_lang']
                target_lang = text_info['target_lang']
                text = text_info['text']
                field_name = text_info['field_name']
                
                if not text or not text.strip() or source_lang == target_lang:
                    return field_name, text
                
                source_code = LANGUAGE_MAPPING.get(source_lang, source_lang)
                target_code = LANGUAGE_MAPPING.get(target_lang, target_lang)
                
                translator = GoogleTranslator(source=source_code, target=target_code)
                result = translator.translate(text)
                
                logger.info(f"Translated {field_name} from {source_lang} to {target_lang}")
                return field_name, result
                
            except Exception as e:
                logger.error(f"Translation failed for {text_info['field_name']}: {e}")
                return text_info['field_name'], text_info['text']

    # Создаем задачи для всех переводов
    tasks = []
    for text_info in texts_to_translate:
        task = asyncio.create_task(translate_single(text_info))
        tasks.append(task)
    
    # Выполняем все переводы параллельно с ограничением
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Формируем результат
    translation_dict = {}
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Translation task failed: {result}")
            continue
        field_name, translated_text = result
        translation_dict[field_name] = translated_text
    
    return translation_dict

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
    
    texts_to_translate = []
    
    if primary_title and primary_title.strip():
        for lang in SUPPORTED_LANGUAGES:
            if lang != primary_lang:
                field_name = f'title_{lang}'
                if not result[field_name] or not result[field_name].strip():
                    texts_to_translate.append({
                        'field_name': field_name,
                        'text': primary_title,
                        'source_lang': primary_lang,
                        'target_lang': lang
                    })
    
    if primary_description and primary_description.strip():
        for lang in SUPPORTED_LANGUAGES:
            if lang != primary_lang:
                field_name = f'description_{lang}'
                if not result[field_name] or not result[field_name].strip():
                    texts_to_translate.append({
                        'field_name': field_name,
                        'text': primary_description,
                        'source_lang': primary_lang,
                        'target_lang': lang
                    })
    
    # Выполняем все переводы параллельно с ограничением одновременных запросов
    if texts_to_translate:
        translation_results = await translate_text_batch_with_semaphore(texts_to_translate, max_concurrent=3)
        
        for field_name, translated_text in translation_results.items():
            if translated_text and translated_text.strip():
                result[field_name] = translated_text
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
    
    texts_to_translate = []
    
    if primary_lang_name:
        primary_name = result[f'company_name_{primary_lang_name}']
        if primary_name and primary_name.strip():
            for lang in SUPPORTED_LANGUAGES:
                if lang != primary_lang_name:
                    field_name = f'company_name_{lang}'
                    if not result[field_name] or not result[field_name].strip():
                        texts_to_translate.append({
                            'field_name': field_name,
                            'text': primary_name,
                            'source_lang': primary_lang_name,
                            'target_lang': lang
                        })
    
    if primary_lang_desc:
        primary_desc = result[f'company_description_{primary_lang_desc}']
        if primary_desc and primary_desc.strip():
            for lang in SUPPORTED_LANGUAGES:
                if lang != primary_lang_desc:
                    field_name = f'company_description_{lang}'
                    if not result[field_name] or not result[field_name].strip():
                        texts_to_translate.append({
                            'field_name': field_name,
                            'text': primary_desc,
                            'source_lang': primary_lang_desc,
                            'target_lang': lang
                        })
    
    # Выполняем все переводы параллельно с ограничением одновременных запросов
    if texts_to_translate:
        translation_results = await translate_text_batch_with_semaphore(texts_to_translate, max_concurrent=3)
        
        for field_name, translated_text in translation_results.items():
            if translated_text and translated_text.strip():
                result[field_name] = translated_text
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