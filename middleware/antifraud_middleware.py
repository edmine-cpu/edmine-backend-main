"""
Middleware для антифрод системы
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import json
from utils.antifraud import antifraud
from routers.secur import get_current_user


async def antifraud_middleware(request: Request, call_next):
    """Middleware для проверки антифрод системы"""
    
    # Получаем IP адрес
    client_ip = request.client.host
    if 'x-forwarded-for' in request.headers:
        client_ip = request.headers['x-forwarded-for'].split(',')[0].strip()
    
    # Получаем пользователя (если авторизован)
    user = None
    user_id = None
    try:
        user = await get_current_user(request)
        user_id = user.id if user else None
    except:
        pass  # Не авторизован или ошибка авторизации
    
    # Определяем действие на основе URL и метода
    action = _get_action_from_request(request)
    
    # Проверяем лимиты скорости
    rate_check = await antifraud.check_rate_limits(user_id, client_ip, action)
    
    if not rate_check['allowed']:
        return JSONResponse(
            status_code=429,
            content={
                'error': 'Rate limit exceeded',
                'message': rate_check['reason'],
                'retry_after': rate_check['retry_after']
            },
            headers={'Retry-After': str(rate_check['retry_after'])}
        )
    
    # Подготавливаем данные запроса для анализа
    request_data = await _prepare_request_data(request)
    
    # Проверяем подозрительные паттерны
    pattern_check = await antifraud.detect_suspicious_patterns(
        user_id, client_ip, request_data
    )
    
    # Логируем активность
    await antifraud.log_activity(
        user_id, client_ip, action, 
        {
            'user_id': user_id,
            'risk_score': pattern_check['risk_score'],
            'patterns': pattern_check['patterns']
        }
    )
    
    # Если обнаружены подозрительные паттерны
    if pattern_check['is_suspicious']:
        if action in ['login', 'register']:
            # Требуем капчу для подозрительных попыток входа/регистрации
            return JSONResponse(
                status_code=403,
                content={
                    'error': 'Suspicious activity detected',
                    'message': 'Please complete captcha verification',
                    'require_captcha': True,
                    'risk_score': pattern_check['risk_score']
                }
            )
        elif pattern_check['risk_score'] > 150:  # Очень высокий риск
            return JSONResponse(
                status_code=403,
                content={
                    'error': 'Access denied',
                    'message': 'Suspicious activity detected. Access temporarily restricted.',
                    'patterns': pattern_check['patterns']
                }
            )
    
    # Проверяем, нужно ли заблокировать пользователя
    if user_id:
        block_check = await antifraud.should_block_user(user_id)
        if block_check['should_block']:
            return JSONResponse(
                status_code=403,
                content={
                    'error': 'Account blocked',
                    'message': f"Account temporarily blocked: {block_check['reason']}",
                    'duration': block_check['duration']
                }
            )
    
    # Продолжаем выполнение запроса
    response = await call_next(request)
    
    # Логируем результат
    if response.status_code >= 400:
        await antifraud.log_activity(
            user_id, client_ip, f"{action}_failed",
            {'status_code': response.status_code}
        )
    
    return response


def _get_action_from_request(request: Request) -> str:
    """Определить действие на основе запроса"""
    path = request.url.path
    method = request.method
    
    if '/api/login' in path:
        return 'login'
    elif '/api/register' in path:
        return 'register'
    elif '/api/bids' in path and method == 'POST':
        return 'create_bid'
    elif '/api/chats' in path and 'messages' in path and method == 'POST':
        return 'send_message'
    elif '/api/profile' in path and method == 'POST':
        return 'update_profile'
    elif '/api/admin' in path:
        return 'admin_action'
    elif method == 'POST':
        return 'create_content'
    elif method == 'PUT' or method == 'PATCH':
        return 'update_content'
    elif method == 'DELETE':
        return 'delete_content'
    else:
        return 'general_request'


async def _prepare_request_data(request: Request) -> dict:
    """Подготовить данные запроса для анализа"""
    data = {
        'user_agent': request.headers.get('user-agent', ''),
        'referer': request.headers.get('referer', ''),
        'content_type': request.headers.get('content-type', ''),
    }
    
    # Пытаемся получить данные тела запроса (для POST/PUT)
    if request.method in ['POST', 'PUT', 'PATCH']:
        try:
            # Создаем копию тела запроса
            body = await request.body()
            if body:
                if 'application/json' in data['content_type']:
                    try:
                        json_data = json.loads(body.decode())
                        # Извлекаем только безопасные поля
                        safe_fields = ['email', 'username', 'name', 'city', 'country']
                        for field in safe_fields:
                            if field in json_data:
                                data[field] = json_data[field]
                    except:
                        pass
        except:
            pass  # Не критично, если не можем прочитать тело
    
    return data
