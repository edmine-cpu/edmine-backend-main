from contextlib import asynccontextmanager
from tortoise import Tortoise
from settings import settings

DATABASE_MODULES = ["models"]

JWT_SECRET_KEY = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES
JWT_COOKIE_NAME = settings.JWT_COOKIE_NAME

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SENDER_EMAIL = settings.SENDER_EMAIL
SENDER_PASSWORD = settings.SENDER_PASSWORD
CODE_RESEND_INTERVAL = 60
VERIFICATION_CODE_LENGTH = 6

MAX_FILES_COUNT = 10
ALLOWED_FILE_TYPES = {
    'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml',
    'application/pdf', 'image/bmp', 'image/gif'
}
TEMP_FILES_DIR = 'static/tmp_files'
BID_FILES_DIR = 'static/bid_files'
DELETE_TOKEN_LENGTH = 32

USER_ROLE_EXECUTOR = 'executor'
USER_ROLE_CUSTOMER = 'customer'
DEFAULT_USER_ROLE = USER_ROLE_EXECUTOR

MIN_PASSWORD_LENGTH = 8
BCRYPT_ROUNDS = 12

APP_TITLE = "FreelanceBirja"
APP_DESCRIPTION = "Біржа послуг та виконавців"
APP_VERSION = "1.0.0"
APP_HOST = "0.0.0.0"
APP_PORT = 8000

TEMPLATES_DIR = 'templates'
STATIC_DIR = 'static'

API_PREFIX = '/api'

SORT_OPTIONS = ['newest', 'oldest']
DEFAULT_SORT_ORDER = 'newest'


@asynccontextmanager
async def lifespan(app):
    await Tortoise.init(
        db_url=await settings.database_url,
        modules={'models': DATABASE_MODULES}
    )
    await Tortoise.generate_schemas()
    
    yield
    
    await Tortoise.close_connections()


INITIAL_CATEGORIES = [
    {'name': 'plumbing', 'name_uk': 'Сантехніка'},
    {'name': 'electrical', 'name_uk': 'Електрика'},
    {'name': 'repair', 'name_uk': 'Ремонт'},
    {'name': 'cleaning', 'name_uk': 'Прибирання'},
    {'name': 'other', 'name_uk': 'Інше'}
]

UKRAINIAN_CITIES = [
    'Київ', 'Харків', 'Одеса', 'Дніпро', 'Донецьк', 'Запоріжжя', 'Львів',
    'Кривий Ріг', 'Миколаїв', 'Маріуполь', 'Луганськ', 'Вінниця', 'Херсон',
    'Полтава', 'Чернігів', 'Черкаси', 'Хмельницький', 'Житомир', 'Суми',
    'Рівне', 'Івано-Франківськ', 'Тернопіль', 'Луцьк', 'Ужгород',
    'Кам\'янець-Подільський', 'Дрогобич', 'Біла Церква', 'Нікополь',
    'Бердянськ', 'Павлоград', 'Кременчук', 'Мелітополь', 'Керч',
    'Краматорськ', 'Слов\'янськ', 'Бровари', 'Ірпінь', 'Буча'
]