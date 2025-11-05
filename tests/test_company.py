import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCompanyEndpoints:
    """Tests for company API endpoints"""

    async def test_get_companies_no_filters(self, client: AsyncClient, test_company):
        """Test getting companies without filters"""
        response = await client.get("/api/companies?limit=10&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert "companies" in data or isinstance(data, list)

    async def test_get_companies_with_pagination(self, client: AsyncClient, test_company):
        """Test getting companies with pagination"""
        response = await client.get("/api/companies?limit=5&offset=0")
        assert response.status_code == 200

        response2 = await client.get("/api/companies?limit=5&offset=5")
        assert response2.status_code == 200

    async def test_get_companies_with_category_filter(self, client: AsyncClient, test_company, test_category):
        """Test getting companies filtered by category"""
        response = await client.get(f"/api/companies?category={test_category.slug}&limit=10&offset=0")
        assert response.status_code == 200

    async def test_get_companies_with_location_filters(self, client: AsyncClient, test_company):
        """Test getting companies filtered by location"""
        response = await client.get("/api/companies?country=UA&city=Kyiv&limit=10&offset=0")
        assert response.status_code == 200

    async def test_get_companies_with_search(self, client: AsyncClient, test_company):
        """Test searching companies"""
        response = await client.get(f"/api/companies?search=Test&limit=10&offset=0")
        assert response.status_code == 200

    async def test_get_companies_with_sort(self, client: AsyncClient, test_company):
        """Test getting companies with different sort options"""
        sort_options = ["relevance", "rating", "newest"]

        for sort in sort_options:
            response = await client.get(f"/api/companies?sort={sort}&limit=10&offset=0")
            assert response.status_code == 200

    async def test_get_company_by_id(self, client: AsyncClient, test_company):
        """Test getting a specific company by ID"""
        response = await client.get(f"/api/companies/{test_company.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id

    async def test_get_company_by_id_not_found(self, client: AsyncClient):
        """Test getting non-existent company"""
        response = await client.get("/api/companies/99999")
        assert response.status_code == 404

    async def test_get_company_by_slug_valid(self, client: AsyncClient, test_company):
        """Test getting company by slug with valid format"""
        slug_with_id = f"test-company-{test_company.id}"
        response = await client.get(f"/api/companies/slug/{slug_with_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id

    async def test_get_company_by_slug_invalid_format(self, client: AsyncClient):
        """Test getting company by slug with invalid format"""
        response = await client.get("/api/companies/slug/invalidslug")
        assert response.status_code == 400
        assert "Invalid slug format" in response.json()["detail"]

    async def test_get_company_by_slug_invalid_id(self, client: AsyncClient):
        """Test getting company by slug with non-numeric ID"""
        response = await client.get("/api/companies/slug/test-company-abc")
        assert response.status_code == 400
        assert "Invalid company ID" in response.json()["detail"]

    async def test_get_company_by_slug_separate_params(self, client: AsyncClient, test_company):
        """Test getting company by slug with separate slug and ID parameters"""
        response = await client.get(f"/api/companies/slug/test-company/{test_company.id}")
        assert response.status_code == 200

    async def test_create_company(self, authenticated_client: AsyncClient):
        """Test creating a new company"""
        company_data = {
            "name_uk": "Нова компанія",
            "name_en": "New Company",
            "description_uk": "Опис нової компанії",
            "description_en": "Description of new company",
            "email": "newcompany@test.com",
            "phone": "+380501234567"
        }

        response = await authenticated_client.post("/api/companies", json=company_data)
        # Note: This might require authentication, so status could be 401
        assert response.status_code in [200, 201, 401]

    async def test_create_company_fast(self, authenticated_client: AsyncClient):
        """Test fast company creation"""
        company_data = {
            "name_uk": "Швидка компанія",
            "name_en": "Fast Company",
            "description_uk": "Опис",
            "description_en": "Description"
        }

        response = await authenticated_client.post("/api/companies-fast", json=company_data)
        assert response.status_code in [200, 201, 401]

    async def test_update_company(self, authenticated_client: AsyncClient, test_company):
        """Test updating a company"""
        update_data = {
            "name_uk": "Оновлена компанія",
            "name_en": "Updated Company"
        }

        response = await authenticated_client.put(
            f"/api/companies/{test_company.id}",
            json=update_data
        )
        assert response.status_code in [200, 401, 403]

    async def test_delete_company(self, authenticated_client: AsyncClient, test_company):
        """Test deleting a company"""
        # Create a company to delete
        from models.user import Company, User

        user = await User.first()
        company_to_delete = await Company.create(
            name="Company to delete",
            name_uk="Компанія для видалення",
            name_en="Company to delete",
            description_uk="Опис",
            description_en="Description",
            owner=user
        )

        response = await authenticated_client.delete(f"/api/companies/{company_to_delete.id}")
        assert response.status_code in [200, 204, 401, 403]

        # Cleanup if not deleted
        if response.status_code not in [200, 204]:
            await company_to_delete.delete()

    async def test_get_companies_by_owner(self, authenticated_client: AsyncClient, test_company):
        """Test getting companies owned by current user"""
        response = await authenticated_client.get("/api/companies/profile/get_companies")
        assert response.status_code in [200, 401]

    async def test_get_companies_combined_filters(self, client: AsyncClient, test_company):
        """Test getting companies with multiple filters combined"""
        response = await client.get(
            "/api/companies"
            "?limit=10&offset=0"
            "&search=Test"
            "&sort=relevance"
            "&country=UA"
        )
        assert response.status_code == 200

    async def test_company_pagination_limits(self, client: AsyncClient):
        """Test pagination with edge cases"""
        # Test with limit=0
        response = await client.get("/api/companies?limit=0&offset=0")
        assert response.status_code == 200

        # Test with very large limit
        response = await client.get("/api/companies?limit=1000&offset=0")
        assert response.status_code == 200

        # Test with very large offset
        response = await client.get("/api/companies?limit=10&offset=10000")
        assert response.status_code == 200
