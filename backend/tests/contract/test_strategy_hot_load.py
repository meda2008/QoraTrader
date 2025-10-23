"""
Contract tests for strategy hot loading endpoints
These tests verify that the strategy hot loading API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_strategy_hot_loading_endpoint_contract():
    """
    Test the contract for strategy hot loading endpoint
    """
    strategy_data = {
        "strategy_id": "test-strategy-123",
        "strategy_code": "def strategy_logic():\n    pass",
        "config": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    
    response = client.post("/api/v1/strategies/hot-load", json=strategy_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "status", "message", "loaded_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Status should indicate success
        assert data["status"] == "loaded"
        assert "successfully" in data["message"].lower()

def test_strategy_unloading_endpoint_contract():
    """
    Test the contract for strategy unloading endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.post(f"/api/v1/strategies/{strategy_id}/unload")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "status", "message", "unloaded_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Status should indicate success
        assert data["status"] == "unloaded"
        assert "successfully" in data["message"].lower()

def test_strategy_reload_endpoint_contract():
    """
    Test the contract for strategy reload endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.post(f"/api/v1/strategies/{strategy_id}/reload")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "status", "message", "reloaded_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Status should indicate success
        assert data["status"] == "reloaded"
        assert "successfully" in data["message"].lower()

def test_strategy_status_endpoint_contract():
    """
    Test the contract for strategy status endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.get(f"/api/v1/strategies/{strategy_id}/hot-load-status")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "is_loaded", "is_active", "loaded_at", 
            "last_modified", "config", "status"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should have a boolean indicating if loaded
        assert isinstance(data["is_loaded"], bool)
        assert isinstance(data["is_active"], bool)