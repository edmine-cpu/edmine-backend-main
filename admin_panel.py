"""
Admin Panel для всех моделей используя SQLAdmin
"""
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from slugify import slugify
from deep_translator import GoogleTranslator
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Подключение к базе данных через SQLAlchemy
DB_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE_URL = f"postgresql+asyncpg://postgres:{DB_PASSWORD}@0.0.0.0:5432/makeasap_dev"

# Создаем движок SQLAlchemy для админки
engine = create_async_engine(DATABASE_URL, echo=False)

Base = declarative_base()

# Вспомогательные функции для перевода и генерации slug
SUPPORTED_LANGUAGES = ['uk', 'en', 'pl', 'fr', 'de']

def generate_slug(text: str, lang: str = 'en') -> str:
    """Генерирует slug из текста"""
    if not text or not text.strip():
        return ""
    return slugify(text, max_length=128)

async def translate_field(text: str, source_lang: str, target_lang: str) -> str:
    """Переводит текст с одного языка на другой"""
    if not text or not text.strip() or source_lang == target_lang:
        return text

    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def detect_primary_language(data: dict, field_prefix: str = 'name') -> str:
    """Определяет основной язык по заполненным полям"""
    for lang in SUPPORTED_LANGUAGES:
        field_name = f"{field_prefix}_{lang}"
        if field_name in data and data[field_name] and str(data[field_name]).strip():
            return lang
    return 'uk'  # По умолчанию украинский

async def auto_translate_and_slug(data: dict, field_prefix: str = 'name', generate_slugs: bool = True):
    """Автоматически переводит поля и генерирует slug"""
    # Определяем основной язык
    primary_lang = detect_primary_language(data, field_prefix)
    primary_field = f"{field_prefix}_{primary_lang}"
    primary_text = data.get(primary_field, "")

    if not primary_text or not str(primary_text).strip():
        return data

    primary_text = str(primary_text).strip()

    # Переводим на все остальные языки
    tasks = []
    for lang in SUPPORTED_LANGUAGES:
        if lang != primary_lang:
            target_field = f"{field_prefix}_{lang}"
            # Переводим только если поле пустое
            if not data.get(target_field) or not str(data.get(target_field)).strip():
                task = translate_field(primary_text, primary_lang, lang)
                tasks.append((target_field, task))

    # Выполняем все переводы параллельно
    if tasks:
        translations = await asyncio.gather(*[task for _, task in tasks])
        for (field_name, _), translated_text in zip(tasks, translations):
            data[field_name] = translated_text

    # Генерируем slug для всех языков
    if generate_slugs:
        for lang in SUPPORTED_LANGUAGES:
            name_field = f"{field_prefix}_{lang}"
            slug_field = f"slug_{lang}"

            if name_field in data and data.get(name_field):
                text = str(data[name_field]).strip()
                if text:
                    data[slug_field] = generate_slug(text, lang)

    return data


class AdminAuth(AuthenticationBackend):
    """Простая аутентификация для админки"""

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        # Проверка логина и пароля
        if username == "test" and password == "test":
            # Устанавливаем флаг аутентификации в сессии
            request.session["admin_logged_in"] = True
            return True
        return False

    async def logout(self, request: Request) -> bool:
        # Очищаем сессию при выходе
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        # Проверяем, есть ли флаг аутентификации в сессии
        admin_logged_in = request.session.get("admin_logged_in", False)
        return admin_logged_in


# SQLAlchemy модели, отражающие структуру таблиц Tortoise ORM
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    email = Column(String(64), unique=True)
    city = Column(String(64))
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    password = Column(String(128))
    role = Column(Integer, default=0)
    language = Column(String(2), default='en')
    nickname = Column(String(64), nullable=True)
    avatar = Column(String(500), nullable=True)
    user_role = Column(String(20), default='customer')
    profile_description = Column(Text, nullable=True)
    slug_uk = Column(String(128), nullable=True)
    slug_en = Column(String(128), nullable=True)
    slug_pl = Column(String(128), nullable=True)
    slug_fr = Column(String(128), nullable=True)
    slug_de = Column(String(128), nullable=True)
    company_name_uk = Column(String(128), nullable=True)
    company_name_en = Column(String(128), nullable=True)
    company_name_pl = Column(String(128), nullable=True)
    company_name_fr = Column(String(128), nullable=True)
    company_name_de = Column(String(128), nullable=True)
    company_description_uk = Column(Text, nullable=True)
    company_description_en = Column(Text, nullable=True)
    company_description_pl = Column(Text, nullable=True)
    company_description_fr = Column(Text, nullable=True)
    company_description_de = Column(Text, nullable=True)
    auto_translated_fields = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    name_uk = Column(String(64), nullable=True)
    name_en = Column(String(64), nullable=True)
    name_pl = Column(String(64), nullable=True)
    name_fr = Column(String(64), nullable=True)
    name_de = Column(String(64), nullable=True)
    description_uk = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    description_pl = Column(Text, nullable=True)
    description_fr = Column(Text, nullable=True)
    description_de = Column(Text, nullable=True)
    slug_name = Column(String(64), nullable=True)
    slug_uk = Column(String(128), nullable=True)
    slug_en = Column(String(128), nullable=True)
    slug_pl = Column(String(128), nullable=True)
    slug_fr = Column(String(128), nullable=True)
    slug_de = Column(String(128), nullable=True)
    city = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    auto_translated_fields = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name_uk = Column(String(64))
    name_en = Column(String(64))
    name_pl = Column(String(64))
    name_fr = Column(String(64))
    name_de = Column(String(64))
    slug_uk = Column(String(128), nullable=True)
    slug_en = Column(String(128), nullable=True)
    slug_pl = Column(String(128), nullable=True)
    slug_fr = Column(String(128), nullable=True)
    slug_de = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name_uk = Column(String(64))
    name_en = Column(String(64))
    name_pl = Column(String(64))
    name_fr = Column(String(64))
    name_de = Column(String(64))
    slug_uk = Column(String(128), nullable=True)
    slug_en = Column(String(128), nullable=True)
    slug_pl = Column(String(128), nullable=True)
    slug_fr = Column(String(128), nullable=True)
    slug_de = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True)
    name_uk = Column(String(64))
    name_en = Column(String(64))
    name_pl = Column(String(64))
    name_fr = Column(String(64), nullable=True)
    name_de = Column(String(64), nullable=True)
    slug_uk = Column(String(128), nullable=True)
    slug_en = Column(String(128), nullable=True)
    slug_pl = Column(String(128), nullable=True)
    slug_fr = Column(String(128), nullable=True)
    slug_de = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class UnderCategory(Base):
    __tablename__ = "undercategory"

    id = Column(Integer, primary_key=True)
    name_uk = Column(String(64), nullable=True)
    name_en = Column(String(64), nullable=True)
    name_pl = Column(String(64), nullable=True)
    name_fr = Column(String(64), nullable=True)
    name_de = Column(String(64), nullable=True)
    slug_uk = Column(String(128), nullable=True)
    slug_en = Column(String(128), nullable=True)
    slug_pl = Column(String(128), nullable=True)
    slug_fr = Column(String(128), nullable=True)
    slug_de = Column(String(128), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True)
    title_uk = Column(String(128), nullable=True)
    title_en = Column(String(128), nullable=True)
    title_pl = Column(String(128), nullable=True)
    title_fr = Column(String(128), nullable=True)
    title_de = Column(String(128), nullable=True)
    slug_uk = Column(String(256), nullable=True)
    slug_en = Column(String(256), nullable=True)
    slug_pl = Column(String(256), nullable=True)
    slug_fr = Column(String(256), nullable=True)
    slug_de = Column(String(256), nullable=True)
    main_language = Column(String(2), default='en', nullable=True)
    categories = Column(JSON, nullable=True)
    under_categories = Column(JSON, nullable=True)
    description_uk = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    description_pl = Column(Text, nullable=True)
    description_fr = Column(Text, nullable=True)
    description_de = Column(Text, nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    budget = Column(String(32), nullable=True)
    budget_type = Column(String(8), nullable=True)
    files = Column(JSON, nullable=True)
    auto_translated_fields = Column(JSON, nullable=True)
    delete_token = Column(String(64), unique=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class BlogArticle(Base):
    __tablename__ = "blog_articles"

    id = Column(Integer, primary_key=True)
    title_uk = Column(String(256))
    title_en = Column(String(256), nullable=True)
    title_pl = Column(String(256), nullable=True)
    title_fr = Column(String(256), nullable=True)
    title_de = Column(String(256), nullable=True)
    slug_uk = Column(String(300), nullable=True)
    slug_en = Column(String(300), nullable=True)
    slug_pl = Column(String(300), nullable=True)
    slug_fr = Column(String(300), nullable=True)
    slug_de = Column(String(300), nullable=True)
    content_uk = Column(Text)
    content_en = Column(Text, nullable=True)
    content_pl = Column(Text, nullable=True)
    content_fr = Column(Text, nullable=True)
    content_de = Column(Text, nullable=True)
    description_uk = Column(String(300), nullable=True)
    description_en = Column(String(300), nullable=True)
    description_pl = Column(String(300), nullable=True)
    description_fr = Column(String(300), nullable=True)
    description_de = Column(String(300), nullable=True)
    keywords_uk = Column(String(500), nullable=True)
    keywords_en = Column(String(500), nullable=True)
    keywords_pl = Column(String(500), nullable=True)
    keywords_fr = Column(String(500), nullable=True)
    keywords_de = Column(String(500), nullable=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Автор статьи (необязательно)
    is_published = Column(Boolean, default=False)
    auto_translated_fields = Column(JSON, nullable=True)
    featured_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), default=func.now())


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    token = Column(String(255), unique=True)
    code = Column(String(6))
    created_at = Column(DateTime, server_default=func.now(), default=func.now())
    expires_at = Column(DateTime, nullable=True)
    is_used = Column(Boolean, default=False)


# ModelView для каждой таблицы
class UserAdmin(ModelView, model=User):
    """Администрирование пользователей"""
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        User.id, User.name, User.email, User.city, User.role,
        User.user_role, User.nickname, User.created_at
    ]
    column_searchable_list = [User.name, User.email, User.nickname]
    column_sortable_list = [User.id, User.name, User.email, User.created_at]
    column_default_sort = [(User.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        User.name, User.email, User.city, User.password, User.role,
        User.nickname, User.user_role, User.profile_description,
        User.language, User.avatar
    ]

    page_size = 50
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class CompanyAdmin(ModelView, model=Company):
    """Администрирование компаний"""
    name = "Company"
    name_plural = "Companies"
    icon = "fa-solid fa-building"

    column_list = [Company.id, Company.name, Company.slug_name, Company.city, Company.country, Company.created_at]
    column_searchable_list = [Company.name, Company.name_uk, Company.name_en]
    column_sortable_list = [Company.id, Company.name, Company.created_at]
    column_default_sort = [(Company.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        Company.name, Company.name_uk, Company.name_en, Company.name_pl, Company.name_fr, Company.name_de,
        Company.description_uk, Company.description_en, Company.description_pl, Company.description_fr, Company.description_de,
        Company.slug_name, Company.slug_uk, Company.slug_en, Company.slug_pl, Company.slug_fr, Company.slug_de,
        Company.city, Company.country
    ]

    page_size = 50
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        """Автоматический перевод и генерация slug перед сохранением"""
        # Переводим name полям
        await auto_translate_and_slug(data, field_prefix='name', generate_slugs=True)
        # Переводим description поля (без slug)
        await auto_translate_and_slug(data, field_prefix='description', generate_slugs=False)


class CountryAdmin(ModelView, model=Country):
    """Администрирование стран"""
    name = "Country"
    name_plural = "Countries"
    icon = "fa-solid fa-globe"

    column_list = [Country.id, Country.name_uk, Country.name_en, Country.name_pl, Country.created_at]
    column_searchable_list = [Country.name_uk, Country.name_en, Country.name_pl]
    column_sortable_list = [Country.id, Country.name_en, Country.created_at]
    column_default_sort = [(Country.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        Country.name_uk, Country.name_en, Country.name_pl, Country.name_fr, Country.name_de,
        Country.slug_uk, Country.slug_en, Country.slug_pl, Country.slug_fr, Country.slug_de
    ]

    page_size = 100
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        """Автоматический перевод и генерация slug перед сохранением"""
        await auto_translate_and_slug(data, field_prefix='name', generate_slugs=True)


class CityAdmin(ModelView, model=City):
    """Администрирование городов"""
    name = "City"
    name_plural = "Cities"
    icon = "fa-solid fa-city"

    column_list = [City.id, City.name_uk, City.name_en, City.name_pl, City.created_at]
    column_searchable_list = [City.name_uk, City.name_en, City.name_pl]
    column_sortable_list = [City.id, City.name_en, City.created_at]
    column_default_sort = [(City.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        City.name_uk, City.name_en, City.name_pl, City.name_fr, City.name_de,
        City.slug_uk, City.slug_en, City.slug_pl, City.slug_fr, City.slug_de
    ]

    page_size = 100
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        """Автоматический перевод и генерация slug перед сохранением"""
        await auto_translate_and_slug(data, field_prefix='name', generate_slugs=True)


class CategoryAdmin(ModelView, model=Category):
    """Администрирование категорий"""
    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-tags"

    column_list = [Category.id, Category.name, Category.name_uk, Category.name_en, Category.created_at]
    column_searchable_list = [Category.name, Category.name_uk, Category.name_en]
    column_sortable_list = [Category.id, Category.name, Category.created_at]
    column_default_sort = [(Category.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        Category.name, Category.name_uk, Category.name_en, Category.name_pl, Category.name_fr, Category.name_de,
        Category.slug_uk, Category.slug_en, Category.slug_pl, Category.slug_fr, Category.slug_de
    ]

    page_size = 50
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        """Автоматический перевод и генерация slug перед сохранением"""
        await auto_translate_and_slug(data, field_prefix='name', generate_slugs=True)


class UnderCategoryAdmin(ModelView, model=UnderCategory):
    """Администрирование подкатегорий"""
    name = "UnderCategory"
    name_plural = "UnderCategories"
    icon = "fa-solid fa-tag"

    column_list = [UnderCategory.id, UnderCategory.name_uk, UnderCategory.name_en, UnderCategory.created_at]
    column_searchable_list = [UnderCategory.name_uk, UnderCategory.name_en]
    column_sortable_list = [UnderCategory.id, UnderCategory.name_uk, UnderCategory.created_at]
    column_default_sort = [(UnderCategory.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        UnderCategory.name_uk, UnderCategory.name_en, UnderCategory.name_pl, UnderCategory.name_fr, UnderCategory.name_de,
        UnderCategory.slug_uk, UnderCategory.slug_en, UnderCategory.slug_pl, UnderCategory.slug_fr, UnderCategory.slug_de
    ]

    page_size = 50
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        """Автоматический перевод и генерация slug перед сохранением"""
        await auto_translate_and_slug(data, field_prefix='name', generate_slugs=True)


class BidAdmin(ModelView, model=Bid):
    """Администрирование заявок"""
    name = "Bid"
    name_plural = "Bids"
    icon = "fa-solid fa-file-contract"

    column_list = [
        Bid.id, Bid.title_uk, Bid.title_en, Bid.budget,
        Bid.budget_type, Bid.main_language, Bid.created_at
    ]
    column_searchable_list = [Bid.title_uk, Bid.title_en, Bid.title_pl]
    column_sortable_list = [Bid.id, Bid.title_uk, Bid.budget, Bid.created_at]
    column_default_sort = [(Bid.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        Bid.title_uk, Bid.title_en, Bid.title_pl, Bid.title_fr, Bid.title_de,
        Bid.slug_uk, Bid.slug_en, Bid.slug_pl, Bid.slug_fr, Bid.slug_de,
        Bid.description_uk, Bid.description_en, Bid.description_pl, Bid.description_fr, Bid.description_de,
        Bid.main_language, Bid.budget, Bid.budget_type,
        Bid.categories, Bid.under_categories, Bid.files,
        Bid.delete_token
    ]

    page_size = 50
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        """Автоматический перевод и генерация slug перед сохранением"""
        # Переводим title поля
        await auto_translate_and_slug(data, field_prefix='title', generate_slugs=True)
        # Переводим description поля (без slug)
        await auto_translate_and_slug(data, field_prefix='description', generate_slugs=False)


class BlogArticleAdmin(ModelView, model=BlogArticle):
    """Администрирование статей блога"""
    name = "BlogArticle"
    name_plural = "Blog Articles"
    icon = "fa-solid fa-newspaper"

    column_list = [
        BlogArticle.id, BlogArticle.title_uk, BlogArticle.title_en,
        BlogArticle.is_published, BlogArticle.created_at
    ]
    column_searchable_list = [BlogArticle.title_uk, BlogArticle.title_en]
    column_sortable_list = [BlogArticle.id, BlogArticle.title_uk, BlogArticle.is_published, BlogArticle.created_at]
    column_default_sort = [(BlogArticle.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [
        BlogArticle.title_uk, BlogArticle.title_en, BlogArticle.title_pl, BlogArticle.title_fr, BlogArticle.title_de,
        BlogArticle.slug_uk, BlogArticle.slug_en, BlogArticle.slug_pl, BlogArticle.slug_fr, BlogArticle.slug_de,
        BlogArticle.content_uk, BlogArticle.content_en, BlogArticle.content_pl, BlogArticle.content_fr, BlogArticle.content_de,
        BlogArticle.description_uk, BlogArticle.description_en, BlogArticle.description_pl, BlogArticle.description_fr, BlogArticle.description_de,
        BlogArticle.keywords_uk, BlogArticle.keywords_en, BlogArticle.keywords_pl, BlogArticle.keywords_fr, BlogArticle.keywords_de,
        BlogArticle.author_id, BlogArticle.is_published, BlogArticle.featured_image
    ]

    page_size = 30
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    async def on_model_change(self, data: dict, model, is_created: bool, request: Request) -> None:
        """Автоматический перевод и генерация slug перед сохранением"""
        # Переводим title поля
        await auto_translate_and_slug(data, field_prefix='title', generate_slugs=True)
        # Переводим content поля (без slug)
        await auto_translate_and_slug(data, field_prefix='content', generate_slugs=False)
        # Переводим description поля (без slug)
        await auto_translate_and_slug(data, field_prefix='description', generate_slugs=False)
        # Переводим keywords поля (без slug)
        await auto_translate_and_slug(data, field_prefix='keywords', generate_slugs=False)


class PasswordResetTokenAdmin(ModelView, model=PasswordResetToken):
    """Администрирование токенов сброса пароля"""
    name = "PasswordResetToken"
    name_plural = "Password Reset Tokens"
    icon = "fa-solid fa-key"

    column_list = [PasswordResetToken.id, PasswordResetToken.token, PasswordResetToken.code,
                   PasswordResetToken.is_used, PasswordResetToken.expires_at, PasswordResetToken.created_at]
    column_searchable_list = [PasswordResetToken.token, PasswordResetToken.code]
    column_sortable_list = [PasswordResetToken.id, PasswordResetToken.is_used, PasswordResetToken.created_at]
    column_default_sort = [(PasswordResetToken.id, False)]  # Сортировка по ID по возрастанию

    form_columns = [PasswordResetToken.token, PasswordResetToken.code, PasswordResetToken.is_used, PasswordResetToken.expires_at]

    page_size = 50
    can_create = False
    can_edit = True
    can_delete = True
    can_view_details = True


def setup_admin(app):
    """Настройка и регистрация админки"""

    # Создаем админку с аутентификацией
    admin = Admin(
        app=app,
        engine=engine,
        title="Admin Panel",
        authentication_backend=AdminAuth(secret_key="your-secret-key-here"),
        base_url="/admin"
    )

    # Регистрируем все ModelView
    admin.add_view(UserAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(CountryAdmin)
    admin.add_view(CityAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(UnderCategoryAdmin)
    admin.add_view(BidAdmin)
    admin.add_view(BlogArticleAdmin)
    admin.add_view(PasswordResetTokenAdmin)

    return admin
