from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.categories import Category, UnderCategory
from tortoise.exceptions import DoesNotExist
from api.translation_utils import translate_text
from api.slug_utils import generate_slug

router = APIRouter()
templates = Jinja2Templates(directory='templates')

SUPPORTED_LANGUAGES = ['uk', 'en', 'pl', 'fr', 'de']

def get_admin_user(request: Request):
    """Get admin user from request state"""
    user_role = getattr(request.state, 'user_role', 0)
    user_email = getattr(request.state, 'user_email', None)
    
    if user_role != 1:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user_email

# Categories admin routes
@router.get("/{lang}/admin/categories")
async def admin_categories_list(request: Request, lang: str, admin_user: str = Depends(get_admin_user)):
    """Admin categories management page"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    # Get all categories
    categories = await Category.all().prefetch_related('undercategories').order_by('id')
    
    return templates.TemplateResponse("admin_categories_list.html", {
        "request": request,
        "lang": lang,
        "categories": categories,
        "user_email": getattr(request.state, 'user_email', None),
        "user_role": getattr(request.state, 'user_role', 0),
    })

@router.get("/{lang}/admin/categories/create")
async def admin_categories_create_form(request: Request, lang: str, admin_user: str = Depends(get_admin_user)):
    """Admin category creation form"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    return templates.TemplateResponse("admin_categories_create.html", {
        "request": request,
        "lang": lang,
        "user_email": getattr(request.state, 'user_email', None),
        "user_role": getattr(request.state, 'user_role', 0),
    })

@router.post("/{lang}/admin/categories/create")
async def admin_categories_create(
    request: Request,
    lang: str,
    name_uk: str = Form(...),
    name_en: str = Form(""),
    name_pl: str = Form(""),
    name_fr: str = Form(""),
    name_de: str = Form(""),
    admin_user: str = Depends(get_admin_user)
):
    """Create new category"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    # Find the primary language (first non-empty)
    names = {'uk': name_uk, 'en': name_en, 'pl': name_pl, 'fr': name_fr, 'de': name_de}
    primary_lang = None
    for lang_code in SUPPORTED_LANGUAGES:
        if names[lang_code].strip():
            primary_lang = lang_code
            break
    
    if not primary_lang:
        raise HTTPException(status_code=400, detail="At least one name must be provided")
    
    # Auto-translate missing fields
    primary_name = names[primary_lang].strip()
    for target_lang in SUPPORTED_LANGUAGES:
        if target_lang != primary_lang and not names[target_lang].strip():
            try:
                translated = await translate_text(primary_name, primary_lang, target_lang)
                names[target_lang] = translated
            except Exception as e:
                print(f"Translation error: {e}")
                names[target_lang] = primary_name
    
    # Create category
    category = await Category.create(
        name_uk=names['uk'],
        name_en=names['en'],
        name_pl=names['pl'],
        name_fr=names['fr'],
        name_de=names['de']
    )
    
    # Generate slugs for all languages
    for lang_code in SUPPORTED_LANGUAGES:
        name = names[lang_code]
        if name:
            slug = generate_slug(name, category.id)
            setattr(category, f'slug_{lang_code}', slug)
    
    await category.save()
    
    return RedirectResponse(url=f"/{lang}/admin/categories", status_code=302)

@router.get("/{lang}/admin/categories/{category_id}/edit")
async def admin_categories_edit_form(request: Request, lang: str, category_id: int, admin_user: str = Depends(get_admin_user)):
    """Admin category edit form"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    try:
        category = await Category.get(id=category_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return templates.TemplateResponse("admin_categories_edit.html", {
        "request": request,
        "lang": lang,
        "category": category,
        "user_email": getattr(request.state, 'user_email', None),
        "user_role": getattr(request.state, 'user_role', 0),
    })

@router.post("/{lang}/admin/categories/{category_id}/edit")
async def admin_categories_edit(
    request: Request,
    lang: str,
    category_id: int,
    name_uk: str = Form(...),
    name_en: str = Form(""),
    name_pl: str = Form(""),
    name_fr: str = Form(""),
    name_de: str = Form(""),
    admin_user: str = Depends(get_admin_user)
):
    """Edit category"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    try:
        category = await Category.get(id=category_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update names
    category.name_uk = name_uk
    category.name_en = name_en
    category.name_pl = name_pl
    category.name_fr = name_fr
    category.name_de = name_de
    
    # Regenerate slugs
    names = {'uk': name_uk, 'en': name_en, 'pl': name_pl, 'fr': name_fr, 'de': name_de}
    for lang_code in SUPPORTED_LANGUAGES:
        name = names[lang_code]
        if name:
            slug = generate_slug(name, category.id)
            setattr(category, f'slug_{lang_code}', slug)
    
    await category.save()
    
    return RedirectResponse(url=f"/{lang}/admin/categories", status_code=302)

@router.post("/{lang}/admin/categories/{category_id}/delete")
async def admin_categories_delete(request: Request, lang: str, category_id: int, admin_user: str = Depends(get_admin_user)):
    """Delete category"""
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail="Language not supported")
    
    try:
        category = await Category.get(id=category_id)
        await category.delete()
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return RedirectResponse(url=f"/{lang}/admin/categories", status_code=302) 