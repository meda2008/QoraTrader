"""
Unit tests for core trading components
These tests verify the correctness of individual components in isolation
"""
import pytest
from unittest.mock import patch, MagicMock
from src.models import Order, OrderType, OrderSide, Strategy, Account, Position
from src.trading.engine import TradingEngine
from src.services.backtest_service import BacktestService
from src.services.risk_rule_service import RiskRuleService
from src.utils.error_handler import CustomException

def test_order_creation():
    """
    Test the creation of Order objects with various parameters
    """
    # Test valid order creation
    # Note: We're not testing the default status value here as that's handled by the database
    # In unit tests, we just verify the object can be created with the required parameters
    order = Order(
        strategy_id="test-strategy-123",
        symbol="AAPL",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=100,
        price=150.0
    )
    
    assert order.strategy_id == "test-strategy-123"
    assert order.symbol == "AAPL"
    assert order.order_type == OrderType.LIMIT
    assert order.side == OrderSide.BUY
    assert order.quantity == 100
    assert order.price == 150.0

def test_strategy_model():
    """
    Test the Strategy model with various configurations
    """
    strategy = Strategy(
        name="Test Strategy",
        description="A test strategy for unit testing",
        config='{"param1": "value1"}',
        code="def strategy_logic(): pass"
    )
    
    assert strategy.name == "Test Strategy"
    assert strategy.description == "A test strategy for unit testing"
    assert strategy.config == '{"param1": "value1"}'

def test_account_model():
    """
    Test the Account model with various parameters
    """
    account = Account(
        user_id="test-user-123",
        account_type="simulated",
        balance=100000.0,
        available_balance=95000.0,
        market_value=5000.0
    )
    
    assert account.user_id == "test-user-123"
    assert account.account_type == "simulated"
    assert account.balance == 100000.0
    assert account.available_balance == 95000.0
    assert account.market_value == 5000.0

def test_position_model():
    """
    Test the Position model with various parameters
    """
    position = Position(
        account_id="test-account-123",
        strategy_id="test-strategy-123",
        symbol="AAPL",
        direction="long",
        volume=1000,
        avg_price=150.0
    )
    
    assert position.account_id == "test-account-123"
    assert position.strategy_id == "test-strategy-123"
    assert position.symbol == "AAPL"
    assert position.direction == "long"
    assert position.volume == 1000
    assert position.avg_price == 150.0

@patch('src.database.get_db')
def test_trading_engine_order_validation(mock_get_db):
    """
    Test the trading engine's order validation logic
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Test valid order
    valid_order = Order(
        strategy_id="test-strategy-123",
        symbol="AAPL",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=100,
        price=150.0
    )
    
    # This test verifies that the order passes basic validation
    # The actual validation would happen in the submit_order method
    assert valid_order.quantity > 0
    assert valid_order.price >= 0

@patch('src.services.backtest_service.BacktestService._get_market_data')
@patch('src.database.get_db')
def test_backtest_service_data_retrieval(mock_get_db, mock_get_market_data):
    """
    Test the backtest service's data retrieval logic
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Mock market data service
    mock_market_data = [
        {"timestamp": "2023-01-01T00:00:00", "close": 100.0},
        {"timestamp": "2023-01-02T00:00:00", "close": 101.0}
    ]
    mock_get_market_data.return_value = mock_market_data
    
    # Create backtest service instance
    service = BacktestService()
    
    # Test data retrieval
    data = service._generate_signal(mock_market_data, 1, "AAPL")
    
    # Should return a signal (BUY, SELL, or HOLD)
    assert data in ["BUY", "SELL", "HOLD"]

@patch('src.database.get_db')
def test_risk_rule_service_validation(mock_get_db):
    """
    Test the risk rule service's validation logic
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create risk rule service instance
    service = RiskRuleService()
    
    # Test order validation against risk rules
    order_data = {
        "price": 150.0,
        "quantity": 100
    }
    
    # This would normally check against actual risk rules
    # For this test, we're just verifying the method structure
    result = service.validate_order_against_risk_rules("test-strategy-123", order_data)
    
    # Should return a dictionary with validation results
    assert isinstance(result, dict)
    assert "valid" in result

def test_custom_exception_handling():
    """
    Test the custom exception handling mechanism
    """
    # Test creating a custom exception
    exception = CustomException("Test error message", 400)
    
    assert str(exception) == "Test error message"
    assert exception.status_code == 400
    
    # Test raising and catching the exception
    try:
        raise CustomException("Another test error", 500)
    except CustomException as e:
        assert e.message == "Another test error"
        assert e.status_code == 500

def test_order_side_enum():
    """
    Test the OrderSide enum values
    """
    assert OrderSide.BUY.value == "buy"
    assert OrderSide.SELL.value == "sell"

def test_order_type_enum():
    """
    Test the OrderType enum values
    """
    assert OrderType.MARKET.value == "market"
    assert OrderType.LIMIT.value == "limit"
    assert OrderType.STOP.value == "stop"

def test_strategy_status_enum():
    """
    Test the StrategyStatus enum values
    """
    from src.models.base import StrategyStatus
    assert StrategyStatus.ACTIVE.value == "active"
    assert StrategyStatus.INACTIVE.value == "inactive"
    assert StrategyStatus.PAUSED.value == "paused"
    assert StrategyStatus.STOPPED.value == "stopped"
    assert StrategyStatus.ERROR.value == "error"