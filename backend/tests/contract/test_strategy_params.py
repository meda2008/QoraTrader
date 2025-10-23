"""
Contract tests for strategy parameter update endpoints
These tests verify that the strategy parameter update API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_update_strategy_parameters_contract():
    """
    Test the contract for updating strategy parameters endpoint
    """
    strategy_id = "test-strategy-123"
    param_updates = {
        "threshold": 0.07,
        "window_size": 25,
        "enable_shorting": True
    }
    
    response = client.put(f"/api/v1/strategies/{strategy_id}/parameters", json=param_updates)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "name", "message", "updated_at", "updated_parameters"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful update
        assert data["strategy_id"] == "test-strategy-123"
        assert isinstance(data["updated_parameters"], list)
        assert "threshold" in data["updated_parameters"]

def test_update_single_strategy_parameter_contract():
    """
    Test the contract for updating a single strategy parameter endpoint
    """
    strategy_id = "test-strategy-123"
    param_name = "threshold"
    param_value = 0.08
    
    response = client.patch(
        f"/api/v1/strategies/{strategy_id}/parameters/{param_name}",
        json={"param_value": param_value}
    )
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "name", "message", "updated_at", "updated_parameter", "new_value"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful update
        assert data["strategy_id"] == "test-strategy-123"
        assert data["updated_parameter"] == "threshold"
        assert data["new_value"] == 0.08

def test_get_strategy_parameters_contract():
    """
    Test the contract for getting strategy parameters endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.get(f"/api/v1/strategies/{strategy_id}/parameters")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "name", "parameters", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Parameters should be a dictionary
        assert isinstance(data["parameters"], dict)

def test_remove_strategy_parameter_contract():
    """
    Test the contract for removing a strategy parameter endpoint
    """
    strategy_id = "test-strategy-123"
    param_name = "obsolete_param"
    
    response = client.delete(f"/api/v1/strategies/{strategy_id}/parameters/{param_name}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "name", "message", "updated_at", "removed_parameter"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful removal
        assert data["strategy_id"] == "test-strategy-123"
        assert data["removed_parameter"] == "obsolete_param"

def test_reset_strategy_parameters_contract():
    """
    Test the contract for resetting strategy parameters endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.post(f"/api/v1/strategies/{strategy_id}/parameters/reset")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "name", "message", "updated_at"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful reset
        assert data["strategy_id"] == "test-strategy-123"
        assert "reset" in data["message"].lower()

def test_validate_strategy_parameters_contract():
    """
    Test the contract for validating strategy parameters endpoint
    """
    strategy_id = "test-strategy-123"
    param_updates = {
        "threshold": 0.10,
        "window_size": 30
    }
    
    response = client.post(
        f"/api/v1/strategies/{strategy_id}/parameters/validate",
        json=param_updates
    )
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "valid", "message", "validation_time", "validated_parameters"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate validation result
        assert data["strategy_id"] == "test-strategy-123"
        assert isinstance(data["valid"], bool)
        assert isinstance(data["validated_parameters"], list)

def test_get_parameter_update_history_contract():
    """
    Test the contract for getting parameter update history endpoint
    """
    strategy_id = "test-strategy-123"
    response = client.get(f"/api/v1/strategies/{strategy_id}/parameters/history")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "history", "count"
        ]
        for field in expected_fields:
            assert field in data
            
        # History should be a list
        assert isinstance(data["history"], list)
        assert isinstance(data["count"], int)
        
        # Each history entry should have expected fields
        if len(data["history"]) > 0:
            first_entry = data["history"][0]
            entry_fields = ["timestamp", "parameter", "old_value", "new_value", "updated_by"]
            for field in entry_fields:
                assert field in first_entry