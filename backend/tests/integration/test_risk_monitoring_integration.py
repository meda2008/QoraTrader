"""
Integration tests for risk monitoring functionality
These tests verify that the risk monitoring functions correctly
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_account_risk_metrics_integration():
    """
    Test the integration of account risk metrics
    """
    # Mock the risk metrics service
    with patch('src.services.risk_metrics_service.risk_metrics_service.calculate_account_risk_metrics') as mock_calc_risk:
        # Create mock risk metrics data
        mock_risk_data = {
            "account_id": "test-account-123",
            "total_market_value": 100000.0,
            "total_pnl": 5000.0,
            "available_balance": 80000.0,
            "risk_level": "medium",
            "concentration_risk": 0.3,
            "position_count": 5,
            "last_updated": "2023-10-22T10:30:00Z"
        }
        mock_calc_risk.return_value = mock_risk_data
        
        response = client.get("/api/v1/risk-monitoring/account-risk/test-account-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["account_id"] == "test-account-123"
        assert data["total_pnl"] == 5000.0
        assert data["risk_level"] == "medium"

def test_system_risk_metrics_integration():
    """
    Test the integration of system-wide risk metrics
    """
    # Mock the risk metrics service
    with patch('src.services.risk_metrics_service.risk_metrics_service.calculate_system_wide_risk_metrics') as mock_calc_system_risk:
        # Create mock system risk data
        mock_system_risk_data = {
            "total_accounts": 10,
            "total_market_value": 1000000.0,
            "total_pnl": 50000.0,
            "risk_distribution": {
                "low": 3,
                "medium": 5,
                "high": 2,
                "extreme": 0
            },
            "avg_concentration": 0.25,
            "last_updated": "2023-10-22T10:30:00Z"
        }
        mock_calc_system_risk.return_value = mock_system_risk_data
        
        response = client.get("/api/v1/risk-monitoring/system-risk")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total_accounts"] == 10
        assert data["risk_distribution"]["medium"] == 5

def test_volatile_positions_integration():
    """
    Test the integration of volatile positions detection
    """
    # Mock the risk metrics service
    with patch('src.services.risk_metrics_service.risk_metrics_service.get_volatile_positions') as mock_get_volatile:
        # Create mock volatile positions data
        mock_volatile_data = [
            {
                "position_id": "pos-1",
                "account_id": "acc-1",
                "symbol": "VOLATILE",
                "volume": 1000,
                "avg_price": 50.0,
                "current_value": 50000.0,
                "estimated_volatility": 0.08
            }
        ]
        mock_get_volatile.return_value = mock_volatile_data
        
        response = client.get("/api/v1/risk-monitoring/volatile-positions")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["symbol"] == "VOLATILE"
        assert data[0]["estimated_volatility"] == 0.08