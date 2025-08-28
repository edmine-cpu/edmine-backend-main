from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from typing import Optional
from models import User
from models.chat import Chat, Message
from routers.secur import get_current_user

async def get_current_user_dependency(request: Request):
    return await get_current_user(request)

import os
import uuid
from datetime import datetime

router = APIRouter()

# Создаем директорию для файлов если её нет
os.makedirs("static/chat_files", exist_ok=True)

@router.get('/chats')
async def get_user_chats(current_user: User = Depends(get_current_user_dependency)):
    """Get all chats for current user"""
    try:
        from tortoise import models
        chats = await Chat.filter(
            models.Q(user1_id=current_user.id) | models.Q(user2_id=current_user.id)
        ).prefetch_related("user1", "user2").all()
        
        result = []
        for chat in chats:
            # Get partner (other user)
            partner = chat.user2 if chat.user1.id == current_user.id else chat.user1
            
            # Get latest message
            latest_message = await Message.filter(chat=chat).prefetch_related("sender").order_by("-created_at").first()
            
            # Get unread count
            unread_count = await Message.filter(
                chat=chat,
                sender=partner,
                is_read=False
            ).count()
            
            # Используем имя из регистрации или nickname
            display_name = partner.name if partner.name and partner.name != 'temp' else (partner.nickname or partner.email.split('@')[0])
            
            result.append({
                "id": chat.id,
                "partner": {
                    "id": partner.id,
                    "name": display_name,
                    "avatar": partner.avatar,
                    "email": partner.email
                },
                "latest_message": {
                    "content": latest_message.content if latest_message else "",
                    "created_at": latest_message.created_at.isoformat() if latest_message else chat.created_at.isoformat(),
                    "is_file": bool(latest_message.file_path) if latest_message else False,
                    "sender_id": latest_message.sender.id if latest_message else None
                } if latest_message else None,
                "unread_count": unread_count,
                "created_at": chat.created_at.isoformat() if chat.created_at else None
            })
        
        # Sort by latest activity
        result.sort(key=lambda x: x["latest_message"]["created_at"] if x["latest_message"] else x["created_at"], reverse=True)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения чатов: {str(e)}")

@router.post('/chats')
async def create_or_get_chat(
    partner_id: int = Form(...), 
    current_user: User = Depends(get_current_user_dependency)
):
    """Create or get existing chat with partner"""
    try:
        if current_user.id == partner_id:
            raise HTTPException(status_code=400, detail="Нельзя создать чат с самим собой")

        # Проверяем существование партнера
        partner = await User.get_or_none(id=partner_id)
        if not partner:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        # Ищем существующий чат
        chat = await Chat.filter(
            user1_id=min(current_user.id, partner_id), 
            user2_id=max(current_user.id, partner_id)
        ).first()
        
        if chat is None:
            # Создаем новый чат
            chat = await Chat.create(
                user1_id=min(current_user.id, partner_id), 
                user2_id=max(current_user.id, partner_id)
            )
        
        # Используем имя из регистрации или nickname
        display_name = partner.name if partner.name and partner.name != 'temp' else (partner.nickname or partner.email.split('@')[0])
        
        return {
            "chat_id": chat.id,
            "partner": {
                "id": partner.id,
                "name": display_name,
                "avatar": partner.avatar,
                "email": partner.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка создания чата: {str(e)}")

@router.get('/chats/{chat_id}/messages')
async def list_messages(
    chat_id: int, 
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user_dependency)
):
    """Get messages from chat"""
    try:
        chat = await Chat.get_or_none(id=chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            raise HTTPException(status_code=403, detail="Нет доступа к этому чату")

        # Пагинация
        offset = (page - 1) * limit
        
        messages = await Message.filter(chat_id=chat_id).prefetch_related("sender").order_by('-created_at').offset(offset).limit(limit)
        
        # Помечаем сообщения как прочитанные
        await Message.filter(
            chat_id=chat_id,
            is_read=False
        ).exclude(sender=current_user).update(is_read=True)
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "content": msg.content,
                "file_path": msg.file_path,
                "file_name": msg.file_name,
                "file_size": msg.file_size,
                "sender_id": msg.sender.id,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        return {
            "messages": result,
            "page": page,
            "limit": limit,
            "has_more": len(result) == limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения сообщений: {str(e)}")

@router.post('/chats/{chat_id}/messages')
async def send_message(
    chat_id: int, 
    content: Optional[str] = Form(None), 
    file: Optional[UploadFile] = File(None), 
    current_user: User = Depends(get_current_user_dependency)
):
    """Send message to chat"""
    try:
        # Проверяем доступ к чату
        chat = await Chat.get_or_none(id=chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            raise HTTPException(status_code=403, detail="Нет доступа к этому чату")

        # Валидация
        if not content and not file:
            raise HTTPException(status_code=400, detail="Сообщение или файл обязательны")

        if content and len(content.strip()) == 0:
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

        file_path = None
        file_name = None
        file_size = None

        # Обработка файла
        if file:
            # Проверяем размер файла (максимум 10MB)
            if file.size and file.size > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Файл слишком большой (максимум 10MB)")

            # Проверяем тип файла
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain']
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail="Неподдерживаемый тип файла")

            # Сохраняем файл
            file_extension = os.path.splitext(file.filename)[1] if file.filename else '.txt'
            file_name = f"{uuid.uuid4()}{file_extension}"
            file_path = f"static/chat_files/{file_name}"
            
            with open(file_path, "wb") as buffer:
                content_data = await file.read()
                buffer.write(content_data)
                file_size = len(content_data)

        # Создаем сообщение
        message = await Message.create(
            chat_id=chat_id,
            sender=current_user,
            content=content.strip() if content else "",
            file_path=file_path,
            file_name=file.filename if file else None,
            file_size=file_size,
            is_read=False
        )

        return {
            "id": message.id,
            "content": message.content,
            "file_path": message.file_path,
            "file_name": message.file_name,
            "file_size": message.file_size,
            "sender_id": message.sender.id,
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat() if message.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отправки сообщения: {str(e)}")

@router.delete('/chats/{chat_id}/messages/{message_id}')
async def delete_message(
    chat_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user_dependency)
):
    """Delete message (only sender can delete)"""
    try:
        message = await Message.get_or_none(id=message_id, chat_id=chat_id).prefetch_related("sender")
        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")

        if message.sender.id != current_user.id:
            raise HTTPException(status_code=403, detail="Можно удалять только свои сообщения")

        # Удаляем файл если есть
        if message.file_path and os.path.exists(message.file_path):
            os.remove(message.file_path)

        await message.delete()
        return {"message": "Сообщение удалено"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления сообщения: {str(e)}")

@router.get('/chats/{chat_id}/unread-count')
async def get_unread_count(
    chat_id: int,
    current_user: User = Depends(get_current_user_dependency)
):
    """Get unread messages count for chat"""
    try:
        chat = await Chat.get_or_none(id=chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            raise HTTPException(status_code=403, detail="Нет доступа к этому чату")

        # Получаем партнера
        partner_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id

        unread_count = await Message.filter(
            chat_id=chat_id,
            sender__id=partner_id,
            is_read=False
        ).count()

        return {"unread_count": unread_count}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения количества непрочитанных сообщений: {str(e)}")


