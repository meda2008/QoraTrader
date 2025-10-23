"""
Integration tests for detailed report retrieval
These tests verify that the detailed strategy report retrieval functions correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_detailed_report_retrieval():
    """
    Test the retrieval of detailed strategy reports
    """
    # Mock the strategy report service
    with patch('src.services.strategy_report_service.strategy_report_service.get_strategy_report') as mock_get_report:
        # Create mock report data
        mock_report_data = {
            "strategy_id": "strategy-1",
            "strategy_name": "Test Strategy",
            "strategy_description": "A test strategy",
            "created_at": "2023-01-01T00:00:00",
            "performance_metrics": {
                "total_trades": 150,
                "win_rate": 0.6,
                "total_return": 0.15,
                "sharpe_ratio": 1.2,
                "max_drawdown": 0.05,
                "profit_factor": 1.8
            },
            "equity_curve": [
                {"date": "2023-01-01", "value": 100000},
                {"date": "2023-01-02", "value": 100500},
                {"date": "2023-01-03", "value": 101200}
            ],
            "recent_trades": [
                {
                    "id": "trade-1",
                    "symbol": "AAPL",
                    "side": "buy",
                    "quantity": 100,
                    "price": 150.0,
                    "executed_at": "2023-01-01T10:00:00"
                }
            ],
            "backtest_reports": [
                {
                    "id": "report-1",
                    "start_date": "2023-01-01",
                    "end_date": "2023-12-31",
                    "initial_capital": 100000.0,
                    "final_capital": 115000.0,
                    "total_return": 0.15
                }
            ]
        }
        mock_get_report.return_value = mock_report_data
        
        response = client.get("/api/v1/strategy-details/strategy-1/report")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["strategy_id"] == "strategy-1"
        assert data["strategy_name"] == "Test Strategy"
        assert len(data["equity_curve"]) == 3
        assert len(data["recent_trades"]) == 1
        assert len(data["backtest_reports"]) == 1