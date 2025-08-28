import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

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
# from routers.bid import router as bid_router
from routers.secur import router as jwt_router

app = FastAPI()


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    response = await call_next(request)
    return response

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
)


app.include_router(jwt_router, prefix="", tags=["Auth"])
app.include_router(categories_get_router, prefix="/check", tags=["Categories"])
app.include_router(places_get_router, prefix="/api", tags=["Places"])
app.include_router(user_router, prefix="/api", tags=["Users"])
app.include_router(bids_router, prefix="/api", tags=["Bids"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(profile_router, prefix="/api", tags=["Profile"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])
app.include_router(blog_router, prefix="/api", tags=["Blog"])
app.include_router(password_reset_router, prefix="/api", tags=["Password Reset"])
app.include_router(company_router, prefix="/api", tags=["Company"])


app.mount("/static", StaticFiles(directory="static"), name="static")


register_tortoise(
    app,
    db_url="postgres://postgres:Ns290872erh@127.0.0.1:5432/makeasap",
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

if __name__ == "__main__":
    uvicorn.run(app, port=80)
