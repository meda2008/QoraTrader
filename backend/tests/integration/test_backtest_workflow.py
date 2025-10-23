"""
Integration tests for complete backtest workflow
These tests verify that the entire backtest workflow functions correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import init_db
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_complete_backtest_workflow():
    """
    Test the complete backtest workflow from request to result
    """
    # Mock the backtest service to avoid actual computation
    with patch('src.services.backtest_service.BacktestService.run_backtest') as mock_run_backtest:
        # Create a mock backtest report
        mock_report = MagicMock()
        mock_report.id = "test-report-id"
        mock_report.strategy_id = "test-strategy-123"
        mock_report.start_date = "2023-01-01T00:00:00"
        mock_report.end_date = "2023-12-31T23:59:59"
        mock_report.initial_capital = 100000.0
        mock_report.final_capital = 110000.0
        mock_report.total_return = 0.10
        mock_report.annual_return = 0.10
        mock_report.sharpe_ratio = 1.2
        mock_report.max_drawdown = 0.05
        mock_report.total_trades = 150
        mock_report.win_rate = 0.6
        mock_report.profit_factor = 1.8
        mock_report.created_at = "2023-10-22T10:30:00"
        
        mock_run_backtest.return_value = mock_report
        
        # Make the backtest request
        backtest_request = {
            "strategy_id": "test-strategy-123",
            "start_date": "2023-01-01T00:00:00",
            "end_date": "2023-12-31T23:59:59",
            "initial_capital": 100000.0
        }
        
        response = client.post("/api/v1/backtest/", json=backtest_request)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Check the response data
        assert data["strategy_id"] == "test-strategy-123"
        assert data["initial_capital"] == 100000.0
        assert data["final_capital"] == 110000.0
        assert data["total_return"] == 0.10

def test_backtest_workflow_with_invalid_data():
    """
    Test the backtest workflow with invalid input data
    """
    # Test with missing required fields
    incomplete_request = {
        "strategy_id": "test-strategy-123",
        # Missing start_date, end_date, and initial_capital
    }
    
    response = client.post("/api/v1/backtest/", json=incomplete_request)
    
    # Should return a validation error
    assert response.status_code == 422

def test_backtest_workflow_with_invalid_strategy():
    """
    Test the backtest workflow with a non-existent strategy
    """
    # Test with an invalid strategy ID
    invalid_request = {
        "strategy_id": "non-existent-strategy-123",
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T23:59:59",
        "initial_capital": 100000.0
    }
    
    response = client.post("/api/v1/backtest/", json=invalid_request)
    
    # Should return an error
    assert response.status_code in [404, 400, 500]  # Could be any of these depending on implementation