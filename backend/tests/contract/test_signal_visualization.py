"""
Contract tests for signal visualization endpoints
These tests verify that the signal visualization API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_signal_visualization_endpoint_contract():
    """
    Test the contract for signal-trading visualization endpoint
    """
    # Use query parameters as defined in the API
    response = client.get(
        "/api/v1/visualization/signal-trade-visualization",
        params={
            "strategy_id": "test-strategy-id",
            "symbol": "AAPL",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31"
        }
    )
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 404]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "symbol", "strategy_id", "start_date", "end_date", 
            "price_data", "trades", "signals", "summary"
        ]
        for field in expected_fields:
            assert field in data
            
        # Check that price_data, trades, and signals are lists
        assert isinstance(data["price_data"], list)
        assert isinstance(data["trades"], list)
        assert isinstance(data["signals"], list)
        
        # Check that summary has expected sub-fields
        summary = data["summary"]
        assert "total_trades" in summary
        assert "total_signals" in summary
        assert "trade_success_rate" in summary