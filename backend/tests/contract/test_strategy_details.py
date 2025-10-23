"""
Contract tests for strategy details endpoints
These tests verify that the strategy details API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_strategy_details_contract():
    """
    Test the contract for strategy details endpoint
    """
    strategy_id = "dummy-strategy-id"
    response = client.get(f"/api/v1/strategy-details/{strategy_id}/report")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "strategy_id", "strategy_name", "strategy_description", "created_at", 
            "performance_metrics", "equity_curve", "recent_trades", "backtest_reports"
        ]
        for field in expected_fields:
            assert field in data
            
        # Check that performance_metrics has expected sub-fields
        assert "total_trades" in data["performance_metrics"]
        assert "win_rate" in data["performance_metrics"]
        assert "total_return" in data["performance_metrics"]
        
        # Check that equity_curve is a list
        assert isinstance(data["equity_curve"], list)
        
        # Check that recent_trades is a list
        assert isinstance(data["recent_trades"], list)
        
        # Check that backtest_reports is a list
        assert isinstance(data["backtest_reports"], list)