from fastapi import Request, HTTPException
from fastapi.responses import Response
import time
import secrets
from typing import Dict, Set
import asyncio

# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, list] = {}
failed_attempts: Dict[str, int] = {}
blocked_ips: Set[str] = set()

# CSRF token storage (in production, use secure session storage)
csrf_tokens: Set[str] = set()

def cleanup_rate_limit():
    """Clean up old rate limit entries"""
    current_time = time.time()
    for ip in list(rate_limit_storage.keys()):
        rate_limit_storage[ip] = [
            timestamp for timestamp in rate_limit_storage[ip]
            if current_time - timestamp < 3600  # Keep last hour
        ]
        if not rate_limit_storage[ip]:
            del rate_limit_storage[ip]

async def rate_limit_middleware(request: Request):
    """Rate limiting middleware"""
    client_ip = request.client.host
    
    # Get real IP if behind proxy
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    # Check if IP is temporarily blocked
    if client_ip in blocked_ips:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    current_time = time.time()
    
    # Initialize rate limit tracking for IP
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = []
    
    # Clean old requests
    rate_limit_storage[client_ip] = [
        timestamp for timestamp in rate_limit_storage[client_ip]
        if current_time - timestamp < 60  # Last minute
    ]
    
    # Check rate limit (60 requests per minute)
    if len(rate_limit_storage[client_ip]) >= 60:
        # Block IP for 1 hour if too many requests
        blocked_ips.add(client_ip)
        asyncio.create_task(unblock_ip_after_delay(client_ip, 3600))
        raise HTTPException(status_code=429, detail="Rate limit exceeded. IP blocked for 1 hour.")
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    
    # Clean up periodically
    if len(rate_limit_storage) > 1000:
        cleanup_rate_limit()

async def unblock_ip_after_delay(ip: str, delay: int):
    """Unblock IP after delay"""
    await asyncio.sleep(delay)
    blocked_ips.discard(ip)

def add_security_headers(response: Response):
    """Add security headers to response"""
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # CSP for API responses
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: http://82.25.86.30:8000; "
        "connect-src 'self' http://82.25.86.30:8000; "
        "font-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    
    return response

def generate_csrf_token() -> str:
    """Generate CSRF token"""
    token = secrets.token_urlsafe(32)
    csrf_tokens.add(token)
    return token

def validate_csrf_token(token: str) -> bool:
    """Validate CSRF token"""
    if token in csrf_tokens:
        csrf_tokens.remove(token)  # Single use
        return True
    return False

async def validate_request_size(request: Request, max_size: int = 50 * 1024 * 1024):  # 50MB
    """Validate request size"""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > max_size:
        raise HTTPException(status_code=413, detail="Request too large")

def sanitize_input(input_str: str) -> str:
    """Basic input sanitization"""
    if not input_str:
        return input_str
    
    # Remove potential XSS patterns
    dangerous_patterns = ["<script", "</script", "javascript:", "on", "eval("]
    sanitized = input_str
    
    for pattern in dangerous_patterns:
        sanitized = sanitized.replace(pattern.lower(), "")
        sanitized = sanitized.replace(pattern.upper(), "")
    
    return sanitized.strip()

# SQL injection protection patterns
def check_sql_injection(input_str: str) -> bool:
    """Check for potential SQL injection"""
    if not input_str:
        return False
    
    sql_patterns = [
        "' OR '1'='1",
        "' OR 1=1",
        "' UNION SELECT",
        "'; DROP TABLE",
        "'; DELETE FROM",
        "'; INSERT INTO",
        "'; UPDATE",
        "' AND 1=1",
        "1' OR '1'='1",
    ]
    
    input_lower = input_str.lower()
    return any(pattern.lower() in input_lower for pattern in sql_patterns)

def validate_file_upload(filename: str, content_type: str, max_size: int = 30 * 1024 * 1024) -> bool:
    """Validate file upload"""
    if not filename:
        return False
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip'}
    file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    if file_ext not in allowed_extensions:
        return False
    
    # Check content type
    allowed_content_types = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'application/msword', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain', 'application/zip'
    }
    
    if content_type not in allowed_content_types:
        return False
    
    return True
