"""
Unit Tests for Bank Management Application
===========================================
Comprehensive test suite using PyTest to test all CRUD operations,
both for web routes and RESTful API endpoints.

Author: Your Name
Date: 2024

Run tests with: pytest test_app.py -v
Run with coverage: pytest test_app.py -v --cov=app
"""

import pytest
import json
from app import app, init_database, get_db_connection

# PYTEST FIXTURES


@pytest.fixture
def client():
    """
    Create a test client for the Flask application.
    This fixture is used by all test functions to make requests to the app.

    Yields:
        FlaskClient: Test client for making requests
    """
    # Configure app for testing
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing

    with app.test_client() as client:
        # Initialize database
        with app.app_context():
            init_database()

        yield client

        # Clean up test data
        with app.app_context():
            cleanup_test_data()


@pytest.fixture
def sample_bank_data():
    """
    Provide sample bank data for testing.

    Returns:
        dict: Sample bank information
    """
    return {"name": "Test Bank", "location": "Test City"}


def cleanup_test_data():
    """
    Clean up test data from the database after tests.
    This ensures each test starts with a clean slate.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Delete all test banks (or all banks in test database)
            cursor.execute("DELETE FROM banks WHERE name LIKE 'Test%'")
            conn.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")


def create_test_bank(name="Test Bank", location="Test City"):
    """
    Helper function to create a test bank directly in the database.

    Args:
        name (str): Bank name
        location (str): Bank location

    Returns:
        int: ID of created bank
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO banks (name, location) VALUES (?, ?)", (name, location)
        )
        conn.commit()
        cursor.execute("SELECT @@IDENTITY AS id")
        return cursor.fetchone()[0]


# WEB INTERFACE TEST
class TestWebInterface:
    """Test cases for web interface routes"""

    def test_index_page_loads(self, client):
        """
        Test that the index page loads successfully.

        Expected: HTTP 200 status code and page contains "All Banks"
        """
        response = client.get("/")
        assert response.status_code == 200
        assert b"All Banks" in response.data

    def test_index_displays_banks(self, client):
        """
        Test that the index page displays existing banks.

        Setup: Create a test bank
        Expected: Bank name appears in the response
        """
        # Create a test bank
        bank_id = create_test_bank("Test Display Bank", "Display City")

        # Fetch index page
        response = client.get("/")
        assert response.status_code == 200
        assert b"Test Display Bank" in response.data

    def test_create_bank_page_loads(self, client):
        """
        Test that the create bank form page loads.

        Expected: HTTP 200 status code
        """
        response = client.get("/bank/new")
        assert response.status_code == 200
        assert b"Add New Bank" in response.data

    def test_create_bank_success(self, client, sample_bank_data):
        """
        Test successful bank creation via web form.

        Expected: Redirect to index page and bank appears in database
        """
        response = client.post(
            "/bank/new", data=sample_bank_data, follow_redirects=True
        )

        assert response.status_code == 200
        assert b"Bank created successfully" in response.data
        assert sample_bank_data["name"].encode() in response.data

    def test_create_bank_missing_fields(self, client):
        """
        Test bank creation with missing required fields.

        Expected: Error message displayed
        """
        response = client.post("/bank/new", data={"name": ""}, follow_redirects=True)

        assert response.status_code == 200
        assert b"required" in response.data.lower()

    def test_view_bank_page(self, client):
        """
        Test viewing a specific bank's details page.

        Setup: Create a test bank
        Expected: HTTP 200 and bank details displayed
        """
        bank_id = create_test_bank("View Test Bank", "View City")

        response = client.get(f"/bank/{bank_id}")
        assert response.status_code == 200
        assert b"View Test Bank" in response.data
        assert b"View City" in response.data

    def test_edit_bank_page_loads(self, client):
        """
        Test that the edit bank form page loads with existing data.

        Setup: Create a test bank
        Expected: HTTP 200 and form pre-filled with bank data
        """
        bank_id = create_test_bank("Edit Test Bank", "Edit City")

        response = client.get(f"/bank/{bank_id}/edit")
        assert response.status_code == 200
        assert b"Edit Test Bank" in response.data

    def test_edit_bank_success(self, client):
        """
        Test successful bank update via web form.

        Setup: Create a test bank
        Expected: Bank updated and redirect to view page
        """
        bank_id = create_test_bank("Original Name", "Original City")

        updated_data = {"name": "Updated Name", "location": "Updated City"}

        response = client.post(
            f"/bank/{bank_id}/edit", data=updated_data, follow_redirects=True
        )

        assert response.status_code == 200
        assert b"Bank updated successfully" in response.data
        assert b"Updated Name" in response.data

    def test_delete_bank_success(self, client):
        """
        Test successful bank deletion.

        Setup: Create a test bank
        Expected: Bank deleted and redirect to index
        """
        bank_id = create_test_bank("Delete Test Bank", "Delete City")

        response = client.post(f"/bank/{bank_id}/delete", follow_redirects=True)

        assert response.status_code == 200
        assert b"Bank deleted successfully" in response.data


# RESTful API TEST

class TestAPIEndpoints:
    """Test cases for RESTful API endpoints."""

    def test_api_get_all_banks_empty(self, client):
        """
        Test API endpoint for retrieving all banks when database is empty.

        Expected: HTTP 200, success=true, empty data array
        """
        cleanup_test_data()  # Ensure database is empty

        response = client.get("/api/banks")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert data["count"] >= 0

    def test_api_get_all_banks_with_data(self, client):
        """
        Test API endpoint for retrieving all banks with existing data.

        Setup: Create test banks
        Expected: HTTP 200, success=true, banks in response
        """
        create_test_bank("API Test Bank 1", "City 1")
        create_test_bank("API Test Bank 2", "City 2")

        response = client.get("/api/banks")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert len(data["data"]) >= 2

    def test_api_get_bank_by_id_success(self, client):
        """
        Test API endpoint for retrieving a specific bank by ID.

        Setup: Create a test bank
        Expected: HTTP 200, success=true, correct bank data
        """
        bank_id = create_test_bank("Specific Bank", "Specific City")

        response = client.get(f"/api/banks/{bank_id}")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["data"]["id"] == bank_id
        assert data["data"]["name"] == "Specific Bank"
        assert data["data"]["location"] == "Specific City"

    def test_api_get_bank_by_id_not_found(self, client):
        """
        Test API endpoint for non-existent bank ID.

        Expected: HTTP 404, success=false, error message
        """
        response = client.get("/api/banks/99999")
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data["success"] is False
        assert "error" in data

    def test_api_create_bank_success(self, client, sample_bank_data):
        """
        Test API endpoint for creating a new bank.

        Expected: HTTP 201, success=true, bank created with ID
        """
        response = client.post(
            "/api/banks",
            data=json.dumps(sample_bank_data),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data["success"] is True
        assert "id" in data["data"]

    def test_api_create_bank_missing_fields(self, client):
        """
        Test API endpoint for creating bank with missing required fields.

        Expected: HTTP 400, success=false, error message
        """
        incomplete_data = {"name": "Test Bank"}  # Missing location

        response = client.post(
            "/api/banks",
            data=json.dumps(incomplete_data),
            content_type="application/json",
        )
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False
        assert "error" in data

    def test_api_update_bank_success(self, client):
        """
        Test API endpoint for updating an existing bank.
        
        Setup: Create a test bank
        Expected: HTTP 200, success=true, bank updated
        """
        bank_id = create_test_bank("Original API Bank", "Original City")
        
        updated_data = {
            "name": "Updated API Bank",
            "location": "Updated City"
        }
        
        response = client.put(
            f'/api/banks/{bank_id}',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
    
    def test_api_update_bank_not_found(self, client):
        """
        Test API endpoint for updating non-existent bank.
        
        Expected: HTTP 404, success=false, error message
        """
        updated_data = {
            "name": "Non-existent Bank",
            "location": "Non-existent City"
        }
        
        response = client.put(
            '/api/banks/99999',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
    
    def test_api_update_bank_missing_fields(self, client):
        """
        Test API endpoint for updating bank with incomplete data.
        Setup: Create a test bank
        Expected: HTTP 400, success=false, error message
        """
        bank_id = create_test_bank("Update Test Bank", "Test City")
        
        incomplete_data = {"name": "Only Name"}  # Missing location
        
        response = client.put(
            f'/api/banks/{bank_id}',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False

    def test_api_delete_bank_success(self, client):
        """
        Test API endpoint for deleting a bank.
        Setup: Create a test bank
        Expected: HTTP 200, success=true, bank deleted
        """
        bank_id = create_test_bank("Delete API Bank", "Delete City")
        
        response = client.delete(f'/api/banks/{bank_id}')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
    
    def test_api_delete_bank_not_found(self, client):
        """
        Test API endpoint for deleting non-existent bank.
        
        Expected: HTTP 404, success=false, error message
        """
        response = client.delete('/api/banks/99999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False