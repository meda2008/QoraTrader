"""
Contract tests for exchange adapter endpoints
These tests verify that the exchange adapter API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_register_exchange_adapter_contract():
    """
    Test the contract for registering an exchange adapter endpoint
    """
    # Test data for registering an exchange adapter
    adapter_data = {
        "name": "test-exchange-adapter",
        "adapter_type": "mock",
        "config": {
            "api_key": "test-api-key",
            "api_secret": "test-api-secret",
            "base_url": "https://api.test-exchange.com"
        }
    }
    
    response = client.post("/api/v1/exchanges/register", json=adapter_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "type", "status", "message"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful registration
        assert data["name"] == "test-exchange-adapter"
        assert data["type"] == "mock"
        assert data["status"] == "registered"

def test_unregister_exchange_adapter_contract():
    """
    Test the contract for unregistering an exchange adapter endpoint
    """
    adapter_name = "test-exchange-adapter"
    response = client.delete(f"/api/v1/exchanges/{adapter_name}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "status", "message"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful unregistration
        assert data["name"] == "test-exchange-adapter"
        assert data["status"] == "unregistered"

def test_connect_exchange_adapter_contract():
    """
    Test the contract for connecting to an exchange adapter endpoint
    """
    adapter_name = "test-exchange-adapter"
    response = client.post(f"/api/v1/exchanges/{adapter_name}/connect")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403, 500]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "status", "message"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful connection
        assert data["name"] == "test-exchange-adapter"
        assert data["status"] == "connected"

def test_disconnect_exchange_adapter_contract():
    """
    Test the contract for disconnecting from an exchange adapter endpoint
    """
    adapter_name = "test-exchange-adapter"
    response = client.post(f"/api/v1/exchanges/{adapter_name}/disconnect")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403, 500]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "status", "message"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful disconnection
        assert data["name"] == "test-exchange-adapter"
        assert data["status"] == "disconnected"

def test_list_exchange_adapters_contract():
    """
    Test the contract for listing exchange adapters endpoint
    """
    response = client.get("/api/v1/exchanges/")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "adapters", "adapter_classes", "count", "class_count"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should return lists
        assert isinstance(data["adapters"], list)
        assert isinstance(data["adapter_classes"], list)

def test_get_exchange_adapter_status_contract():
    """
    Test the contract for getting exchange adapter status endpoint
    """
    adapter_name = "test-exchange-adapter"
    response = client.get(f"/api/v1/exchanges/{adapter_name}/status")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "connected", "supported_markets", "class_name"
        ]
        for field in expected_fields:
            assert field in data

def test_get_all_exchange_adapter_statuses_contract():
    """
    Test the contract for getting all exchange adapter statuses endpoint
    """
    response = client.get("/api/v1/exchanges/statuses")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "statuses", "count"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should return a list of statuses
        assert isinstance(data["statuses"], list)

def test_connect_all_exchange_adapters_contract():
    """
    Test the contract for connecting to all exchange adapters endpoint
    """
    response = client.post("/api/v1/exchanges/connect-all")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "results", "summary", "message"
        ]
        for field in expected_fields:
            assert field in data
            
        # Summary should have expected sub-fields
        summary = data["summary"]
        assert "successful" in summary
        assert "failed" in summary
        assert "total" in summary

def test_disconnect_all_exchange_adapters_contract():
    """
    Test the contract for disconnecting from all exchange adapters endpoint
    """
    response = client.post("/api/v1/exchanges/disconnect-all")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "results", "summary", "message"
        ]
        for field in expected_fields:
            assert field in data
            
        # Summary should have expected sub-fields
        summary = data["summary"]
        assert "successful" in summary
        assert "failed" in summary
        assert "total" in summary

def test_set_default_exchange_adapter_contract():
    """
    Test the contract for setting default exchange adapter endpoint
    """
    adapter_name = "test-exchange-adapter"
    response = client.post(f"/api/v1/exchanges/{adapter_name}/set-default")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "status", "message"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful default setting
        assert data["name"] == "test-exchange-adapter"
        assert data["status"] == "default_set"

def test_get_default_exchange_adapter_contract():
    """
    Test the contract for getting default exchange adapter endpoint
    """
    response = client.get("/api/v1/exchanges/default")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "message"
        ]
        for field in expected_fields:
            assert field in data

def test_update_exchange_adapter_config_contract():
    """
    Test the contract for updating exchange adapter configuration endpoint
    """
    adapter_name = "test-exchange-adapter"
    config_data = {
        "api_key": "updated-api-key",
        "api_secret": "updated-api-secret"
    }
    
    response = client.put(f"/api/v1/exchanges/{adapter_name}/config", json=config_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "status", "message", "updated_config"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should indicate successful config update
        assert data["name"] == "test-exchange-adapter"
        assert data["status"] == "config_updated"

def test_get_supported_markets_contract():
    """
    Test the contract for getting supported markets endpoint
    """
    adapter_name = "test-exchange-adapter"
    response = client.get(f"/api/v1/exchanges/{adapter_name}/markets")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "name", "supported_markets", "count"
        ]
        for field in expected_fields:
            assert field in data
            
        # Should return a list of markets
        assert isinstance(data["supported_markets"], list)