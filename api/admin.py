from fastapi import APIRouter, HTTPException, Form, Depends, Query
from typing import Optional, List
from models.user import User
from models.actions import Bid, BlogArticle
from models.chat import Chat, Message, BannedIP
from models.categories import Category, UnderCategory
from models.places import Country, City
from routers.secur import get_current_user
from datetime import datetime, timedelta
import ipaddress

router = APIRouter()

# Simple demo endpoints without authentication for testing
@router.get("/admin/stats")
async def get_simple_stats():
    """Get basic stats without authentication for demo"""
    try:
        users_count = await User.all().count()
        bids_count = await Bid.all().count()
        chats_count = await Chat.all().count()
        categories_count = await Category.all().count()
        
        return {
            "users_count": users_count,
            "bids_count": bids_count,
            "chats_count": chats_count,
            "categories_count": categories_count
        }
    except Exception as e:
        return {
            "users_count": 0,
            "bids_count": 0,
            "chats_count": 0,
            "categories_count": 0,
            "error": str(e)
        }

@router.get("/admin/users")
async def get_simple_users():
    """Get basic users list without authentication for demo"""
    try:
        users = await User.all().prefetch_related("country")
        
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "user_role": user.user_role or 'user',
                "created_at": user.created_at.isoformat() if user.created_at else None,
            })
        
        return users_data
    except Exception as e:
        return []

@router.put("/admin/users/{user_id}")
async def update_user_simple(
    user_id: int, 
    name: str = Form(...), 
    email: str = Form(...), 
    user_role: str = Form(...),
    nickname: str = Form(None),
    city: str = Form(None),
    profile_description: str = Form(None)
):
    """Update user without authentication for demo"""
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user.name = name
        user.email = email
        user.user_role = user_role
        if nickname is not None:
            user.nickname = nickname
        if city is not None:
            user.city = city
        if profile_description is not None:
            user.profile_description = profile_description
        await user.save()
        
        return {"message": "Пользователь обновлен", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления: {str(e)}")

@router.delete("/admin/users/{user_id}")
async def delete_user_simple(user_id: int):
    """Delete user without authentication for demo"""
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        await user.delete()
        return {"message": "Пользователь удален", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления: {str(e)}")

@router.get("/admin/blogs")
async def get_simple_blogs():
    """Get basic blogs list without authentication for demo"""
    try:
        blogs = await BlogArticle.all().prefetch_related("author").limit(20)
        
        blogs_data = []
        for blog in blogs:
            blogs_data.append({
                "id": blog.id,
                "title_uk": blog.title_uk,
                "title_en": blog.title_en,
                "content_uk": blog.content_uk[:200] + "..." if len(blog.content_uk) > 200 else blog.content_uk,
                "content_en": (blog.content_en[:200] + "..." if blog.content_en and len(blog.content_en) > 200 else blog.content_en) if blog.content_en else "",
                "is_published": blog.is_published,
                "author": blog.author.name if blog.author else "Unknown",
                "created_at": blog.created_at.isoformat() if blog.created_at else None,
            })
        
        return blogs_data
    except Exception as e:
        return []

@router.post("/admin/blogs/create-test")
async def create_test_blog():
    """Create test blog without authentication for demo"""
    try:
        # Find any user for author
        author = await User.first()
        if not author:
            raise HTTPException(status_code=404, detail="Нет пользователей для автора")
        
        # Create test blog
        blog = await BlogArticle.create(
            title_uk="Тестова стаття",
            title_en="Test Article",
            content_uk="Це тестова стаття для демонстрації блогу. Вона містить важливу інформацію про наш сервіс та корисні поради для користувачів.",
            content_en="This is a test article for blog demonstration. It contains important information about our service and useful tips for users.",
            description_uk="Опис тестової статті",
            description_en="Description of test article",
            is_published=True,
            author=author
        )
        
        return {"message": "Тестовый блог создан", "blog_id": blog.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания: {str(e)}")

@router.delete("/admin/blogs/{blog_id}")
async def delete_blog_simple(blog_id: int):
    """Delete blog without authentication for demo"""
    try:
        blog = await BlogArticle.get_or_none(id=blog_id)
        if not blog:
            raise HTTPException(status_code=404, detail="Блог не найден")
        
        await blog.delete()
        return {"message": "Блог удален", "blog_id": blog_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления: {str(e)}")

@router.get("/blog/articles")
async def get_blog_articles(lang: str = Query("uk")):
    """Get published blog articles for frontend"""
    try:
        blogs = await BlogArticle.filter(is_published=True).prefetch_related("author").order_by('-created_at').limit(20)
        
        articles_data = []
        for blog in blogs:
            # Get title and description based on language
            title = getattr(blog, f'title_{lang}', None) or blog.title_uk
            description = getattr(blog, f'description_{lang}', None) or blog.description_uk
            
            articles_data.append({
                "id": blog.id,
                "title": title,
                "description": description or "",
                "slug": getattr(blog, f'slug_{lang}', None) or getattr(blog, 'slug_uk', None) or f"article-{blog.id}",
                "featured_image": blog.featured_image,
                "author_name": blog.author.name if blog.author else "Unknown",
                "created_at": blog.created_at.isoformat() if blog.created_at else None,
                "updated_at": blog.updated_at.isoformat() if blog.updated_at else None,
            })
        
        return articles_data
    except Exception as e:
        return []

async def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    
    if current_user.role != 1:
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    
    return current_user

@router.get("/admin/dashboard")
async def get_dashboard_stats(admin: User = Depends(require_admin)):
    """Get admin dashboard statistics"""
    try:
        # User stats
        total_users = await User.all().count()
        new_users_this_week = await User.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).count()
        
        # Bid stats
        total_bids = await Bid.all().count()
        new_bids_this_week = await Bid.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).count()
        
        # Chat stats
        total_chats = await Chat.all().count()
        total_messages = await Message.all().count()
        
        # Banned IPs
        banned_ips_count = await BannedIP.all().count()
        
        return {
            "users": {
                "total": total_users,
                "new_this_week": new_users_this_week
            },
            "bids": {
                "total": total_bids,
                "new_this_week": new_bids_this_week
            },
            "chats": {
                "total": total_chats,
                "messages": total_messages
            },
            "security": {
                "banned_ips": banned_ips_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

# @router.get("/admin/users")
# async def get_users(
#     page: int = Query(1, ge=1),
#     limit: int = Query(20, ge=1, le=100),
#     search: Optional[str] = Query(None),
#     admin: User = Depends(require_admin)
# ):
#     """Get paginated list of users"""
#     try:
#         offset = (page - 1) * limit
#         
#         # Build query
#         query = User.all()
#         if search:
#             query = query.filter(
#                 name__icontains=search
#             ) | query.filter(
#                 email__icontains=search
#             ) | query.filter(
#                 nickname__icontains=search
#             )
#         
#         total = await query.count()
#         users = await query.offset(offset).limit(limit).prefetch_related("country").all()
#         
#         users_data = []
#         for user in users:
#             users_data.append({
#                 "id": user.id,
#                 "name": user.name,
#                 "nickname": user.nickname,
#                 "email": user.email,
#                 "user_role": user.user_role,
#                 "role": user.role,
#                 "city": user.city,
#                 "country": user.country.name_en if user.country else None,
#                 "created_at": user.created_at.isoformat() if user.created_at else None,
#                 "updated_at": user.updated_at.isoformat() if user.updated_at else None,
#             })
#         
#         return {
#             "users": users_data,
#             "total": total,
#             "page": page,
#             "limit": limit,
#             "pages": (total + limit - 1) // limit
#         }
#     except Exception as e:

@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: int = Form(...),
    admin: User = Depends(require_admin)
):
    """Update user role"""
    try:
        if role not in [0, 1]:  # 0 = user, 1 = admin
            raise HTTPException(status_code=400, detail="Неверная роль")
        
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        user.role = role
        user.user_role = 'admin' if role == 1 else 'user'
        await user.save()
        
        return {"message": "Роль пользователя обновлена", "user_id": user_id, "role": role}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления роли: {str(e)}")

# @router.delete("/admin/users/{user_id}")
# async def delete_user(
#     user_id: int,
#     admin: User = Depends(require_admin)
# ):
#     """Delete user"""
#     try:
#         user = await User.get_or_none(id=user_id)
#         if not user:
#         
#         if user.role == 1:
#         
#         await user.delete()
#     except HTTPException:
#         raise
#     except Exception as e:

@router.get("/admin/bids")
async def get_bids(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin)
):
    """Get paginated list of bids"""
    try:
        offset = (page - 1) * limit
        
        total = await Bid.all().count()
        bids = await Bid.all().offset(offset).limit(limit).prefetch_related("user").all()
        
        bids_data = []
        for bid in bids:
            bids_data.append({
                "id": bid.id,
                "title": bid.title,
                "description": bid.description,
                "budget": bid.budget,
                "status": bid.status,
                "user": {
                    "id": bid.user.id,
                    "name": bid.user.name,
                    "email": bid.user.email
                } if bid.user else None,
                "created_at": bid.created_at.isoformat() if bid.created_at else None,
            })
        
        return {
            "bids": bids_data,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения заявок: {str(e)}")

@router.get("/admin/chats")
async def get_chats(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin)
):
    """Get paginated list of chats"""
    try:
        offset = (page - 1) * limit
        
        total = await Chat.all().count()
        chats = await Chat.all().offset(offset).limit(limit).prefetch_related("user1", "user2").all()
        
        chats_data = []
        for chat in chats:
            chats_data.append({
                "id": chat.id,
                "user1": {
                    "id": chat.user1.id,
                    "name": chat.user1.name,
                    "email": chat.user1.email
                } if chat.user1 else None,
                "user2": {
                    "id": chat.user2.id,
                    "name": chat.user2.name,
                    "email": chat.user2.email
                } if chat.user2 else None,
                "created_at": chat.created_at.isoformat() if chat.created_at else None,
            })
        
        return {
            "chats": chats_data,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения чатов: {str(e)}")

@router.get("/admin/banned-ips")
async def get_banned_ips(admin: User = Depends(require_admin)):
    """Get banned IPs"""
    try:
        banned_ips = await BannedIP.all().all()
        
        ips_data = []
        for ip in banned_ips:
            ips_data.append({
                "id": ip.id,
                "ip_address": ip.ip_address,
                "reason": ip.reason,
                "banned_at": ip.banned_at.isoformat() if ip.banned_at else None,
            })
        
        return {"banned_ips": ips_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения заблокированных IP: {str(e)}")

@router.post("/admin/ban-ip")
async def ban_ip(
    ip_address: str = Form(...),
    reason: str = Form(...),
    admin: User = Depends(require_admin)
):
    """Ban IP address"""
    try:
        # Validate IP address
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат IP адреса")
        
        # Check if already banned
        existing = await BannedIP.get_or_none(ip_address=ip_address)
        if existing:
            raise HTTPException(status_code=400, detail="IP адрес уже заблокирован")
        
        # Create ban record
        banned_ip = await BannedIP.create(
            ip_address=ip_address,
            reason=reason,
            banned_at=datetime.now()
        )
        
        return {"message": "IP адрес заблокирован", "ip_address": ip_address}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка блокировки IP: {str(e)}")

@router.delete("/admin/unban-ip/{ip_id}")
async def unban_ip(
    ip_id: int,
    admin: User = Depends(require_admin)
):
    """Unban IP address"""
    try:
        banned_ip = await BannedIP.get_or_none(id=ip_id)
        if not banned_ip:
            raise HTTPException(status_code=404, detail="IP адрес не найден")
        
        await banned_ip.delete()
        return {"message": "IP адрес разблокирован", "ip_id": ip_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка разблокировки IP: {str(e)}")
