"""
Contract tests for custom indicator registration endpoints
These tests verify that the custom indicator registration API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_custom_indicator_registration_endpoint_contract():
    """
    Test the contract for custom indicator registration endpoint
    """
    # Test data for custom indicator registration
    indicator_data = {
        "name": "custom_macd",
        "description": "Custom MACD implementation",
        "version": "1.0.0",
        "library_path": "/path/to/custom/macd.py",
        "function_name": "calculate_macd",
        "parameters": {
            "fast_period": 12,
            "slow_period": 26,
            "signal_period": 9
        }
    }
    
    response = client.post("/api/v1/indicators/register-custom", json=indicator_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "id", "name", "description", "version", "path", 
            "is_active", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful registration
        assert data["name"] == "custom_macd"
        assert data["is_active"] == True

def test_custom_indicator_list_endpoint_contract():
    """
    Test the contract for listing custom indicators endpoint
    """
    response = client.get("/api/v1/indicators/custom-list")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return a list of custom indicators
        assert isinstance(data, list)
        if len(data) > 0:
            # Each custom indicator should have certain fields
            first_indicator = data[0]
            expected_fields = [
                "id", "name", "description", "version", "path", 
                "is_active", "created_at", "updated_at"
            ]
            for field in expected_fields:
                assert field in first_indicator

def test_custom_indicator_removal_endpoint_contract():
    """
    Test the contract for removing custom indicator endpoint
    """
    indicator_id = "test-indicator-id"
    response = client.delete(f"/api/v1/indicators/remove-custom/{indicator_id}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return success message
        assert "message" in data
        assert "successfully" in data["message"].lower()

def test_custom_indicator_activation_endpoint_contract():
    """
    Test the contract for activating custom indicator endpoint
    """
    indicator_id = "test-indicator-id"
    response = client.post(f"/api/v1/indicators/{indicator_id}/activate")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return updated indicator info
        expected_fields = [
            "id", "name", "description", "version", "path", 
            "is_active", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
        # Should be active now
        assert data["is_active"] == True

def test_custom_indicator_deactivation_endpoint_contract():
    """
    Test the contract for deactivating custom indicator endpoint
    """
    indicator_id = "test-indicator-id"
    response = client.post(f"/api/v1/indicators/{indicator_id}/deactivate")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return updated indicator info
        expected_fields = [
            "id", "name", "description", "version", "path", 
            "is_active", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
        # Should be inactive now
        assert data["is_active"] == False