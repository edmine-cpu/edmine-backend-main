from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
import os
from dotenv import load_dotenv
from api.admin import router as admin_router
from api.bids import router as bids_router
from api.blog import router as blog_router
from api.categories import router as categories_get_router
from api.chat import router as chat_router
from api.password_reset import router as password_reset_router
from api.places import router as places_get_router
from api.profile import router as profile_router
from api.user import router as user_router
from api.company import router as company_router
from api.v2.bids import router as bids_v2_router
from routers.secur import router as jwt_router

app = FastAPI()

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response


app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://82.25.86.30:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400, 
)


app.include_router(jwt_router, prefix="", tags=["Auth"])
app.include_router(categories_get_router, prefix="/check", tags=["Categories"])
app.include_router(places_get_router, prefix="/api", tags=["Places"])
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(bids_router, prefix="/api", tags=["Bids"])
app.include_router(bids_v2_router, prefix="/api/v2", tags=["Bids V2"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(profile_router, prefix="/api", tags=["Profile"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
app.include_router(blog_router, prefix="/api", tags=["Blog"])
app.include_router(password_reset_router, prefix="/api", tags=["Password Reset"])
app.include_router(company_router, prefix="/api", tags=["Company"])


class OptimizedStaticFiles(StaticFiles):
    def __init__(self, directory: str):
        super().__init__(directory=directory)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            
            if path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico')):
                cache_control = "public, max-age=86400"  # 24 часа для изображений
            elif path.endswith(('.css', '.js')):
                cache_control = "public, max-age=3600"   # 1 час для CSS/JS
            elif path.endswith(('.pdf', '.txt')):
                cache_control = "public, max-age=1800"   # 30 минут для документов
            else:
                cache_control = "public, max-age=300"    # 5 минут для остальных
            
            # Переопределяем send для добавления заголовков
            original_send = send
            
            async def send_with_cache_headers(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append([b"cache-control", cache_control.encode()])
                    headers.append([b"etag", f'"{hash(path)}"'.encode()])
                    message["headers"] = headers
                await original_send(message)
            
            return await super().__call__(scope, receive, send_with_cache_headers)
        
        return await super().__call__(scope, receive, send)

app.mount("/static", OptimizedStaticFiles(directory="static"), name="static")

load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")

register_tortoise(
    app,
    db_url=f"postgres://postgres:{DB_PASSWORD}@0.0.0.0:5432/makeasap_dev",
    modules={
        "models": [
            "models.user",
            "models.actions",
            "models.categories",
            "models.places",
            "models.chat",
            "models.password_reset",
        ]
    },
    generate_schemas=False,
    add_exception_handlers=True,
)

