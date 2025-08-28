TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": "mydb",
                "host": "127.0.0.1",
                "user": "postgres",
                "password": "WordPass_!forPostgres_@",
                "port": 5432,
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
