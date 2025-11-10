from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from typing import Optional
from models import User
from models.chat import Chat, Message
from routers.secur import get_current_user
from services.translation.utils import translate_text, SUPPORTED_LANGUAGES
from deep_translator import GoogleTranslator

async def get_current_user_dependency(request: Request):
    return await get_current_user(request)

import os
import uuid
from datetime import datetime

router = APIRouter()

async def detect_message_language(text: str) -> str:
    """Auto-detect message language"""
    if not text or not text.strip():
        return 'uk'
    
    try:
        from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES
        
        
        sample_text = text[:100]
        
        
        test_translations = {}
        for lang in SUPPORTED_LANGUAGES:
            try:
                translator = GoogleTranslator(source='auto', target=lang)
                translated = translator.translate(sample_text)
                
                if translated and len(translated.strip()) > 0:
                    similarity = len(set(sample_text.lower().split()) & set(translated.lower().split()))
                    test_translations[lang] = similarity
            except:
                continue
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['hello', 'hi', 'good', 'how', 'what', 'the', 'and', 'you', 'are', 'that', 'sounds', 'great', 'plans', 'weekend']):
            return 'en'
        elif any(word in text_lower for word in ['привіт', 'привет', 'як', 'як справи', 'добре', 'дякую', 'спасибо', 'що', 'де', 'коли', 'все', 'плануємо', 'поїхати', 'дачу']):
            return 'uk'
        elif any(word in text_lower for word in ['dzień', 'dobry', 'jak', 'się', 'masz', 'dziękuję', 'dzięki', 'cześć', 'witaj']):
            return 'pl'
        elif any(word in text_lower for word in ['bonjour', 'comment', 'allez', 'vous', 'merci', 'au revoir', 'salut']):
            return 'fr'
        elif any(word in text_lower for word in ['guten', 'tag', 'wie', 'geht', 'ihnen', 'danke', 'auf wiedersehen', 'hallo']):
            return 'de'

        if 'привет' in text_lower:
            return 'uk'
        elif 'hello' in text_lower:
            return 'en'

        return 'uk'

    except Exception as e:
        return 'uk'

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

        partner = await User.get_or_none(id=partner_id)
        if not partner:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        chat = await Chat.filter(
            user1_id=min(current_user.id, partner_id), 
            user2_id=max(current_user.id, partner_id)
        ).first()
        
        if chat is None:
            chat = await Chat.create(
                user1_id=min(current_user.id, partner_id), 
                user2_id=max(current_user.id, partner_id)
            )
        
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
    translate_to: Optional[str] = None,
    current_user: User = Depends(get_current_user_dependency)
):
    """Get messages from chat"""
    try:
        chat = await Chat.get_or_none(id=chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            raise HTTPException(status_code=403, detail="Нет доступа к этому чату")

        offset = (page - 1) * limit
        
        messages = await Message.filter(chat_id=chat_id).prefetch_related("sender").order_by('-created_at').offset(offset).limit(limit)
        
        await Message.filter(
            chat_id=chat_id,
            is_read=False
        ).exclude(sender=current_user).update(is_read=True)
        
        result = []
        for msg in messages:
            msg_data = {
                "id": msg.id,
                "content": msg.content,
                "file_path": msg.file_path,
                "file_name": msg.file_name,
                "file_size": msg.file_size,
                "sender_id": msg.sender.id,
                "is_read": msg.is_read,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            }
            
            if translate_to and translate_to in SUPPORTED_LANGUAGES and msg.content:
                try:
                    detected_language = await detect_message_language(msg.content)
                    if detected_language != translate_to:
                        translated_content = await translate_text(msg.content, detected_language, translate_to)
                        if translated_content:
                            msg_data["translated_content"] = translated_content
                            msg_data["detected_language"] = detected_language
                            msg_data["target_language"] = translate_to
                            msg_data["is_translated"] = True
                        else:
                            msg_data["is_translated"] = False
                    else:
                        msg_data["is_translated"] = False
                except Exception as e:
                    msg_data["is_translated"] = False
            else:
                msg_data["is_translated"] = False
            
            result.append(msg_data)
        
        return {
            "messages": result,
            "page": page,
            "limit": limit,
            "has_more": len(result) == limit,
            "translation_enabled": translate_to is not None,
            "target_language": translate_to,
            "supported_languages": SUPPORTED_LANGUAGES
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
        chat = await Chat.get_or_none(id=chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            raise HTTPException(status_code=403, detail="Нет доступа к этому чату")

        # Валидация контента
        if not content and not file:
            raise HTTPException(status_code=400, detail="Сообщение или файл обязательны")

        if content and len(content.strip()) == 0:
            raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

        file_path = None
        file_size = None

        if file:
            # Разрешаем все типы файлов
            # Список опасных расширений, которые не разрешаем
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.ps1', '.msi', '.scr', '.com', '.pif']

            file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else '.txt'

            if file_extension in dangerous_extensions:
                raise HTTPException(status_code=400, detail="Исполняемые файлы запрещены из соображений безопасности")

            # Генерируем уникальное имя файла
            unique_file_name = f"{uuid.uuid4()}{file_extension}"
            # Путь для сохранения на диске (физический путь)
            disk_path = f"static/chat_files/{unique_file_name}"
            # Путь для URL (относительно /static)
            file_path = f"/chat_files/{unique_file_name}"

            # Читаем и сохраняем файл chunk by chunk для больших файлов
            chunk_size = 1024 * 1024  # 1MB chunks
            total_size = 0
            max_size = 50 * 1024 * 1024  # 50MB max

            with open(disk_path, "wb") as buffer:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > max_size:
                        # Удаляем частично загруженный файл
                        buffer.close()
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        raise HTTPException(status_code=400, detail="Файл слишком большой (максимум 50MB)")
                    buffer.write(chunk)

            file_size = total_size

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
            "sender_id": current_user.id,  # Используем current_user.id напрямую
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

@router.post('/chats/{chat_id}/translate')
async def translate_chat_messages(
    chat_id: int,
    target_language: str = Form(...),
    current_user: User = Depends(get_current_user_dependency)
):
    """Translate chat messages to specified language"""
    try:
        chat = await Chat.get_or_none(id=chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        if current_user.id not in [chat.user1_id, chat.user2_id]:
            raise HTTPException(status_code=403, detail="Нет доступа к этому чату")

        if target_language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=400, 
                detail=f"Неподдерживаемый язык. Поддерживаемые языки: {', '.join(SUPPORTED_LANGUAGES)}"
            )

        partner_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id

        partner_messages = await Message.filter(
            chat_id=chat_id,
            sender__id=partner_id
        ).prefetch_related("sender").order_by('-created_at').all()

        translated_messages = []
        
        for message in partner_messages:
            if not message.content or not message.content.strip():
                translated_messages.append({
                    "id": message.id,
                    "original_content": message.content,
                    "translated_content": message.content,
                    "detected_language": None,
                    "target_language": target_language,
                    "translation_available": False
                })
                continue
            
            detected_language = await detect_message_language(message.content)
            print(f"Message '{message.content}' detected as language: {detected_language}")
            
            translated_content = message.content
            translation_available = True
            
            if detected_language != target_language:
                print(f"Translating from {detected_language} to {target_language}")
                translated_result = await translate_text(
                    message.content, 
                    detected_language, 
                    target_language
                )
                
                if translated_result:
                    translated_content = translated_result
                    print(f"Translation result: {translated_result}")
                else:
                    translation_available = False
                    print("Translation failed")
            else:
                print(f"No translation needed - same language ({detected_language})")
            
            translated_messages.append({
                "id": message.id,
                "original_content": message.content,
                "translated_content": translated_content,
                "detected_language": detected_language,
                "target_language": target_language,
                "translation_available": translation_available,
                "created_at": message.created_at.isoformat() if message.created_at else None
            })

        return {
            "chat_id": chat_id,
            "target_language": target_language,
            "total_messages": len(translated_messages),
            "translated_messages": translated_messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка перевода сообщений: {str(e)}")


