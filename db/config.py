from settings import settings

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": settings.DB_NAME,
                "host": settings.DB_HOST,
                "user": settings.DB_USER,
                "password": settings.DB_PASSWORD,
                "port": settings.DB_PORT,
            }
        }
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    }
}
