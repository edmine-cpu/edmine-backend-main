from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from models.chat import BannedIP
import ipaddress

async def check_ip_ban(request: Request):
    """Middleware to check if client IP is banned"""
    # Get client IP from request
    client_ip = request.client.host
    
    # Handle forwarded headers (if behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        client_ip = real_ip.strip()
    
    try:
        # Validate IP address format
        ipaddress.ip_address(client_ip)
        
        # Check if IP is banned
        banned = await BannedIP.get_or_none(ip=client_ip)
        if banned:
            return JSONResponse(
                status_code=403,
                content={"detail": f"Your IP address {client_ip} has been banned. Reason: {banned.reason}"}
            )
    except ValueError:
        # Invalid IP format, allow the request
        pass
    
    return None  # Continue processing
