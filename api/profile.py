from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, Request
from typing import Optional, List
import os
import uuid
import shutil
from models.user import User
from models.categories import Category, UnderCategory
from models.places import Country, City
from routers.secur import get_current_user

async def get_current_user_dependency(request: Request):
    return await get_current_user(request)
router = APIRouter()

# Create directories if they don't exist
os.makedirs("static/avatars", exist_ok=True)

@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user_dependency)):
    """Get current user profile with all details"""
    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    try:
        await user.fetch_related("categories", "subcategories", "country")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Get cities for user's country
    cities = []
    if user.country:
        cities = await City.filter(country=user.country).all()
    
    return {
        "id": user.id,
        "name": user.name,
        "nickname": user.nickname,
        "email": user.email,
        "avatar": user.avatar,
        "user_role": user.user_role,
        "profile_description": user.profile_description,
        "city": user.city,
        "country": {
            "id": user.country.id,
            "name_uk": user.country.name_uk,
            "name_en": user.country.name_en,
            "name_pl": user.country.name_pl,
            "name_fr": user.country.name_fr,
            "name_de": user.country.name_de,
        } if user.country else None,
        "language": user.language,
        "categories": [
            {
                "id": cat.id,
                "name_uk": cat.name_uk,
                "name_en": cat.name_en,
                "name_pl": cat.name_pl,
                "name_fr": cat.name_fr,
                "name_de": cat.name_de,
            } for cat in user.categories
        ],
        "subcategories": [
            {
                "id": subcat.id,
                "name_uk": subcat.name_uk,
                "name_en": subcat.name_en,
                "name_pl": subcat.name_pl,
                "name_fr": subcat.name_fr,
                "name_de": subcat.name_de,
            } for subcat in user.subcategories
        ],
        "cities": [
            {
                "id": city.id,
                "name_uk": city.name_uk,
                "name_en": city.name_en,
                "name_pl": city.name_pl,
                "name_fr": city.name_fr,
                "name_de": city.name_de,
            } for city in cities
        ]
    }

@router.put("/profile/nickname")
async def update_nickname(
    value: str = Form(...),
    user: User = Depends(get_current_user_dependency)
):
    """Update user nickname"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user.nickname = value
    await user.save()
    return {"message": "Nickname updated successfully"}

@router.put("/profile/name")
async def update_name(
    value: str = Form(...),
    user: User = Depends(get_current_user_dependency)
):
    """Update user name"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user.name = value
    await user.save()
    return {"message": "Name updated successfully"}

@router.put("/profile/description")
async def update_description(
    value: str = Form(...),
    user: User = Depends(get_current_user_dependency)
):
    """Update user description"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user.profile_description = value
    await user.save()
    return {"message": "Description updated successfully"}

@router.put("/profile/role")
async def update_role(
    value: str = Form(...),
    user: User = Depends(get_current_user_dependency)
):
    """Update user role"""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user.user_role = value
    await user.save()
    return {"message": "Role updated successfully"}

@router.put("/profile/avatar")
async def update_avatar(
    avatar: UploadFile = File(...),
    user: User = Depends(get_current_user_dependency)
):
    """Upload/update user avatar"""
    # Check file type
    if not avatar.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Check file size (max 5MB)
    if avatar.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    # Generate unique filename
    file_extension = avatar.filename.split('.')[-1] if '.' in avatar.filename else 'jpg'
    filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = f"static/avatars/{filename}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)
    
    # Remove old avatar if exists
    if user.avatar and os.path.exists(user.avatar):
        try:
            os.remove(user.avatar)
        except:
            pass
    
    # Update user avatar path
    user.avatar = file_path
    await user.save()
    
    return {"message": "Avatar updated successfully", "avatar": user.avatar}



@router.put("/profile/categories")
async def update_categories(
    category_ids: str = Form(...),  # comma-separated IDs
    subcategory_ids: str = Form(""),  # comma-separated IDs
    user: User = Depends(get_current_user_dependency)
):
    """Update user categories and subcategories"""
    # Parse category IDs
    try:
        cat_ids = [int(x.strip()) for x in category_ids.split(',') if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category IDs")
    
    # Parse subcategory IDs
    try:
        subcat_ids = [int(x.strip()) for x in subcategory_ids.split(',') if x.strip()] if subcategory_ids else []
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subcategory IDs")
    
    # Validate categories exist
    categories = await Category.filter(id__in=cat_ids).all()
    if len(categories) != len(cat_ids):
        raise HTTPException(status_code=400, detail="Some categories not found")
    
    # Validate subcategories exist
    subcategories = []
    if subcat_ids:
        subcategories = await UnderCategory.filter(id__in=subcat_ids).all()
        if len(subcategories) != len(subcat_ids):
            raise HTTPException(status_code=400, detail="Some subcategories not found")
    
    # Update user relations
    await user.categories.clear()
    await user.subcategories.clear()
    
    for category in categories:
        await user.categories.add(category)
    
    for subcategory in subcategories:
        await user.subcategories.add(subcategory)
    
    return {"message": "Categories updated successfully"}

@router.put("/profile/location")
async def update_location(
    country_id: int = Form(...),
    city: str = Form(...),
    user: User = Depends(get_current_user_dependency)
):
    """Update user country and city"""
    # Validate country
    country = await Country.get_or_none(id=country_id)
    if not country:
        raise HTTPException(status_code=400, detail="Invalid country")
    
    # Validate city exists in the country
    city_obj = await City.filter(country=country, id=city).first()

    
    if not city_obj:
        raise HTTPException(status_code=400, detail="City not found in selected country")
    
    # Update user location
    user.country = country
    user.city = await City.filter(id=city).first()
    await user.save()
    
    return {"message": "Location updated successfully"}

@router.delete("/profile/avatar")
async def delete_avatar(user: User = Depends(get_current_user_dependency)):
    """Delete user avatar"""
    if user.avatar and os.path.exists(user.avatar):
        try:
            os.remove(user.avatar)
        except:
            pass
    
    user.avatar = None
    await user.save()
    
    return {"message": "Avatar deleted successfully"}

@router.put("/profile/multilang")
async def update_multilang_info(
    company_name_uk: str = Form(""),
    company_name_en: str = Form(""),
    company_name_pl: str = Form(""),
    company_name_fr: str = Form(""),
    company_name_de: str = Form(""),
    company_description_uk: str = Form(""),
    company_description_en: str = Form(""),
    company_description_pl: str = Form(""),
    company_description_fr: str = Form(""),
    company_description_de: str = Form(""),
    user: User = Depends(get_current_user_dependency)
):
    """Update user multilanguage company information"""
    # Update company names
    user.company_name_uk = company_name_uk.strip() if company_name_uk else None
    user.company_name_en = company_name_en.strip() if company_name_en else None
    user.company_name_pl = company_name_pl.strip() if company_name_pl else None
    user.company_name_fr = company_name_fr.strip() if company_name_fr else None
    user.company_name_de = company_name_de.strip() if company_name_de else None
    
    # Update company descriptions
    user.company_description_uk = company_description_uk.strip() if company_description_uk else None
    user.company_description_en = company_description_en.strip() if company_description_en else None
    user.company_description_pl = company_description_pl.strip() if company_description_pl else None
    user.company_description_fr = company_description_fr.strip() if company_description_fr else None
    user.company_description_de = company_description_de.strip() if company_description_de else None
    
    await user.save()
    
    return {"message": "Multilanguage company information updated successfully"}


