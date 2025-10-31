from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения с чтением из .env файла"""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    # Database settings
    DB_HOST: str = Field(default="localhost", description="PostgreSQL хост")
    DB_PORT: int = Field(default=5432, description="PostgreSQL порт")
    DB_USER: str = Field(default="postgres", description="PostgreSQL пользователь")
    DB_PASSWORD: str = Field(description="PostgreSQL пароль")
    DB_NAME: str = Field(default="makeasap_dev", description="Имя базы данных")

    # JWT settings
    JWT_SECRET: str = Field(description="Секретный ключ для JWT")
    JWT_ALGORITHM: str = Field(default="HS256", description="Алгоритм JWT")
    JWT_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, description="Время жизни JWT токена в минутах")
    JWT_COOKIE_NAME: str = Field(default="jwt_token", description="Имя cookie для JWT")

    # Session settings
    SESSION_SECRET_KEY: str = Field(description="Секретный ключ для сессий")

    # SMTP settings
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP хост")
    SMTP_PORT: int = Field(default=465, description="SMTP порт")
    SENDER_EMAIL: str = Field(description="Email отправителя")
    SENDER_PASSWORD: str = Field(description="Пароль SMTP")

    # App settings
    APP_HOST: str = Field(default="0.0.0.0", description="Хост приложения")
    APP_PORT: int = Field(default=8000, description="Порт приложения")
    DEBUG: bool = Field(default=False, description="Режим отладки")

    @property
    def database_url(self) -> str:
        """Генерирует URL для подключения к БД в формате Tortoise ORM"""
        return f"postgres://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_asyncpg(self) -> str:
        """Генерирует URL для подключения к БД в формате asyncpg"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Глобальный экземпляр настроек
settings = Settings()
