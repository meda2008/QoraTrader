"""
Contract tests for risk rule configuration endpoints
These tests verify that the risk rule configuration API endpoints conform to the expected contract
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_get_risk_rules_endpoint_contract():
    """
    Test the contract for getting all risk rules endpoint
    """
    response = client.get("/api/v1/risk-rules/")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return a list of risk rules
        assert isinstance(data, list)
        if len(data) > 0:
            # Each rule should have certain fields
            first_rule = data[0]
            expected_fields = [
                "id", "strategy_id", "max_position_size", "max_order_size", 
                "max_daily_loss", "max_drawdown", "position_limit_per_symbol", 
                "daily_order_limit", "order_frequency_limit", "risk_level", 
                "is_active", "created_at", "updated_at"
            ]
            for field in expected_fields:
                assert field in first_rule

def test_get_single_risk_rule_endpoint_contract():
    """
    Test the contract for getting a single risk rule endpoint
    """
    rule_id = "test-rule-id"
    response = client.get(f"/api/v1/risk-rules/{rule_id}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "id", "strategy_id", "max_position_size", "max_order_size", 
            "max_daily_loss", "max_drawdown", "position_limit_per_symbol", 
            "daily_order_limit", "order_frequency_limit", "risk_level", 
            "is_active", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data

def test_create_risk_rule_endpoint_contract():
    """
    Test the contract for creating a risk rule endpoint
    """
    risk_rule_data = {
        "max_position_size": 1000000,
        "max_order_size": 100000,
        "max_daily_loss": 50000,
        "max_drawdown": 0.1,
        "risk_level": "medium"
    }
    
    response = client.post("/api/v1/risk-rules/", json=risk_rule_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "id", "strategy_id", "max_position_size", "max_order_size", 
            "max_daily_loss", "max_drawdown", "position_limit_per_symbol", 
            "daily_order_limit", "order_frequency_limit", "risk_level", 
            "is_active", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data

def test_update_risk_rule_endpoint_contract():
    """
    Test the contract for updating a risk rule endpoint
    """
    rule_id = "test-rule-id"
    update_data = {
        "max_daily_loss": 75000
    }
    
    response = client.put(f"/api/v1/risk-rules/{rule_id}", json=update_data)
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 404, 422, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Check for expected fields in the response
        expected_fields = [
            "id", "strategy_id", "max_position_size", "max_order_size", 
            "max_daily_loss", "max_drawdown", "position_limit_per_symbol", 
            "daily_order_limit", "order_frequency_limit", "risk_level", 
            "is_active", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data

def test_get_risk_rules_by_strategy_endpoint_contract():
    """
    Test the contract for getting risk rules by strategy endpoint
    """
    strategy_id = "test-strategy-id"
    response = client.get(f"/api/v1/risk-rules/strategy/{strategy_id}")
    
    # Check that the response has the expected structure
    assert response.status_code in [200, 401, 403]  # Expected status codes
    
    if response.status_code == 200:
        data = response.json()
        # Should return a list of risk rules
        assert isinstance(data, list)
        if len(data) > 0:
            # Each rule should have certain fields
            first_rule = data[0]
            expected_fields = [
                "id", "strategy_id", "max_position_size", "max_order_size", 
                "max_daily_loss", "max_drawdown", "position_limit_per_symbol", 
                "daily_order_limit", "order_frequency_limit", "risk_level", 
                "is_active", "created_at", "updated_at"
            ]
            for field in expected_fields:
                assert field in first_rule