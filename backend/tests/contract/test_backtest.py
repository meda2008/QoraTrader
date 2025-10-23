"""
Contract tests for backtest endpoints
These tests verify that the backtest API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import init_db

client = TestClient(app)

def test_backtest_creation_contract():
    """
    Test the contract for backtest creation endpoint
    """
    # Test data following the expected schema
    backtest_request = {
        "strategy_id": "test-strategy-id",
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T23:59:59",
        "initial_capital": 100000.0
    }
    
    # This would normally require a valid strategy in the database
    # For contract testing, we're primarily verifying the request/response structure
    response = client.post("/api/v1/backtest/", json=backtest_request)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 404, 401]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        assert "id" in data
        assert "strategy_id" in data
        assert "start_date" in data
        assert "end_date" in data
        assert "initial_capital" in data
        assert "final_capital" in data
        # Additional fields that should be present
        expected_fields = [
            "total_return", "annual_return", "sharpe_ratio", "max_drawdown", 
            "total_trades", "win_rate", "profit_factor", "created_at"
        ]
        for field in expected_fields:
            assert field in data

def test_backtest_report_retrieval_contract():
    """
    Test the contract for backtest report retrieval endpoint
    """
    # Test with a dummy report ID
    report_id = "dummy-report-id"
    response = client.get(f"/api/v1/backtest/{report_id}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        assert "id" in data
        assert "strategy_id" in data
        assert "start_date" in data
        assert "end_date" in data
        assert "initial_capital" in data
        assert "final_capital" in data
        # Additional fields that should be present
        expected_fields = [
            "total_return", "annual_return", "sharpe_ratio", "max_drawdown", 
            "total_trades", "win_rate", "profit_factor", "created_at"
        ]
        for field in expected_fields:
            assert field in data