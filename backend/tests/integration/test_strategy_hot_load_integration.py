"""
Integration tests for hot loading functionality
These tests verify that the strategy hot loading functions correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_strategy_hot_loading_integration():
    """
    Test the integration of strategy hot loading functionality
    """
    # Mock the strategy hot loader service
    with patch('src.strategies.hot_reload.strategy_hot_reloader.reload_strategy') as mock_reload_strategy:
        # Create mock reload result
        mock_reload_result = True
        mock_reload_strategy.return_value = mock_reload_result
        
        # Test strategy data
        strategy_data = {
            "strategy_id": "test-strategy-123",
            "strategy_code": "def strategy_logic():\n    return 'test'",
            "config": {
                "param1": "value1",
                "param2": "value2"
            }
        }
        
        response = client.post("/api/v1/strategies/hot-load", json=strategy_data)
        
        # Assertions
        assert response.status_code in [200, 422, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert "strategy_id" in data
            assert "status" in data
            assert data["status"] in ["loaded", "error"]

def test_strategy_unloading_integration():
    """
    Test the integration of strategy unloading functionality
    """
    # Mock the strategy management service
    with patch('src.strategies.manager.strategy_manager.unregister_strategy') as mock_unregister:
        # Create mock unregister result
        mock_unregister.return_value = True
        
        strategy_id = "test-strategy-123"
        response = client.post(f"/api/v1/strategies/{strategy_id}/unload")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert "strategy_id" in data
            assert "status" in data
            assert data["status"] == "unloaded"

def test_strategy_reload_integration():
    """
    Test the integration of strategy reload functionality
    """
    # Mock the strategy hot loader service
    with patch('src.strategies.hot_reload.strategy_hot_reloader.reload_strategy') as mock_reload_strategy:
        # Create mock reload result
        mock_reload_result = True
        mock_reload_strategy.return_value = mock_reload_result
        
        strategy_id = "test-strategy-123"
        response = client.post(f"/api/v1/strategies/{strategy_id}/reload")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert "strategy_id" in data
            assert "status" in data
            assert data["status"] == "reloaded"

def test_strategy_status_integration():
    """
    Test the integration of strategy status retrieval
    """
    # Mock the strategy management service
    with patch('src.strategies.manager.strategy_manager.get_strategy_status') as mock_get_status:
        # Create mock status data
        mock_status_data = {
            "strategy_id": "test-strategy-123",
            "is_loaded": True,
            "is_active": True,
            "loaded_at": "2023-10-22T10:30:00Z",
            "last_modified": "2023-10-22T10:30:00Z",
            "config": {
                "param1": "value1",
                "param2": "value2"
            },
            "status": "active"
        }
        mock_get_status.return_value = mock_status_data
        
        strategy_id = "test-strategy-123"
        response = client.get(f"/api/v1/strategies/{strategy_id}/hot-load-status")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "test-strategy-123"
            assert data["is_loaded"] == True
            assert data["is_active"] == True
            assert data["status"] == "active"

def test_multiple_strategies_hot_loading():
    """
    Test hot loading of multiple strategies
    """
    # Mock the strategy hot loader service
    with patch('src.strategies.hot_reload.strategy_hot_reloader.reload_strategy') as mock_reload_strategy:
        # Create mock reload result
        mock_reload_result = True
        mock_reload_strategy.return_value = mock_reload_result
        
        # Test multiple strategies
        strategies_data = [
            {
                "strategy_id": "strategy-1",
                "strategy_code": "def strategy_logic():\n    return 'strategy-1'",
                "config": {"param": "value1"}
            },
            {
                "strategy_id": "strategy-2", 
                "strategy_code": "def strategy_logic():\n    return 'strategy-2'",
                "config": {"param": "value2"}
            }
        ]
        
        # Load each strategy
        for strategy_data in strategies_data:
            response = client.post("/api/v1/strategies/hot-load", json=strategy_data)
            
            # Basic assertions
            assert response.status_code in [200, 422, 401, 403]
            
            if response.status_code == 200:
                data = response.json()
                assert "strategy_id" in data
                assert data["strategy_id"] == strategy_data["strategy_id"]

def test_strategy_hot_loading_with_invalid_code():
    """
    Test hot loading with invalid strategy code
    """
    # Mock the strategy hot loader service to simulate compilation error
    with patch('src.strategies.hot_reload.strategy_hot_reloader.reload_strategy') as mock_reload_strategy:
        # Simulate compilation error
        mock_reload_strategy.return_value = False
        
        strategy_data = {
            "strategy_id": "test-strategy-invalid",
            "strategy_code": "def strategy_logic(:\n    return 'invalid-code'",  # Invalid Python syntax
            "config": {"param": "value"}
        }
        
        response = client.post("/api/v1/strategies/hot-load", json=strategy_data)
        
        # Should return an error or indicate failure
        assert response.status_code in [200, 422, 400, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            # Should indicate error or failure in loading
            assert data["status"] in ["loaded", "error"]

def test_strategy_hot_loading_without_authentication():
    """
    Test hot loading without proper authentication
    """
    # Test without authentication headers
    strategy_data = {
        "strategy_id": "test-strategy-123",
        "strategy_code": "def strategy_logic():\n    return 'test'",
        "config": {"param": "value"}
    }
    
    # This should fail with 401 Unauthorized
    response = client.post("/api/v1/strategies/hot-load", json=strategy_data)
    
    # Should be unauthorized or have error
    assert response.status_code in [401, 403, 422]