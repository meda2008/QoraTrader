"""
Contract tests for strategy dashboard endpoints
These tests verify that the strategy dashboard API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_strategy_dashboard_contract():
    """
    Test the contract for strategy dashboard endpoint (get all strategies status)
    """
    response = client.get("/api/v1/strategy-dashboard/status")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return a list of strategy status objects
        assert isinstance(data, list)
        if len(data) > 0:
            # Each strategy status should have certain fields
            first_strategy = data[0]
            expected_fields = ["id", "name", "status", "cumulative_return", "created_at"]
            for field in expected_fields:
                assert field in first_strategy

def test_strategy_specific_status_contract():
    """
    Test the contract for getting specific strategy status
    """
    strategy_id = "dummy-strategy-id"
    response = client.get(f"/api/v1/strategy-dashboard/{strategy_id}/status")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = ["id", "name", "status", "cumulative_return", "created_at"]
        for field in expected_fields:
            assert field in data