"""
Tests for the main FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_docs_endpoint(client):
    """Test API documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_cors_headers(client):
    """Test CORS headers are present."""
    # Test with a GET request since OPTIONS might not be allowed
    response = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    # Check for CORS headers
    assert "access-control-allow-origin" in response.headers


@patch('services.instance_service.InstanceService.load_instances')
@patch('services.instance_service.InstanceService.discover_docker_instances')
def test_app_startup(mock_discover, mock_load, client):
    """Test application startup."""
    mock_load.return_value = None
    mock_discover.return_value = None
    
    # Test that the app starts without errors
    response = client.get("/api/health")
    assert response.status_code == 200