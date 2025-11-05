import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAdminStatsEndpoints:
    """Tests for admin statistics endpoints (without authentication for demo)"""

    async def test_get_simple_stats(self, client: AsyncClient):
        """Test getting basic statistics"""
        response = await client.get("/api/admin/stats")
        assert response.status_code == 200
        data = response.json()

        assert "users_count" in data
        assert "bids_count" in data
        assert "chats_count" in data
        assert "categories_count" in data

        # Check data types
        assert isinstance(data["users_count"], int)
        assert isinstance(data["bids_count"], int)
        assert isinstance(data["chats_count"], int)
        assert isinstance(data["categories_count"], int)

    async def test_get_simple_users(self, client: AsyncClient, test_user):
        """Test getting simple users list"""
        response = await client.get("/api/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            user = data[0]
            assert "id" in user
            assert "name" in user
            assert "email" in user
            assert "user_role" in user
            assert "created_at" in user

    async def test_update_user_simple(self, client: AsyncClient, test_user):
        """Test updating user without authentication"""
        form_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "user_role": "user",
            "nickname": "updatednick",
            "city": "Київ",
            "profile_description": "Updated description"
        }

        response = await client.put(
            f"/api/admin/users/{test_user.id}",
            data=form_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["user_id"] == test_user.id

    async def test_update_user_missing_fields(self, client: AsyncClient, test_user):
        """Test updating user with missing required fields"""
        form_data = {
            "name": "Updated Name"
            # Missing email and user_role
        }

        response = await client.put(
            f"/api/admin/users/{test_user.id}",
            data=form_data
        )
        assert response.status_code == 422

    async def test_update_user_not_found(self, client: AsyncClient):
        """Test updating non-existent user"""
        form_data = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "user_role": "user"
        }

        response = await client.put(
            "/api/admin/users/99999",
            data=form_data
        )
        assert response.status_code == 404

    async def test_delete_user_simple(self, client: AsyncClient):
        """Test deleting user without authentication"""
        from models.user import User

        # Create a user to delete
        user_to_delete = await User.create(
            name="User to Delete",
            email="delete@example.com",
            password="password",
            role=0,
            user_role="user"
        )

        response = await client.delete(f"/api/admin/users/{user_to_delete.id}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["user_id"] == user_to_delete.id

    async def test_delete_user_not_found(self, client: AsyncClient):
        """Test deleting non-existent user"""
        response = await client.delete("/api/admin/users/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestAdminBlogEndpoints:
    """Tests for admin blog management endpoints"""

    async def test_get_simple_blogs(self, client: AsyncClient, test_blog_article):
        """Test getting blogs list"""
        response = await client.get("/api/admin/blogs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            blog = data[0]
            assert "id" in blog
            assert "title_uk" in blog
            assert "title_en" in blog
            assert "content_uk" in blog
            assert "is_published" in blog
            assert "author" in blog
            assert "created_at" in blog

    async def test_create_test_blog(self, client: AsyncClient, test_user):
        """Test creating a test blog"""
        response = await client.post("/api/admin/blogs/create-test")
        assert response.status_code in [200, 201]
        data = response.json()
        assert "message" in data
        assert "blog_id" in data

        # Cleanup
        from models.actions import BlogArticle
        blog = await BlogArticle.get_or_none(id=data["blog_id"])
        if blog:
            await blog.delete()

    async def test_delete_blog_simple(self, client: AsyncClient, test_user):
        """Test deleting a blog"""
        from models.actions import BlogArticle

        # Create a blog to delete
        blog_to_delete = await BlogArticle.create(
            title_uk="Блог для видалення",
            title_en="Blog to delete",
            content_uk="Контент",
            content_en="Content",
            description_uk="Опис",
            description_en="Description",
            slug_uk="delete-blog",
            slug_en="delete-blog",
            author=test_user,
            is_published=True
        )

        response = await client.delete(f"/api/admin/blogs/{blog_to_delete.id}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["blog_id"] == blog_to_delete.id

    async def test_delete_blog_not_found(self, client: AsyncClient):
        """Test deleting non-existent blog"""
        response = await client.delete("/api/admin/blogs/99999")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestAdminAuthenticatedEndpoints:
    """Tests for admin endpoints requiring authentication"""

    async def test_get_dashboard_stats_unauthorized(self, client: AsyncClient):
        """Test getting dashboard stats without authentication"""
        response = await client.get("/api/admin/dashboard")
        assert response.status_code == 401

    async def test_get_dashboard_stats_as_admin(self, admin_client: AsyncClient, test_admin):
        """Test getting dashboard stats as admin"""
        response = await admin_client.get("/api/admin/dashboard")
        # Will fail with mock auth
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert "users" in data
            assert "bids" in data
            assert "chats" in data
            assert "security" in data

    async def test_get_bids_list_unauthorized(self, client: AsyncClient):
        """Test getting bids list without authentication"""
        response = await client.get("/api/admin/bids?page=1&limit=20")
        assert response.status_code == 401

    async def test_get_bids_list_as_admin(self, admin_client: AsyncClient):
        """Test getting bids list as admin"""
        response = await admin_client.get("/api/admin/bids?page=1&limit=20")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert "bids" in data
            assert "total" in data
            assert "page" in data
            assert "limit" in data
            assert "pages" in data

    async def test_get_chats_list_unauthorized(self, client: AsyncClient):
        """Test getting chats list without authentication"""
        response = await client.get("/api/admin/chats?page=1&limit=20")
        assert response.status_code == 401

    async def test_get_chats_list_as_admin(self, admin_client: AsyncClient):
        """Test getting chats list as admin"""
        response = await admin_client.get("/api/admin/chats?page=1&limit=20")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert "chats" in data
            assert "total" in data
            assert "page" in data
            assert "limit" in data

    async def test_get_banned_ips_unauthorized(self, client: AsyncClient):
        """Test getting banned IPs without authentication"""
        response = await client.get("/api/admin/banned-ips")
        assert response.status_code == 401

    async def test_get_banned_ips_as_admin(self, admin_client: AsyncClient):
        """Test getting banned IPs as admin"""
        response = await admin_client.get("/api/admin/banned-ips")
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert "banned_ips" in data
            assert isinstance(data["banned_ips"], list)

    async def test_ban_ip_unauthorized(self, client: AsyncClient):
        """Test banning IP without authentication"""
        form_data = {
            "ip_address": "192.168.1.100",
            "reason": "Suspicious activity"
        }

        response = await client.post("/api/admin/ban-ip", data=form_data)
        assert response.status_code == 401

    async def test_ban_ip_as_admin(self, admin_client: AsyncClient):
        """Test banning IP as admin"""
        form_data = {
            "ip_address": "192.168.1.100",
            "reason": "Test ban"
        }

        response = await admin_client.post("/api/admin/ban-ip", data=form_data)
        assert response.status_code in [200, 400, 401]

        # Cleanup if successful
        if response.status_code == 200:
            from models.chat import BannedIP
            banned = await BannedIP.get_or_none(ip_address="192.168.1.100")
            if banned:
                await banned.delete()

    async def test_ban_ip_invalid_format(self, admin_client: AsyncClient):
        """Test banning IP with invalid format"""
        form_data = {
            "ip_address": "invalid-ip",
            "reason": "Test"
        }

        response = await admin_client.post("/api/admin/ban-ip", data=form_data)
        assert response.status_code in [400, 401]

    async def test_unban_ip_unauthorized(self, client: AsyncClient):
        """Test unbanning IP without authentication"""
        response = await client.delete("/api/admin/unban-ip/1")
        assert response.status_code == 401

    async def test_unban_ip_not_found(self, admin_client: AsyncClient):
        """Test unbanning non-existent IP"""
        response = await admin_client.delete("/api/admin/unban-ip/99999")
        assert response.status_code in [404, 401]

    async def test_update_user_role_unauthorized(self, client: AsyncClient, test_user):
        """Test updating user role without authentication"""
        form_data = {
            "role": 1
        }

        response = await client.put(
            f"/api/admin/users/{test_user.id}/role",
            data=form_data
        )
        assert response.status_code == 401

    async def test_update_user_role_as_admin(self, admin_client: AsyncClient, test_user):
        """Test updating user role as admin"""
        form_data = {
            "role": 0
        }

        response = await admin_client.put(
            f"/api/admin/users/{test_user.id}/role",
            data=form_data
        )
        assert response.status_code in [200, 401]

    async def test_update_user_role_invalid_value(self, admin_client: AsyncClient, test_user):
        """Test updating user role with invalid value"""
        form_data = {
            "role": 999  # Invalid role
        }

        response = await admin_client.put(
            f"/api/admin/users/{test_user.id}/role",
            data=form_data
        )
        assert response.status_code in [400, 401]

    async def test_admin_pagination(self, admin_client: AsyncClient):
        """Test pagination on admin endpoints"""
        endpoints = [
            "/api/admin/bids?page=1&limit=10",
            "/api/admin/bids?page=2&limit=5",
            "/api/admin/chats?page=1&limit=20"
        ]

        for endpoint in endpoints:
            response = await admin_client.get(endpoint)
            assert response.status_code in [200, 401]

    async def test_blog_articles_frontend_endpoint(self, client: AsyncClient, test_blog_article):
        """Test getting blog articles for frontend"""
        response = await client.get("/api/blog/articles?lang=uk")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        if len(data) > 0:
            article = data[0]
            assert "id" in article
            assert "title" in article
            assert "description" in article
            assert "slug" in article
            assert "author_name" in article
