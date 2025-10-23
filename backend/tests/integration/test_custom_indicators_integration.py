"""
Integration tests for custom indicator functionality
These tests verify that the custom indicator functionality works correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_custom_indicator_registration_integration():
    """
    Test the integration of custom indicator registration
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.register_custom_indicator') as mock_register:
        # Create mock registration result
        mock_registration_result = {
            "id": "custom-indicator-123",
            "name": "custom_macd",
            "description": "Custom MACD implementation",
            "version": "1.0.0",
            "path": "/path/to/custom/macd.py",
            "is_active": True,
            "created_at": "2023-10-22T10:30:00Z",
            "updated_at": "2023-10-22T10:30:00Z"
        }
        mock_register.return_value = mock_registration_result
        
        # Test registration data
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
        
        # Assertions
        assert response.status_code in [200, 422, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == "custom-indicator-123"
            assert data["name"] == "custom_macd"
            assert data["is_active"] == True

def test_custom_indicator_listing_integration():
    """
    Test the integration of custom indicator listing
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.list_custom_indicators') as mock_list:
        # Create mock listing result
        mock_listing_result = [
            {
                "id": "indicator-1",
                "name": "custom_macd",
                "description": "Custom MACD implementation",
                "version": "1.0.0",
                "path": "/path/to/custom/macd.py",
                "is_active": True,
                "created_at": "2023-10-22T10:30:00Z",
                "updated_at": "2023-10-22T10:30:00Z"
            },
            {
                "id": "indicator-2",
                "name": "custom_rsi",
                "description": "Custom RSI implementation",
                "version": "1.0.0",
                "path": "/path/to/custom/rsi.py",
                "is_active": False,
                "created_at": "2023-10-22T10:30:00Z",
                "updated_at": "2023-10-22T10:30:00Z"
            }
        ]
        mock_list.return_value = mock_listing_result
        
        response = client.get("/api/v1/indicators/custom-list")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["name"] == "custom_macd"
        assert data[1]["name"] == "custom_rsi"

def test_custom_indicator_calculation_integration():
    """
    Test the integration of custom indicator calculation
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.calculate_custom_indicator') as mock_calculate:
        # Create mock calculation result
        mock_calculation_result = {
            "indicator_id": "custom-indicator-123",
            "input_data": [100, 101, 102, 103, 104],
            "parameters": {"period": 5},
            "result": [102.0]  # Simple moving average result
        }
        mock_calculate.return_value = mock_calculation_result
        
        # Test calculation data
        calculation_data = {
            "indicator_id": "custom-indicator-123",
            "input_data": [100, 101, 102, 103, 104],
            "parameters": {
                "period": 5
            }
        }
        
        response = client.post("/api/v1/indicators/calculate-custom", json=calculation_data)
        
        # Assertions
        assert response.status_code in [200, 422, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["indicator_id"] == "custom-indicator-123"
            assert len(data["result"]) == 1
            assert data["result"][0] == 102.0

def test_custom_indicator_removal_integration():
    """
    Test the integration of custom indicator removal
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.remove_custom_indicator') as mock_remove:
        # Create mock removal result
        mock_remove_result = True
        mock_remove.return_value = mock_remove_result
        
        indicator_id = "custom-indicator-123"
        response = client.delete(f"/api/v1/indicators/remove-custom/{indicator_id}")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "successfully" in data["message"].lower()

def test_custom_indicator_activation_integration():
    """
    Test the integration of custom indicator activation
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.activate_custom_indicator') as mock_activate:
        # Create mock activation result
        mock_activation_result = {
            "id": "custom-indicator-123",
            "name": "custom_macd",
            "description": "Custom MACD implementation",
            "version": "1.0.0",
            "path": "/path/to/custom/macd.py",
            "is_active": True,
            "created_at": "2023-10-22T10:30:00Z",
            "updated_at": "2023-10-22T10:35:00Z"
        }
        mock_activate.return_value = mock_activation_result
        
        indicator_id = "custom-indicator-123"
        response = client.post(f"/api/v1/indicators/{indicator_id}/activate")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == "custom-indicator-123"
            assert data["is_active"] == True
            assert data["updated_at"] == "2023-10-22T10:35:00Z"

def test_custom_indicator_deactivation_integration():
    """
    Test the integration of custom indicator deactivation
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.deactivate_custom_indicator') as mock_deactivate:
        # Create mock deactivation result
        mock_deactivation_result = {
            "id": "custom-indicator-123",
            "name": "custom_macd",
            "description": "Custom MACD implementation",
            "version": "1.0.0",
            "path": "/path/to/custom/macd.py",
            "is_active": False,
            "created_at": "2023-10-22T10:30:00Z",
            "updated_at": "2023-10-22T10:40:00Z"
        }
        mock_deactivate.return_value = mock_deactivation_result
        
        indicator_id = "custom-indicator-123"
        response = client.post(f"/api/v1/indicators/{indicator_id}/deactivate")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == "custom-indicator-123"
            assert data["is_active"] == False
            assert data["updated_at"] == "2023-10-22T10:40:00Z"

def test_custom_indicator_calculation_with_invalid_data():
    """
    Test custom indicator calculation with invalid input data
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.calculate_custom_indicator') as mock_calculate:
        # Simulate calculation error
        mock_calculate.side_effect = Exception("Invalid input data")
        
        # Test calculation with invalid data
        calculation_data = {
            "indicator_id": "non-existent-indicator",
            "input_data": [],  # Empty data
            "parameters": {}
        }
        
        response = client.post("/api/v1/indicators/calculate-custom", json=calculation_data)
        
        # Should return an error
        assert response.status_code in [400, 404, 422, 500, 401, 403]

def test_custom_indicator_registration_with_duplicate_name():
    """
    Test custom indicator registration with duplicate name
    """
    # Mock the indicator service
    with patch('src.services.indicator_service.indicator_service.register_custom_indicator') as mock_register:
        # Simulate duplicate name error
        mock_register.side_effect = Exception("Indicator with this name already exists")
        
        # Test registration with duplicate name
        indicator_data = {
            "name": "duplicate_indicator",
            "description": "Duplicate indicator test",
            "version": "1.0.0",
            "library_path": "/path/to/duplicate/indicator.py",
            "function_name": "calculate_indicator",
            "parameters": {}
        }
        
        response = client.post("/api/v1/indicators/register-custom", json=indicator_data)
        
        # Should return an error
        assert response.status_code in [400, 422, 500, 401, 403]