from fastapi import APIRouter, Request, HTTPException, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from tortoise.exceptions import DoesNotExist
from models.actions import BlogArticle
from models.user import User
from api.slug_utils import generate_slug
from api.translation_utils import translate_text
from api.localization import get_localized_field
import re
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

SUPPORTED_LANGUAGES = ['uk', 'en', 'pl', 'fr', 'de']

def get_admin_user(request: Request):
    """Check if user is admin"""
    if not hasattr(request.state, 'user_role') or request.state.user_role != 1:
        raise HTTPException(status_code=403, detail="Access denied")
    return request.state.user_email


@router.post("/{lang}/api/translate")
async def translate_content(request: Request, lang: str):
    """Translate content from Ukrainian to other languages"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    try:
        data = await request.json()
        uk_title = data.get('title_uk', '')
        uk_content = data.get('content_uk', '')
        uk_description = data.get('description_uk', '')
        uk_keywords = data.get('keywords_uk', '')
        
        translations = {}
        
        # Translate to all supported languages except Ukrainian
        for target_lang in SUPPORTED_LANGUAGES:
            if target_lang != 'uk':
                if uk_title:
                    translations[f'title_{target_lang}'] = await translate_text(uk_title, 'uk', target_lang) or uk_title
                if uk_content:
                    translations[f'content_{target_lang}'] = await translate_text(uk_content, 'uk', target_lang) or uk_content
                if uk_description:
                    translations[f'description_{target_lang}'] = await translate_text(uk_description, 'uk', target_lang) or uk_description
                if uk_keywords:
                    translations[f'keywords_{target_lang}'] = await translate_text(uk_keywords, 'uk', target_lang) or uk_keywords
        
        return JSONResponse(content=translations)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/{lang}/admin/blog/create")
async def admin_blog_create(
    request: Request,
    lang: str,
    title_uk: str = Form(...),
    title_en: str = Form(""),
    title_pl: str = Form(""),
    title_fr: str = Form(""),
    title_de: str = Form(""),
    content_uk: str = Form(...),
    content_en: str = Form(""),
    content_pl: str = Form(""),
    content_fr: str = Form(""),
    content_de: str = Form(""),
    description_uk: str = Form(""),
    description_en: str = Form(""),
    description_pl: str = Form(""),
    description_fr: str = Form(""),
    description_de: str = Form(""),
    keywords_uk: str = Form(""),
    keywords_en: str = Form(""),
    keywords_pl: str = Form(""),
    keywords_fr: str = Form(""),
    keywords_de: str = Form(""),
    featured_image: str = Form(""),
    is_published: bool = Form(True),
    admin_user: str = Depends(get_admin_user)
):
    """Create new blog article"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    # Get author user
    author = await User.get(email=admin_user)
    
    # Auto-translate missing fields
    auto_translated = []
    translations = {
        'title': {'uk': title_uk, 'en': title_en, 'pl': title_pl, 'fr': title_fr, 'de': title_de},
        'content': {'uk': content_uk, 'en': content_en, 'pl': content_pl, 'fr': content_fr, 'de': content_de},
        'description': {'uk': description_uk, 'en': description_en, 'pl': description_pl, 'fr': description_fr, 'de': description_de},
        'keywords': {'uk': keywords_uk, 'en': keywords_en, 'pl': keywords_pl, 'fr': keywords_fr, 'de': keywords_de}
    }
    
    # Ukrainian is always the primary language
    primary_lang = 'uk'
    
    if not translations['title'][primary_lang].strip():
        raise HTTPException(status_code=400, detail="Ukrainian title is required")
    
    # Auto-translate missing fields from Ukrainian using parallel processing
    from services.translation.utils import translate_text_batch_with_semaphore
    import asyncio
    
    texts_to_translate = []
    for field_name, field_translations in translations.items():
        primary_text = field_translations[primary_lang].strip()
        if not primary_text:
            continue
            
        for target_lang in SUPPORTED_LANGUAGES:
            if target_lang != primary_lang:
                # Always translate if the field is empty or contains Ukrainian text
                current_text = field_translations[target_lang].strip()
                should_translate = (
                    not current_text or 
                    current_text == primary_text or  # If it's the same as Ukrainian
                    len(current_text) < 10  # If it's too short, probably not translated
                )
                
                if should_translate:
                    texts_to_translate.append({
                        'field_name': f'{field_name}_{target_lang}',
                        'text': primary_text,
                        'source_lang': primary_lang,
                        'target_lang': target_lang,
                        'original_field': field_name,
                        'target_lang_code': target_lang
                    })
    
    # Выполняем все переводы параллельно
    if texts_to_translate:
        try:
            translation_results = await translate_text_batch_with_semaphore(texts_to_translate, max_concurrent=5)
            
            # Обновляем результат
            for field_key, translated_text in translation_results.items():
                if translated_text and translated_text.strip():
                    # Парсим ключ для получения field_name и target_lang
                    field_name, target_lang = field_key.rsplit('_', 1)
                    translations[field_name][target_lang] = translated_text
                    auto_translated.append(field_key)
        except Exception as e:
            print(f"Batch translation error: {e}")
            # Fallback to Ukrainian text for all failed translations
            for item in texts_to_translate:
                field_name = item['original_field']
                target_lang = item['target_lang_code']
                translations[field_name][target_lang] = item['text']
                auto_translated.append(f'{field_name}_{target_lang}')
    
    # Create article
    article = await BlogArticle.create(
        title_uk=translations['title']['uk'],
        title_en=translations['title']['en'],
        title_pl=translations['title']['pl'],
        title_fr=translations['title']['fr'],
        title_de=translations['title']['de'],
        content_uk=translations['content']['uk'],
        content_en=translations['content']['en'],
        content_pl=translations['content']['pl'],
        content_fr=translations['content']['fr'],
        content_de=translations['content']['de'],
        description_uk=translations['description']['uk'],
        description_en=translations['description']['en'],
        description_pl=translations['description']['pl'],
        description_fr=translations['description']['fr'],
        description_de=translations['description']['de'],
        keywords_uk=translations['keywords']['uk'],
        keywords_en=translations['keywords']['en'],
        keywords_pl=translations['keywords']['pl'],
        keywords_fr=translations['keywords']['fr'],
        keywords_de=translations['keywords']['de'],
        featured_image=featured_image if featured_image.strip() else None,
        is_published=is_published,
        author=author,
        auto_translated_fields=auto_translated if auto_translated else None
    )
    
    # Generate slugs for all languages
    for lang_code in SUPPORTED_LANGUAGES:
        title = translations['title'][lang_code]
        if title.strip():
            slug = generate_slug(title, article.id)
            setattr(article, f'slug_{lang_code}', slug)
    
    await article.save()
    
    return RedirectResponse(url=f"/{lang}/admin/blog", status_code=302)


@router.post("/{lang}/admin/blog/{article_id}/edit")
async def admin_blog_edit(
    request: Request,
    lang: str,
    article_id: int,
    title_uk: str = Form(...),
    title_en: str = Form(""),
    title_pl: str = Form(""),
    title_fr: str = Form(""),
    title_de: str = Form(""),
    content_uk: str = Form(...),
    content_en: str = Form(""),
    content_pl: str = Form(""),
    content_fr: str = Form(""),
    content_de: str = Form(""),
    description_uk: str = Form(""),
    description_en: str = Form(""),
    description_pl: str = Form(""),
    description_fr: str = Form(""),
    description_de: str = Form(""),
    keywords_uk: str = Form(""),
    keywords_en: str = Form(""),
    keywords_pl: str = Form(""),
    keywords_fr: str = Form(""),
    keywords_de: str = Form(""),
    featured_image: str = Form(""),
    is_published: bool = Form(True),
    admin_user: str = Depends(get_admin_user)
):
    """Edit blog article"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    try:
        article = await BlogArticle.get(id=article_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Prepare translations
    translations = {
        'title': {
            'uk': title_uk.strip(),
            'en': title_en.strip(),
            'pl': title_pl.strip(),
            'fr': title_fr.strip(),
            'de': title_de.strip()
        },
        'content': {
            'uk': content_uk.strip(),
            'en': content_en.strip(),
            'pl': content_pl.strip(),
            'fr': content_fr.strip(),
            'de': content_de.strip()
        },
        'description': {
            'uk': description_uk.strip(),
            'en': description_en.strip(),
            'pl': description_pl.strip(),
            'fr': description_fr.strip(),
            'de': description_de.strip()
        },
        'keywords': {
            'uk': keywords_uk.strip(),
            'en': keywords_en.strip(),
            'pl': keywords_pl.strip(),
            'fr': keywords_fr.strip(),
            'de': keywords_de.strip()
        }
    }
    
    # Find the primary language (Ukrainian is always primary)
    primary_lang = 'uk'
    
    if not translations['title'][primary_lang]:
        raise HTTPException(status_code=400, detail="Ukrainian title is required")
    
    # Auto-translate missing fields from Ukrainian
    auto_translated = []
    for field_name, field_translations in translations.items():
        primary_text = field_translations[primary_lang].strip()
        if not primary_text:
            continue
            
        for target_lang in SUPPORTED_LANGUAGES:
            if target_lang != primary_lang:
                # Always translate if the field is empty or contains Ukrainian text
                current_text = field_translations[target_lang].strip()
                should_translate = (
                    not current_text or 
                    current_text == primary_text or  # If it's the same as Ukrainian
                    len(current_text) < 10  # If it's too short, probably not translated
                )
                
                if should_translate:
                    try:
                        translated = await translate_text(primary_text, primary_lang, target_lang)
                        field_translations[target_lang] = translated
                        auto_translated.append(f'{field_name}_{target_lang}')
                    except Exception as e:
                        print(f"Translation error for {field_name}_{target_lang}: {e}")
                        # Fallback to Ukrainian text if translation fails
                        field_translations[target_lang] = primary_text
                        auto_translated.append(f'{field_name}_{target_lang}')
    
    # Update article
    article.title_uk = translations['title']['uk']
    article.title_en = translations['title']['en']
    article.title_pl = translations['title']['pl']
    article.title_fr = translations['title']['fr']
    article.title_de = translations['title']['de']
    article.content_uk = translations['content']['uk']
    article.content_en = translations['content']['en']
    article.content_pl = translations['content']['pl']
    article.content_fr = translations['content']['fr']
    article.content_de = translations['content']['de']
    article.description_uk = translations['description']['uk']
    article.description_en = translations['description']['en']
    article.description_pl = translations['description']['pl']
    article.description_fr = translations['description']['fr']
    article.description_de = translations['description']['de']
    article.keywords_uk = translations['keywords']['uk']
    article.keywords_en = translations['keywords']['en']
    article.keywords_pl = translations['keywords']['pl']
    article.keywords_fr = translations['keywords']['fr']
    article.keywords_de = translations['keywords']['de']
    article.featured_image = featured_image if featured_image.strip() else None
    article.is_published = is_published
    
    # Update auto_translated_fields
    if auto_translated:
        article.auto_translated_fields = auto_translated
    
    # Generate new slugs for all languages
    for lang_code in SUPPORTED_LANGUAGES:
        title = translations['title'][lang_code]
        if title.strip():
            slug = generate_slug(title, article.id)
            setattr(article, f'slug_{lang_code}', slug)
    
    await article.save()
    
    return RedirectResponse(url=f"/{lang}/admin/blog", status_code=302)


@router.post("/{lang}/admin/blog/{article_id}/delete")
async def admin_blog_delete(request: Request, lang: str, article_id: int, admin_user: str = Depends(get_admin_user)):
    """Delete blog article"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    try:
        article = await BlogArticle.get(id=article_id)
        await article.delete()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return RedirectResponse(url=f"/{lang}/admin/blog", status_code=302) 