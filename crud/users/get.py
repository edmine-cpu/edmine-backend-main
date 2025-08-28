from schemas.user import UserProfileResponse
from models import User


class UserGetMixin():
    @staticmethod
    async def get_users(search: str = None):
        if search:
            search_lower = search.lower()
            all_users = await User.all().prefetch_related("country", "categories", "subcategories")
            users = [
                user for user in all_users 
                if (user.name and search_lower in user.name.lower()) or
                   (user.email and search_lower in user.email.lower())
            ]
        else:
            users = await User.all().prefetch_related("country", "categories", "subcategories")
        
        if not users:
            return []
        
        return [
            UserProfileResponse(
                id=u.id,
                name=u.name,
                email=u.email,
                city=u.city,
                country=u.country.name_en if u.country else None,
                company_name={
                    "uk": u.company_name_uk,
                    "en": u.company_name_en,
                    "pl": u.company_name_pl,
                    "fr": u.company_name_fr,
                    "de": u.company_name_de,
                },
                company_description={
                    "uk": u.company_description_uk,
                    "en": u.company_description_en,
                    "pl": u.company_description_pl,
                    "fr": u.company_description_fr,
                    "de": u.company_description_de,
                },
                categories=[{"id": c.id, "name": c.name} for c in await u.categories.all()],
                subcategories=[{"id": s.id, "name_uk": s.name_uk, "name_en": s.name_en, "name_pl": s.name_pl, "name_fr": s.name_fr, "name_de": s.name_de} for s in await u.subcategories.all()],
            )
            for u in users
        ]

        
    @staticmethod
    async def get_user_by_id(id: int):
        user = await User.get_or_none(id=id).prefetch_related("country", "categories", "subcategories")
        
        if user is None:
            return None
        
        return UserProfileResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            city=user.city,
            country=user.country.name_en if user.country else None,
            company_name={
                "uk": user.company_name_uk,
                "en": user.company_name_en,
                "pl": user.company_name_pl,
                "fr": user.company_name_fr,
                "de": user.company_name_de,
            },
            company_description={
                "uk": user.company_description_uk,
                "en": user.company_description_en,
                "pl": user.company_description_pl,
                "fr": user.company_description_fr,
                "de": user.company_description_de,
            },
            categories=[{"id": c.id, "name": c.name} for c in await user.categories.all()],
            subcategories=[{"id": s.id, "name_uk": s.name_uk, "name_en": s.name_en, "name_pl": s.name_pl, "name_fr": s.name_fr, "name_de": s.name_de} for s in await user.subcategories.all()],
        )


# Helper functions for direct import
async def get_user_by_id(id: int):
    """Get user by ID - standalone function"""
    return await UserGetMixin.get_user_by_id(id)

async def get_users(search: str = None):
    """Get all users - standalone function"""
    return await UserGetMixin.get_users(search=search)

async def get_user_by_email(email: str):
    """Get user by email - standalone function"""
    user = await User.get_or_none(email=email).prefetch_related("country")
    
    if user is None:
        return None
    
    return UserProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        city=user.city,
        country=user.country.name_en if user.country else None,
        company_name={
            "uk": user.company_name_uk,
            "en": user.company_name_en,
            "pl": user.company_name_pl,
            "fr": user.company_name_fr,
            "de": user.company_name_de,
        },
        company_description={
            "uk": user.company_description_uk,
            "en": user.company_description_en,
            "pl": user.company_description_pl,
            "fr": user.company_description_fr,
            "de": user.company_description_de,
        },
    )