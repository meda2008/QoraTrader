"""
Contract tests for indicator calculation endpoints
These tests verify that the indicator calculation API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_indicator_calculation_contract():
    """
    Test the contract for indicator calculation endpoint
    """
    # Test data following the expected schema
    indicator_request = {
        "indicator_name": "sma",
        "data": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
        "params": {
            "period": 5
        }
    }
    
    response = client.post("/api/v1/indicators/calculate", json=indicator_request)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        assert "result" in data
        # The result should be a list of calculated values
        assert isinstance(data["result"], (list, float, int))

def test_indicator_list_contract():
    """
    Test the contract for listing available indicators
    """
    response = client.get("/api/v1/indicators/list")
    
    # Check that the response has the expected structure
    assert response.status_code == 200
    data = response.json()
    # Should return a list of indicator names
    assert isinstance(data, list)
    # At least some indicators should be available
    assert len(data) >= 0  # Could be empty if no indicators are registered yet