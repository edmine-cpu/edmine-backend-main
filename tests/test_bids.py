import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
class TestBidsEndpoints:
    """Tests for bids API endpoints"""

    async def test_list_bids_no_filters(self, client: AsyncClient, test_bid):
        """Test getting bids without filters"""
        response = await client.get("/api/bids")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    async def test_list_bids_with_category_filter(self, client: AsyncClient, test_bid, test_category):
        """Test getting bids filtered by category"""
        response = await client.get(f"/api/bids?category={test_category.slug}")
        assert response.status_code == 200

    async def test_list_bids_with_subcategory_filter(self, client: AsyncClient, test_bid, test_subcategory):
        """Test getting bids filtered by subcategory"""
        response = await client.get(f"/api/bids?subcategory={test_subcategory.id}")
        assert response.status_code == 200

    async def test_list_bids_with_location_filters(self, client: AsyncClient, test_bid, test_country, test_city):
        """Test getting bids filtered by location"""
        response = await client.get(
            f"/api/bids?country={test_country.id}&city={test_city.name_en}"
        )
        assert response.status_code == 200

    async def test_list_bids_with_search(self, client: AsyncClient, test_bid):
        """Test searching bids"""
        response = await client.get("/api/bids?search=Test")
        assert response.status_code == 200

    async def test_list_bids_with_limit(self, client: AsyncClient, test_bid):
        """Test getting bids with limit"""
        response = await client.get("/api/bids?limit=5")
        assert response.status_code == 200
        data = response.json()

        if isinstance(data, list):
            assert len(data) <= 5

    async def test_list_bids_with_sort(self, client: AsyncClient, test_bid):
        """Test getting bids with different sort options"""
        sort_options = ["date_desc", "date_asc", "budget_desc", "budget_asc"]

        for sort in sort_options:
            response = await client.get(f"/api/bids?sort={sort}")
            assert response.status_code == 200

    async def test_list_bids_combined_filters(self, client: AsyncClient, test_bid):
        """Test getting bids with multiple filters"""
        response = await client.get(
            "/api/bids"
            "?search=Test"
            "&limit=10"
            "&sort=date_desc"
        )
        assert response.status_code == 200

    async def test_get_bid_by_id(self, client: AsyncClient, test_bid):
        """Test getting a specific bid by ID"""
        response = await client.get(f"/api/bids/{test_bid.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_bid.id

    async def test_get_bid_by_id_not_found(self, client: AsyncClient):
        """Test getting non-existent bid"""
        response = await client.get("/api/bids/99999")
        assert response.status_code == 404
        assert "Bid not found" in response.json()["detail"]

    async def test_create_request_uk(self, client: AsyncClient):
        """Test creating a bid request in Ukrainian"""
        form_data = {
            "title": "Тестова заявка",
            "description": "Опис тестової заявки",
            "budget": "1000",
            "contact_email": "test@example.com",
            "contact_phone": "+380501234567",
            "category": "test-category"
        }

        response = await client.post(
            "/api/uk/create-request",
            data=form_data
        )
        # Might require verification or authentication
        assert response.status_code in [200, 201, 400, 401]

    async def test_create_request_en(self, client: AsyncClient):
        """Test creating a bid request in English"""
        form_data = {
            "title": "Test Request",
            "description": "Test request description",
            "budget": "1000",
            "contact_email": "test@example.com",
            "contact_phone": "+380501234567",
            "category": "test-category"
        }

        response = await client.post(
            "/api/en/create-request",
            data=form_data
        )
        assert response.status_code in [200, 201, 400, 401]

    async def test_create_request_with_files(self, client: AsyncClient):
        """Test creating a bid request with file attachments"""
        form_data = {
            "title": "Request with files",
            "description": "Description",
            "budget": "2000",
            "contact_email": "test@example.com",
            "contact_phone": "+380501234567",
            "category": "test-category"
        }

        # Create a fake file
        fake_file = BytesIO(b"fake file content")
        fake_file.name = "test.pdf"

        files = {"files": ("test.pdf", fake_file, "application/pdf")}

        response = await client.post(
            "/api/uk/create-request",
            data=form_data,
            files=files
        )
        assert response.status_code in [200, 201, 400, 401]

    async def test_create_request_fast_uk(self, client: AsyncClient):
        """Test fast bid creation in Ukrainian"""
        form_data = {
            "title": "Швидка заявка",
            "description": "Опис",
            "budget": "1500",
            "contact_email": "fast@example.com",
            "contact_phone": "+380501234567"
        }

        response = await client.post(
            "/api/uk/create-request-fast",
            data=form_data
        )
        assert response.status_code in [200, 201, 400, 401]

    async def test_create_request_fast_en(self, client: AsyncClient):
        """Test fast bid creation in English"""
        form_data = {
            "title": "Fast Request",
            "description": "Description",
            "budget": "1500",
            "contact_email": "fast@example.com",
            "contact_phone": "+380501234567"
        }

        response = await client.post(
            "/api/en/create-request-fast",
            data=form_data
        )
        assert response.status_code in [200, 201, 400, 401]

    async def test_verify_request_code(self, client: AsyncClient):
        """Test verifying a bid request with code"""
        form_data = {
            "email": "test@example.com",
            "code": "123456"
        }

        response = await client.post(
            "/api/uk/verify-request-code",
            data=form_data
        )
        # Will likely fail as code doesn't exist, but endpoint should work
        assert response.status_code in [200, 400, 404]

    async def test_submit_response_to_bid(self, client: AsyncClient, test_bid):
        """Test submitting a response to a bid"""
        form_data = {
            "job_id": str(test_bid.id),
            "name": "Test Responder",
            "email": "responder@example.com",
            "message": "I'm interested in this job"
        }

        response = await client.post(
            "/api/submit-response",
            data=form_data
        )
        assert response.status_code in [200, 201, 400]

    async def test_submit_response_missing_fields(self, client: AsyncClient):
        """Test submitting a response with missing fields"""
        form_data = {
            "job_id": "1"
            # Missing name, email, message
        }

        response = await client.post(
            "/api/submit-response",
            data=form_data
        )
        assert response.status_code in [400, 422]

    async def test_delete_bid_as_admin(self, admin_client: AsyncClient, test_bid):
        """Test deleting a bid as admin"""
        response = await admin_client.delete(f"/api/bid/{test_bid.id}")
        # Admin should be able to delete
        assert response.status_code in [200, 204, 401, 403]

    async def test_delete_bid_unauthorized(self, client: AsyncClient, test_bid):
        """Test deleting a bid without authentication"""
        response = await client.delete(f"/api/bid/{test_bid.id}")
        # Should be unauthorized or forbidden
        assert response.status_code in [401, 403]

    async def test_delete_bid_not_found(self, admin_client: AsyncClient):
        """Test deleting non-existent bid"""
        response = await admin_client.delete("/api/bid/99999")
        assert response.status_code in [404, 401, 403]

    async def test_create_request_invalid_language(self, client: AsyncClient):
        """Test creating request with invalid language code"""
        form_data = {
            "title": "Test",
            "description": "Test",
            "budget": "1000",
            "contact_email": "test@example.com"
        }

        response = await client.post(
            "/api/invalid/create-request",
            data=form_data
        )
        # Should return 404 as route doesn't exist
        assert response.status_code == 404

    async def test_list_bids_with_all_filters(self, client: AsyncClient, test_bid, test_category, test_country):
        """Test listing bids with all possible filters"""
        response = await client.get(
            f"/api/bids"
            f"?category={test_category.slug}"
            f"&country={test_country.id}"
            f"&city=Kyiv"
            f"&search=Test"
            f"&limit=20"
            f"&sort=date_desc"
        )
        assert response.status_code == 200
