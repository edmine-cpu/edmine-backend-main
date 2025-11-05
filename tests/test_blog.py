import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestBlogEndpoints:
    """Tests for blog API endpoints"""

    async def test_get_blog_articles_default_params(self, client: AsyncClient, test_blog_article):
        """Test getting blog articles with default parameters"""
        response = await client.get("/api/blog/articles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check article structure
        article = data[0]
        assert "id" in article
        assert "title" in article
        assert "description" in article
        assert "slug" in article
        assert "featured_image" in article
        assert "author_name" in article
        assert "created_at" in article
        assert "updated_at" in article

    async def test_get_blog_articles_with_language(self, client: AsyncClient, test_blog_article):
        """Test getting blog articles with different languages"""
        languages = ["uk", "en", "pl", "fr", "de"]

        for lang in languages:
            response = await client.get(f"/api/blog/articles?lang={lang}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    async def test_get_blog_articles_invalid_language(self, client: AsyncClient):
        """Test getting blog articles with invalid language"""
        response = await client.get("/api/blog/articles?lang=invalid")
        assert response.status_code == 400
        assert "Unsupported language" in response.json()["detail"]

    async def test_get_blog_articles_with_pagination(self, client: AsyncClient, test_blog_article):
        """Test getting blog articles with pagination"""
        response = await client.get("/api/blog/articles?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    async def test_get_blog_article_by_id(self, client: AsyncClient, test_blog_article):
        """Test getting a specific blog article by ID"""
        response = await client.get(f"/api/blog/articles/{test_blog_article.id}")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == test_blog_article.id
        assert "title" in data
        assert "content" in data
        assert "description" in data
        assert "keywords" in data
        assert "slug" in data
        assert "featured_image" in data
        assert "author_name" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_get_blog_article_by_id_with_language(self, client: AsyncClient, test_blog_article):
        """Test getting a blog article by ID with different languages"""
        for lang in ["uk", "en"]:
            response = await client.get(f"/api/blog/articles/{test_blog_article.id}?lang={lang}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == test_blog_article.id

    async def test_get_blog_article_not_found(self, client: AsyncClient):
        """Test getting a non-existent blog article"""
        response = await client.get("/api/blog/articles/99999")
        assert response.status_code == 404
        assert "Article not found" in response.json()["detail"]

    async def test_get_blog_article_invalid_language(self, client: AsyncClient, test_blog_article):
        """Test getting a blog article with invalid language"""
        response = await client.get(f"/api/blog/articles/{test_blog_article.id}?lang=xyz")
        assert response.status_code == 400
        assert "Unsupported language" in response.json()["detail"]

    async def test_blog_article_only_published(self, client: AsyncClient, test_blog_article, test_user):
        """Test that only published articles are returned"""
        from models.actions import BlogArticle

        # Create unpublished article
        unpublished = await BlogArticle.create(
            title_uk="Непублікована",
            title_en="Unpublished",
            content_uk="Контент",
            content_en="Content",
            description_uk="Опис",
            description_en="Description",
            slug_uk="unpublished",
            slug_en="unpublished",
            author=test_user,
            is_published=False
        )

        # Get all articles
        response = await client.get("/api/blog/articles")
        assert response.status_code == 200
        data = response.json()

        # Check that unpublished article is not in the list
        article_ids = [article["id"] for article in data]
        assert unpublished.id not in article_ids
        assert test_blog_article.id in article_ids

        # Cleanup
        await unpublished.delete()

    async def test_get_unpublished_article_by_id(self, client: AsyncClient, test_user):
        """Test that unpublished article cannot be retrieved by ID"""
        from models.actions import BlogArticle

        unpublished = await BlogArticle.create(
            title_uk="Непублікована",
            title_en="Unpublished",
            content_uk="Контент",
            content_en="Content",
            description_uk="Опис",
            description_en="Description",
            slug_uk="unpublished",
            slug_en="unpublished",
            author=test_user,
            is_published=False
        )

        response = await client.get(f"/api/blog/articles/{unpublished.id}")
        assert response.status_code == 404

        await unpublished.delete()
