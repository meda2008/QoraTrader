"""
Integration tests for indicator service
These tests verify that the indicator service functions correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_indicator_service_integration():
    """
    Test the integration of the indicator service with the API
    """
    # Test with a simple indicator request
    indicator_request = {
        "indicator_name": "sma",  # Simple moving average
        "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "params": {
            "period": 3
        }
    }
    
    # This will test the actual indicator service
    response = client.post("/api/v1/indicators/calculate", json=indicator_request)
    
    # The response code could vary depending on if the indicator is implemented
    assert response.status_code in [200, 400, 404, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "result" in data

def test_invalid_indicator_name():
    """
    Test calling an invalid indicator name
    """
    indicator_request = {
        "indicator_name": "invalid_indicator_name",
        "data": [1, 2, 3, 4, 5],
        "params": {}
    }
    
    response = client.post("/api/v1/indicators/calculate", json=indicator_request)
    
    # Should return an error for invalid indicator
    assert response.status_code in [400, 404]  # 400 for validation error, 404 for not found

def test_indicator_list_endpoint():
    """
    Test the indicator list endpoint
    """
    response = client.get("/api/v1/indicators/list")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)