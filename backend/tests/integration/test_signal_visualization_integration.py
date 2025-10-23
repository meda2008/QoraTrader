"""
Integration tests for signal and trade visualization
These tests verify that the signal and trade visualization functions correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_signal_trade_visualization_integration():
    """
    Test the integration of signal and trade visualization
    """
    # Mock the visualization service
    with patch('src.services.visualization_service.visualization_service.get_signal_trade_visualization_data') as mock_get_visualization:
        # Create mock visualization data
        mock_visualization_data = {
            "symbol": "AAPL",
            "strategy_id": "test-strategy-123",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "price_data": [
                {"timestamp": "2023-01-01T00:00:00", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000}
            ],
            "trades": [
                {
                    "id": "trade-1",
                    "symbol": "AAPL",
                    "side": "buy",
                    "quantity": 100,
                    "price": 100.0,
                    "executed_at": "2023-01-01T10:00:00",
                    "commission": 0.1
                }
            ],
            "signals": [
                {
                    "timestamp": "2023-01-01T09:30:00",
                    "type": "BUY",
                    "price": 99.5
                }
            ],
            "summary": {
                "total_trades": 1,
                "total_signals": 1,
                "trade_success_rate": 1.0
            }
        }
        mock_get_visualization.return_value = mock_visualization_data
        
        # Call the visualization endpoint
        response = client.get(
            "/api/v1/visualization/signal-trade-visualization",
            params={
                "strategy_id": "test-strategy-123",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["strategy_id"] == "test-strategy-123"
        assert len(data["price_data"]) == 1
        assert len(data["trades"]) == 1
        assert len(data["signals"]) == 1
        assert data["summary"]["total_trades"] == 1

def test_signal_trade_visualization_with_no_data():
    """
    Test visualization when there's no data for the specified period
    """
    # Mock the visualization service to return empty data
    with patch('src.services.visualization_service.visualization_service.get_signal_trade_visualization_data') as mock_get_visualization:
        mock_get_visualization.return_value = {
            "symbol": "AAPL",
            "strategy_id": "test-strategy-123",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "price_data": [],
            "trades": [],
            "signals": [],
            "summary": {
                "total_trades": 0,
                "total_signals": 0,
                "trade_success_rate": 0.0
            }
        }
        
        response = client.get(
            "/api/v1/visualization/signal-trade-visualization",
            params={
                "strategy_id": "test-strategy-123",
                "symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["price_data"]) == 0
        assert len(data["trades"]) == 0
        assert len(data["signals"]) == 0