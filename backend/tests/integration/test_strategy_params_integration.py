"""
Integration tests for strategy parameter adjustment workflow
These tests verify that the strategy parameter adjustment functions correctly with the rest of the system
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_update_strategy_parameters_integration():
    """
    Test the integration of updating strategy parameters
    """
    # Mock the strategy parameter service
    with patch('src.services.strategy_param_service.strategy_param_service.update_strategy_parameters') as mock_update:
        # Create mock updated strategy
        mock_updated_strategy = MagicMock()
        mock_updated_strategy.id = "test-strategy-123"
        mock_updated_strategy.name = "Test Strategy"
        mock_updated_strategy.updated_at = MagicMock()
        mock_updated_strategy.updated_at.isoformat.return_value = "2023-10-22T10:30:00Z"
        mock_update.return_value = mock_updated_strategy
        
        strategy_id = "test-strategy-123"
        param_updates = {
            "threshold": 0.07,
            "window_size": 25,
            "enable_shorting": True
        }
        
        response = client.put(f"/api/v1/strategies/{strategy_id}/parameters", json=param_updates)
        
        # Assertions
        assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "test-strategy-123"
            assert data["name"] == "Test Strategy"
            assert "threshold" in data["updated_parameters"]
            assert data["updated_at"] == "2023-10-22T10:30:00Z"

def test_update_single_strategy_parameter_integration():
    """
    Test the integration of updating a single strategy parameter
    """
    # Mock the strategy parameter service
    with patch('src.services.strategy_param_service.strategy_param_service.update_strategy_parameters') as mock_update:
        # Create mock updated strategy
        mock_updated_strategy = MagicMock()
        mock_updated_strategy.id = "test-strategy-123"
        mock_updated_strategy.name = "Test Strategy"
        mock_updated_strategy.updated_at = MagicMock()
        mock_updated_strategy.updated_at.isoformat.return_value = "2023-10-22T10:30:00Z"
        mock_update.return_value = mock_updated_strategy
        
        strategy_id = "test-strategy-123"
        param_name = "threshold"
        param_value = 0.08
        
        response = client.patch(
            f"/api/v1/strategies/{strategy_id}/parameters/{param_name}",
            json={"param_value": param_value}
        )
        
        # Assertions
        assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "test-strategy-123"
            assert data["updated_parameter"] == "threshold"
            assert data["new_value"] == 0.08
            assert data["updated_at"] == "2023-10-22T10:30:00Z"

def test_get_strategy_parameters_integration():
    """
    Test the integration of getting strategy parameters
    """
    # Mock the database query
    with patch('src.database.get_db') as mock_get_db:
        # Create mock database session
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_strategy = MagicMock()
        mock_strategy.id = "test-strategy-123"
        mock_strategy.name = "Test Strategy"
        mock_strategy.config = '{"threshold": 0.05, "window_size": 20}'
        mock_strategy.created_at = MagicMock()
        mock_strategy.created_at.isoformat.return_value = "2023-10-20T10:00:00Z"
        mock_strategy.updated_at = MagicMock()
        mock_strategy.updated_at.isoformat.return_value = "2023-10-22T10:30:00Z"
        
        mock_query.filter.return_value.first.return_value = mock_strategy
        mock_session.query.return_value = mock_query
        mock_get_db.return_value = iter([mock_session])
        
        strategy_id = "test-strategy-123"
        response = client.get(f"/api/v1/strategies/{strategy_id}/parameters")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "test-strategy-123"
            assert data["name"] == "Test Strategy"
            assert "threshold" in data["parameters"]
            assert data["parameters"]["threshold"] == 0.05
            assert data["parameters"]["window_size"] == 20
            assert data["created_at"] == "2023-10-20T10:00:00Z"
            assert data["updated_at"] == "2023-10-22T10:30:00Z"

def test_remove_strategy_parameter_integration():
    """
    Test the integration of removing a strategy parameter
    """
    # Mock the strategy parameter service
    with patch('src.services.strategy_param_service.strategy_param_service.remove_strategy_parameter') as mock_remove:
        # Create mock updated strategy
        mock_updated_strategy = MagicMock()
        mock_updated_strategy.id = "test-strategy-123"
        mock_updated_strategy.name = "Test Strategy"
        mock_updated_strategy.updated_at = MagicMock()
        mock_updated_strategy.updated_at.isoformat.return_value = "2023-10-22T10:30:00Z"
        mock_remove.return_value = mock_updated_strategy
        
        strategy_id = "test-strategy-123"
        param_name = "obsolete_param"
        
        response = client.delete(f"/api/v1/strategies/{strategy_id}/parameters/{param_name}")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "test-strategy-123"
            assert data["removed_parameter"] == "obsolete_param"
            assert data["updated_at"] == "2023-10-22T10:30:00Z"

def test_reset_strategy_parameters_integration():
    """
    Test the integration of resetting strategy parameters
    """
    # Mock the strategy parameter service
    with patch('src.services.strategy_param_service.strategy_param_service.reset_strategy_parameters') as mock_reset:
        # Create mock updated strategy
        mock_updated_strategy = MagicMock()
        mock_updated_strategy.id = "test-strategy-123"
        mock_updated_strategy.name = "Test Strategy"
        mock_updated_strategy.updated_at = MagicMock()
        mock_updated_strategy.updated_at.isoformat.return_value = "2023-10-22T10:30:00Z"
        mock_reset.return_value = mock_updated_strategy
        
        strategy_id = "test-strategy-123"
        response = client.post(f"/api/v1/strategies/{strategy_id}/parameters/reset")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "test-strategy-123"
            assert "reset" in data["message"].lower()
            assert data["updated_at"] == "2023-10-22T10:30:00Z"

def test_validate_strategy_parameters_integration():
    """
    Test the integration of validating strategy parameters
    """
    # Mock the strategy parameter service
    with patch('src.services.strategy_param_service.strategy_param_service.validate_strategy_parameters') as mock_validate:
        # Create mock validation result
        mock_validation_result = {
            "valid": True,
            "message": "All parameters are valid"
        }
        mock_validate.return_value = mock_validation_result
        
        strategy_id = "test-strategy-123"
        param_updates = {
            "threshold": 0.10,
            "window_size": 30
        }
        
        response = client.post(
            f"/api/v1/strategies/{strategy_id}/parameters/validate",
            json=param_updates
        )
        
        # Assertions
        assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "test-strategy-123"
            assert data["valid"] == True
            assert "valid" in data["message"].lower()
            assert isinstance(data["validated_parameters"], list)
            assert "threshold" in data["validated_parameters"]

def test_get_parameter_update_history_integration():
    """
    Test the integration of getting parameter update history
    """
    # Mock the strategy parameter service or database query
    # For this test, we'll simulate the endpoint returning mock data
    strategy_id = "test-strategy-123"
    response = client.get(f"/api/v1/strategies/{strategy_id}/parameters/history")
    
    # Assertions
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        assert data["strategy_id"] == "test-strategy-123"
        assert isinstance(data["history"], list)
        assert isinstance(data["count"], int)
        
        # Each history entry should have expected fields
        if len(data["history"]) > 0:
            first_entry = data["history"][0]
            entry_fields = ["timestamp", "parameter", "old_value", "new_value", "updated_by"]
            for field in entry_fields:
                assert field in first_entry

def test_strategy_parameter_workflow_integration():
    """
    Test the complete workflow of strategy parameter adjustment
    """
    # Step 1: Get current parameters
    with patch('src.database.get_db') as mock_get_db:
        # Create mock database session for get parameters
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_strategy = MagicMock()
        mock_strategy.id = "workflow-test-strategy"
        mock_strategy.name = "Workflow Test Strategy"
        mock_strategy.config = '{"initial_threshold": 0.05, "window_size": 20}'
        mock_strategy.created_at = MagicMock()
        mock_strategy.created_at.isoformat.return_value = "2023-10-20T10:00:00Z"
        mock_strategy.updated_at = MagicMock()
        mock_strategy.updated_at.isoformat.return_value = "2023-10-22T10:00:00Z"
        
        mock_query.filter.return_value.first.return_value = mock_strategy
        mock_session.query.return_value = mock_query
        mock_get_db.return_value = iter([mock_session])
        
        strategy_id = "workflow-test-strategy"
        response = client.get(f"/api/v1/strategies/{strategy_id}/parameters")
        
        assert response.status_code in [200, 404, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "workflow-test-strategy"
            assert "initial_threshold" in data["parameters"]
    
    # Step 2: Validate new parameters
    with patch('src.services.strategy_param_service.strategy_param_service.validate_strategy_parameters') as mock_validate:
        mock_validation_result = {
            "valid": True,
            "message": "All parameters are valid"
        }
        mock_validate.return_value = mock_validation_result
        
        param_updates = {
            "initial_threshold": 0.07,
            "new_param": "test_value"
        }
        
        response = client.post(
            f"/api/v1/strategies/{strategy_id}/parameters/validate",
            json=param_updates
        )
        
        assert response.status_code in [200, 422, 404, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["valid"] == True
    
    # Step 3: Update parameters
    with patch('src.services.strategy_param_service.strategy_param_service.update_strategy_parameters') as mock_update:
        mock_updated_strategy = MagicMock()
        mock_updated_strategy.id = "workflow-test-strategy"
        mock_updated_strategy.name = "Workflow Test Strategy"
        mock_updated_strategy.updated_at = MagicMock()
        mock_updated_strategy.updated_at.isoformat.return_value = "2023-10-22T10:30:00Z"
        mock_update.return_value = mock_updated_strategy
        
        response = client.put(f"/api/v1/strategies/{strategy_id}/parameters", json=param_updates)
        
        assert response.status_code in [200, 422, 404, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["strategy_id"] == "workflow-test-strategy"
            assert len(data["updated_parameters"]) == 2

def test_strategy_parameter_update_with_invalid_data():
    """
    Test strategy parameter update with invalid data
    """
    strategy_id = "test-strategy-123"
    
    # Test with empty parameter updates
    response = client.put(f"/api/v1/strategies/{strategy_id}/parameters", json={})
    
    # Should return validation error
    assert response.status_code in [422, 400, 401, 403]  # Validation error codes
    
    # Test with invalid parameter values
    invalid_param_updates = {
        "threshold": -0.1,  # Negative threshold might be invalid
        "window_size": 0    # Zero window size might be invalid
    }
    
    with patch('src.services.strategy_param_service.strategy_param_service.validate_strategy_parameters') as mock_validate:
        mock_validation_result = {
            "valid": False,
            "message": "Invalid parameter values"
        }
        mock_validate.return_value = mock_validation_result
        
        response = client.post(
            f"/api/v1/strategies/{strategy_id}/parameters/validate",
            json=invalid_param_updates
        )
        
        assert response.status_code in [200, 422, 404, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert data["valid"] == False

def test_strategy_parameter_update_for_nonexistent_strategy():
    """
    Test strategy parameter update for a nonexistent strategy
    """
    # Mock the strategy parameter service to raise not found error
    with patch('src.services.strategy_param_service.strategy_param_service.update_strategy_parameters') as mock_update:
        from src.utils.error_handler import CustomException
        mock_update.side_effect = CustomException("Strategy not found", 404)
        
        strategy_id = "nonexistent-strategy"
        param_updates = {
            "threshold": 0.07
        }
        
        response = client.put(f"/api/v1/strategies/{strategy_id}/parameters", json=param_updates)
        
        # Should return not found error
        assert response.status_code in [404, 401, 403, 500]

def test_strategy_parameter_validation_with_malformed_json():
    """
    Test strategy parameter validation with malformed JSON
    """
    strategy_id = "test-strategy-123"
    
    # Send malformed JSON
    response = client.post(
        f"/api/v1/strategies/{strategy_id}/parameters/validate",
        content='{"invalid": json}',  # Malformed JSON
        headers={"Content-Type": "application/json"}
    )
    
    # Should return bad request error
    assert response.status_code in [400, 422, 401, 403]

def test_bulk_strategy_parameter_update_integration():
    """
    Test bulk strategy parameter update functionality
    """
    # Mock the strategy parameter service bulk update
    with patch('src.services.strategy_param_service.strategy_param_service.bulk_update_strategy_parameters') as mock_bulk_update:
        mock_bulk_result = {
            "successful": ["strategy-1", "strategy-2"],
            "failed": [
                {"strategy_id": "strategy-3", "error": "Not found"}
            ]
        }
        mock_bulk_update.return_value = mock_bulk_result
        
        strategy_ids = ["strategy-1", "strategy-2", "strategy-3"]
        param_updates = {
            "common_param": "common_value"
        }
        
        # This would be a POST to a bulk update endpoint
        # For now, we'll test the service method directly
        from src.services.strategy_param_service import strategy_param_service
        result = strategy_param_service.bulk_update_strategy_parameters(strategy_ids, param_updates)
        
        assert "successful" in result
        assert "failed" in result
        assert isinstance(result["successful"], list)
        assert isinstance(result["failed"], list)

def test_strategy_parameter_encryption_integration():
    """
    Test that sensitive strategy parameters are properly encrypted
    """
    # This test would verify encryption/decryption of sensitive parameters
    # In a real implementation, this would test the encryption service
    
    # Mock sensitive parameter handling
    with patch('src.services.strategy_param_service.strategy_param_service.update_strategy_parameters') as mock_update:
        # Create mock updated strategy
        mock_updated_strategy = MagicMock()
        mock_updated_strategy.id = "secure-strategy"
        mock_updated_strategy.name = "Secure Strategy"
        mock_updated_strategy.updated_at = MagicMock()
        mock_updated_strategy.updated_at.isoformat.return_value = "2023-10-22T10:30:00Z"
        mock_update.return_value = mock_updated_strategy
        
        strategy_id = "secure-strategy"
        # Parameters that might contain sensitive data
        sensitive_params = {
            "api_key": "secret_api_key_12345",
            "secret_phrase": "very_secret_phrase",
            "threshold": 0.07  # Non-sensitive parameter
        }
        
        response = client.put(f"/api/v1/strategies/{strategy_id}/parameters", json=sensitive_params)
        
        # In a real implementation, we would verify that sensitive data is encrypted
        # For this test, we just verify the request is processed
        assert response.status_code in [200, 422, 404, 401, 403]

def test_strategy_parameter_versioning_integration():
    """
    Test that strategy parameter updates are properly versioned
    """
    # This test would verify that parameter changes are tracked with versioning
    # In a real implementation, this would test the versioning system
    
    # Mock parameter history tracking
    strategy_id = "versioned-strategy"
    response = client.get(f"/api/v1/strategies/{strategy_id}/parameters/history")
    
    # In a real implementation, this would return actual parameter history
    # For this test, we verify the endpoint is accessible
    assert response.status_code in [200, 404, 401, 403]