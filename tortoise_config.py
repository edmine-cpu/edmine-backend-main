TORTOISE_ORM = {
    "connections": {
        "default": "postgres://postgres:WordPass_!forPostgres_%40@127.0.0.1:5432/makeasap_dev"
    },
    "apps": {
        "models": {
            "models": [
                "models",
                "aerich.models"
            ],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC"
}
