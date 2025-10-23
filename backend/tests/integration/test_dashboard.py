"""
Integration tests for dashboard data retrieval
These tests verify that the dashboard data retrieval functions correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_dashboard_data_retrieval():
    """
    Test the retrieval of dashboard data
    """
    # Mock the strategy monitor service
    with patch('src.services.strategy_monitor.strategy_monitor_service.get_all_strategies_status') as mock_get_status:
        # Create mock strategy status data
        mock_status_data = [
            {
                "id": "strategy-1",
                "name": "Test Strategy 1",
                "status": "running",
                "cumulative_return": 0.10,
                "created_at": "2023-01-01T00:00:00"
            },
            {
                "id": "strategy-2", 
                "name": "Test Strategy 2",
                "status": "stopped",
                "cumulative_return": -0.05,
                "created_at": "2023-01-02T00:00:00"
            }
        ]
        mock_get_status.return_value = mock_status_data
        
        response = client.get("/api/v1/strategy-dashboard/status")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]["id"] == "strategy-1"
        assert data[1]["id"] == "strategy-2"

def test_specific_strategy_status():
    """
    Test retrieving status for a specific strategy
    """
    # Mock the strategy monitor service
    with patch('src.services.strategy_monitor.strategy_monitor_service.get_strategy_status') as mock_get_status:
        # Create mock strategy status data
        mock_status_data = {
            "id": "strategy-1",
            "name": "Test Strategy 1",
            "status": "running",
            "cumulative_return": 0.10,
            "created_at": "2023-01-01T00:00:00"
        }
        mock_get_status.return_value = mock_status_data
        
        response = client.get("/api/v1/strategy-dashboard/strategy-1/status")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "strategy-1"
        assert data["status"] == "running"