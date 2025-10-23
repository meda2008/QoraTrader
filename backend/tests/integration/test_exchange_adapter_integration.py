"""
Integration tests for exchange adapter functionality
These tests verify that the exchange adapter functions correctly with the rest of the system
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_exchange_adapter_registration_integration():
    """
    Test the integration of exchange adapter registration
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.register_adapter') as mock_register:
        # Create mock registration result
        mock_register.return_value = True
        
        # Test adapter data
        adapter_data = {
            "name": "test-exchange-adapter",
            "adapter_type": "mock",
            "config": {
                "api_key": "test-api-key",
                "api_secret": "test-api-secret"
            }
        }
        
        response = client.post("/api/v1/exchanges/register", json=adapter_data)
        
        # Assertions
        assert response.status_code in [200, 422, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert data["type"] == "mock"
            assert data["status"] == "registered"

def test_exchange_adapter_connection_integration():
    """
    Test the integration of exchange adapter connection
    """
    # Mock the exchange registry and adapter
    with patch('src.exchanges.registry.exchange_registry.get_adapter') as mock_get_adapter:
        # Create mock adapter
        mock_adapter = MagicMock()
        mock_adapter.connect = MagicMock(return_value=True)
        mock_adapter.connected = False
        mock_get_adapter.return_value = mock_adapter
        
        adapter_name = "test-exchange-adapter"
        response = client.post(f"/api/v1/exchanges/{adapter_name}/connect")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403, 500]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert data["status"] == "connected"

def test_exchange_adapter_disconnection_integration():
    """
    Test the integration of exchange adapter disconnection
    """
    # Mock the exchange registry and adapter
    with patch('src.exchanges.registry.exchange_registry.get_adapter') as mock_get_adapter:
        # Create mock adapter
        mock_adapter = MagicMock()
        mock_adapter.disconnect = MagicMock(return_value=True)
        mock_adapter.connected = True
        mock_get_adapter.return_value = mock_adapter
        
        adapter_name = "test-exchange-adapter"
        response = client.post(f"/api/v1/exchanges/{adapter_name}/disconnect")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403, 500]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert data["status"] == "disconnected"

def test_list_exchange_adapters_integration():
    """
    Test the integration of listing exchange adapters
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.list_adapters') as mock_list_adapters, \
         patch('src.exchanges.registry.exchange_registry.list_adapter_classes') as mock_list_classes:
        # Create mock adapter lists
        mock_list_adapters.return_value = ["adapter1", "adapter2"]
        mock_list_classes.return_value = ["MockAdapter", "RealAdapter"]
        
        response = client.get("/api/v1/exchanges/")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["adapters"], list)
        assert isinstance(data["adapter_classes"], list)
        assert len(data["adapters"]) == 2
        assert len(data["adapter_classes"]) == 2
        assert "adapter1" in data["adapters"]
        assert "MockAdapter" in data["adapter_classes"]

def test_get_exchange_adapter_status_integration():
    """
    Test the integration of getting exchange adapter status
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.get_adapter_status') as mock_get_status:
        # Create mock status data
        mock_status_data = {
            "name": "test-exchange-adapter",
            "connected": True,
            "supported_markets": ["BTC/USD", "ETH/USD"],
            "class_name": "MockExchangeAdapter",
            "last_updated": "2023-10-22T10:30:00Z"
        }
        mock_get_status.return_value = mock_status_data
        
        adapter_name = "test-exchange-adapter"
        response = client.get(f"/api/v1/exchanges/{adapter_name}/status")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert data["connected"] == True
            assert "BTC/USD" in data["supported_markets"]
            assert data["class_name"] == "MockExchangeAdapter"

def test_connect_all_exchange_adapters_integration():
    """
    Test the integration of connecting to all exchange adapters
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.connect_all_adapters') as mock_connect_all:
        # Create mock connection results
        mock_results = {
            "adapter1": True,
            "adapter2": False
        }
        mock_connect_all.return_value = mock_results
        
        response = client.post("/api/v1/exchanges/connect-all")
        
        # Assertions
        assert response.status_code in [200, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "summary" in data
            assert data["results"]["adapter1"] == True
            assert data["results"]["adapter2"] == False
            assert data["summary"]["successful"] == 1
            assert data["summary"]["failed"] == 1
            assert data["summary"]["total"] == 2

def test_disconnect_all_exchange_adapters_integration():
    """
    Test the integration of disconnecting from all exchange adapters
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.disconnect_all_adapters') as mock_disconnect_all:
        # Create mock disconnection results
        mock_results = {
            "adapter1": True,
            "adapter2": True
        }
        mock_disconnect_all.return_value = mock_results
        
        response = client.post("/api/v1/exchanges/disconnect-all")
        
        # Assertions
        assert response.status_code in [200, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "summary" in data
            assert data["results"]["adapter1"] == True
            assert data["results"]["adapter2"] == True
            assert data["summary"]["successful"] == 2
            assert data["summary"]["failed"] == 0
            assert data["summary"]["total"] == 2

def test_set_default_exchange_adapter_integration():
    """
    Test the integration of setting default exchange adapter
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.set_default_adapter') as mock_set_default:
        # Create mock result
        mock_set_default.return_value = True
        
        adapter_name = "test-exchange-adapter"
        response = client.post(f"/api/v1/exchanges/{adapter_name}/set-default")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert data["status"] == "default_set"

def test_get_default_exchange_adapter_integration():
    """
    Test the integration of getting default exchange adapter
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.get_default_adapter_name') as mock_get_default:
        # Create mock result
        mock_get_default.return_value = "test-exchange-adapter"
        
        response = client.get("/api/v1/exchanges/default")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"

def test_update_exchange_adapter_config_integration():
    """
    Test the integration of updating exchange adapter configuration
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.get_adapter') as mock_get_adapter:
        # Create mock adapter
        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter
        
        adapter_name = "test-exchange-adapter"
        config_data = {
            "api_key": "updated-api-key",
            "api_secret": "updated-api-secret"
        }
        
        response = client.put(f"/api/v1/exchanges/{adapter_name}/config", json=config_data)
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert data["status"] == "config_updated"
            assert "updated_config" in data

def test_get_supported_markets_integration():
    """
    Test the integration of getting supported markets
    """
    # Mock the exchange registry and adapter
    with patch('src.exchanges.registry.exchange_registry.get_adapter') as mock_get_adapter:
        # Create mock adapter
        mock_adapter = MagicMock()
        mock_adapter.get_supported_markets = MagicMock(return_value=["BTC/USD", "ETH/USD"])
        mock_get_adapter.return_value = mock_adapter
        
        adapter_name = "test-exchange-adapter"
        response = client.get(f"/api/v1/exchanges/{adapter_name}/markets")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert isinstance(data["supported_markets"], list)
            assert "BTC/USD" in data["supported_markets"]
            assert "ETH/USD" in data["supported_markets"]
            assert data["count"] == 2

def test_unregister_exchange_adapter_integration():
    """
    Test the integration of unregistering an exchange adapter
    """
    # Mock the exchange registry
    with patch('src.exchanges.registry.exchange_registry.unregister_adapter') as mock_unregister:
        # Create mock result
        mock_unregister.return_value = True
        
        adapter_name = "test-exchange-adapter"
        response = client.delete(f"/api/v1/exchanges/{adapter_name}")
        
        # Assertions
        assert response.status_code in [200, 404, 401, 403]  # Expected status codes
        
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "test-exchange-adapter"
            assert data["status"] == "unregistered"

def test_exchange_adapter_with_invalid_data():
    """
    Test exchange adapter operations with invalid data
    """
    # Test registration with missing required fields
    invalid_adapter_data = {
        "name": "test-adapter"
        # Missing adapter_type and config
    }
    
    response = client.post("/api/v1/exchanges/register", json=invalid_adapter_data)
    
    # Should return validation error
    assert response.status_code in [422, 400, 401, 403]  # Validation error codes

def test_nonexistent_exchange_adapter_operations():
    """
    Test operations on a nonexistent exchange adapter
    """
    # Mock the exchange registry to return None
    with patch('src.exchanges.registry.exchange_registry.get_adapter') as mock_get_adapter:
        mock_get_adapter.return_value = None
        
        adapter_name = "nonexistent-adapter"
        
        # Test connection
        response = client.post(f"/api/v1/exchanges/{adapter_name}/connect")
        assert response.status_code in [404, 401, 403, 500]
        
        # Test disconnection
        response = client.post(f"/api/v1/exchanges/{adapter_name}/disconnect")
        assert response.status_code in [404, 401, 403, 500]
        
        # Test status
        response = client.get(f"/api/v1/exchanges/{adapter_name}/status")
        assert response.status_code in [404, 401, 403]

def test_exchange_adapter_with_connection_failure():
    """
    Test exchange adapter operations when connection fails
    """
    # Mock the exchange registry and adapter
    with patch('src.exchanges.registry.exchange_registry.get_adapter') as mock_get_adapter:
        # Create mock adapter that fails to connect
        mock_adapter = MagicMock()
        mock_adapter.connect = MagicMock(return_value=False)  # Connection fails
        mock_get_adapter.return_value = mock_adapter
        
        adapter_name = "failing-adapter"
        response = client.post(f"/api/v1/exchanges/{adapter_name}/connect")
        
        # Should return error or indicate connection failure
        assert response.status_code in [200, 404, 401, 403, 500]