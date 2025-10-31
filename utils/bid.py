import os
import secrets
import asyncio
import aiofiles
from typing import Optional, List

from fastapi import UploadFile, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.bids_config import ALLOWED_FILE_TYPES, MAX_FILES_COUNT, TEMP_FILES_DIR, BID_FILES_DIR
from models import Category

async def _validate_uploaded_files(
        files: Optional[List[UploadFile]],
        user_role: Optional[str],
        user_email: Optional[str],
        lang: str,
        form: dict
) -> List[str]:

    """
    Асинхронная проверка загруженных файлов: тип, размер, количество.
    Возвращает список временных путей к файлам.
    """
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.pdf', '.bmp', '.gif'}
    temp_file_paths = []

    if not files:
        return []

    if len(files) > MAX_FILES_COUNT:
        raise HTTPException(status_code=400, detail=f'Максимальна кількість файлів: {MAX_FILES_COUNT}')

    async def process_single_file(file):
        ext = os.path.splitext(file.filename or '')[1].lower()
        if file.content_type not in ALLOWED_FILE_TYPES and ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f'Непідтримуваний тип файлу: {file.content_type}')

        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail='Розмір файлу не може перевищувати 10MB')

        temp_filename = secrets.token_urlsafe(16).replace('-', '_').replace('=', '_') + ext
        temp_file_path = os.path.join(TEMP_FILES_DIR, temp_filename)

        os.makedirs(TEMP_FILES_DIR, exist_ok=True)
        async with aiofiles.open(temp_file_path, 'wb') as f:
            await f.write(content)

        return temp_file_path

    tasks = [process_single_file(file) for file in files]
    temp_file_paths = await asyncio.gather(*tasks)
    
    return temp_file_paths

async def _move_files_to_final_location(temp_file_paths: List[str]) -> List[str]:
    """
    Асинхронно перемещает временные файлы в финальную папку BID_FILES_DIR и возвращает их новые пути.
    """
    final_file_paths = []

    async def move_single_file(temp_path):
        if not os.path.exists(temp_path):
            return None

        filename = os.path.basename(temp_path)
        safe_filename = ''.join(c if c.isalnum() or c == '.' else '_' for c in filename)
        final_path = os.path.join(BID_FILES_DIR, safe_filename)

        counter = 1
        base, ext = os.path.splitext(safe_filename)
        while os.path.exists(final_path):
            safe_filename = f"{base}_{counter}{ext}"
            final_path = os.path.join(BID_FILES_DIR, safe_filename)
            counter += 1

        os.makedirs(BID_FILES_DIR, exist_ok=True)
        os.rename(temp_path, final_path)
        return final_path

    tasks = [move_single_file(temp_path) for temp_path in temp_file_paths]
    results = await asyncio.gather(*tasks)
    
    final_file_paths = [path for path in results if path is not None]

    return final_file_paths

async def _process_category_id(category: Optional[str]) -> Optional[int]:
    """
    Получить ID категории или None если некорректная
    """
    try:
        if not category or category.strip() == '' or category == 'None':
            return None
        category_id = int(category)
        category_obj = await Category.get(id=category_id)
        return category_obj.id
    except Exception:
        return None

async def _process_under_category_id(under_category: Optional[str]) -> Optional[int]:
    """
    Получить ID подкатегории или None если некорректная
    """
    try:
        if not under_category or under_category.strip() == '' or under_category == 'None':
            return None
        under_category_id = int(under_category)
        return under_category_id
    except Exception:
        return None