import pytest
import asyncio
import os
from httpx import AsyncClient
from tortoise import Tortoise
from models.user import User, Company
from models.actions import BlogArticle, Bid
from models.categories import Category, UnderCategory
from models.places import Country, City
from tortoise_config import TORTOISE_ORM
from faker import Faker

# Set test environment variable before importing app
os.environ["TESTING"] = "1"


fake = Faker()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def init_db():
    """Initialize database for testing"""
    # Use dev database (don't drop data)
    import copy
    test_config = copy.deepcopy(TORTOISE_ORM)

    # Initialize Tortoise
    try:
        await Tortoise.close_connections()
    except:
        pass  # Ignore if not initialized yet

    await Tortoise.init(config=test_config)
    await Tortoise.generate_schemas(safe=True)  # safe=True won't drop existing tables

    yield

    # Cleanup - just close connections, don't drop data
    await Tortoise.close_connections()


@pytest.fixture(scope="function")
async def client(init_db):
    """Create test client"""
    # Import app after DB is initialized to avoid conflicts
    from fastapi import FastAPI
    from api.admin import router as admin_router
    from api.bids import router as bids_router
    from api.blog import router as blog_router
    from api.categories import router as categories_get_router
    from api.chat import router as chat_router
    from api.password_reset import router as password_reset_router
    from api.profile import router as profile_router
    from api.user import router as user_router
    from api.company import router as company_router
    from routers.secur import router as jwt_router

    # Create test app without Tortoise registration
    test_app = FastAPI()
    test_app.include_router(jwt_router, prefix="", tags=["Auth"])
    test_app.include_router(categories_get_router, prefix="/check", tags=["Categories"])
    test_app.include_router(user_router, prefix="/api", tags=["Users"])
    test_app.include_router(bids_router, prefix="/api", tags=["Bids"])
    test_app.include_router(chat_router, prefix="/api", tags=["Chat"])
    test_app.include_router(profile_router, prefix="/api", tags=["Profile"])
    test_app.include_router(admin_router, prefix="/api", tags=["Admin"])
    test_app.include_router(blog_router, prefix="/api", tags=["Blog"])
    test_app.include_router(password_reset_router, prefix="/api", tags=["Password Reset"])
    test_app.include_router(company_router, prefix="/api", tags=["Company"])

    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_user(init_db):
    """Create a test user"""
    user = await User.create(
        name=fake.name(),
        email=fake.email(),
        password="hashed_password_123",
        role=0,  # Regular user
        user_role="user",
        city="Kyiv"
    )
    yield user
    await user.delete()


@pytest.fixture(scope="function")
async def test_admin(init_db):
    """Create a test admin user"""
    admin = await User.create(
        name="Admin User",
        email="admin@test.com",
        password="hashed_password_admin",
        role=1,  # Admin
        user_role="admin",
        city="Kyiv"
    )
    yield admin
    await admin.delete()


@pytest.fixture(scope="function")
async def test_company(init_db, test_user):
    """Create a test company"""
    company = await Company.create(
        name="Test Company",
        name_uk="Тестова компанія",
        name_en="Test Company",
        description_uk="Опис тестової компанії",
        description_en="Test company description",
        owner=test_user
    )
    yield company
    await company.delete()


@pytest.fixture(scope="function")
async def test_category(init_db):
    """Create a test category"""
    category = await Category.create(
        title_uk="Тестова категорія",
        title_en="Test Category",
        slug="test-category"
    )
    yield category
    await category.delete()


@pytest.fixture(scope="function")
async def test_subcategory(init_db, test_category):
    """Create a test subcategory"""
    subcategory = await UnderCategory.create(
        title_uk="Тестова підкатегорія",
        title_en="Test Subcategory",
        category=test_category
    )
    yield subcategory
    await subcategory.delete()


@pytest.fixture(scope="function")
async def test_country(init_db):
    """Create a test country"""
    country = await Country.create(
        name_uk="Україна",
        name_en="Ukraine",
        name_pl="Ukraina",
        code="UA"
    )
    yield country
    await country.delete()


@pytest.fixture(scope="function")
async def test_city(init_db, test_country):
    """Create a test city"""
    city = await City.create(
        name_uk="Київ",
        name_en="Kyiv",
        name_pl="Kijów",
        country=test_country
    )
    yield city
    await city.delete()


@pytest.fixture(scope="function")
async def test_bid(init_db, test_user):
    """Create a test bid"""
    bid = await Bid.create(
        title_uk="Тестова заявка",
        title_en="Test Bid",
        description_uk="Опис тестової заявки",
        description_en="Test bid description",
        budget="1000",
        author=test_user,
        delete_token="test_delete_token_123"
    )
    yield bid
    await bid.delete()


@pytest.fixture(scope="function")
async def test_blog_article(init_db, test_user):
    """Create a test blog article"""
    article = await BlogArticle.create(
        title_uk="Тестова стаття",
        title_en="Test Article",
        content_uk="Контент тестової статті",
        content_en="Test article content",
        description_uk="Опис",
        description_en="Description",
        slug_uk="testova-stattya",
        slug_en="test-article",
        author=test_user,
        is_published=True
    )
    yield article
    await article.delete()


@pytest.fixture(scope="function")
async def authenticated_client(client, test_user):
    """Create authenticated client with JWT token"""
    # Mock JWT token authentication
    # In a real scenario, you'd generate a valid JWT token
    client.headers.update({
        "Authorization": f"Bearer test_token_for_{test_user.id}"
    })
    yield client


@pytest.fixture(scope="function")
async def admin_client(client, test_admin):
    """Create authenticated admin client with JWT token"""
    client.headers.update({
        "Authorization": f"Bearer admin_token_for_{test_admin.id}"
    })
    yield client
