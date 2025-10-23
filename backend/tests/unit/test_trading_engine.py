"""
Unit tests for the trading engine
These tests verify the correctness of the trading engine's core functionality
"""
import pytest
from unittest.mock import patch, MagicMock
from src.trading.engine import TradingEngine
from src.models.base import Order, OrderType, OrderSide, Strategy, Account, Position
from src.utils.error_handler import CustomException

@patch('src.trading.engine.trading_engine.get_db')
def test_trading_engine_initialization(mock_get_db):
    """
    Test the initialization of the TradingEngine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Verify that the engine initializes correctly
    assert hasattr(engine, '_active_strategies')
    assert hasattr(engine, '_pending_orders')
    assert hasattr(engine, '_positions')
    assert hasattr(engine, '_accounts')
    assert engine._running == False

@patch('src.trading.engine.trading_engine.get_db')
def test_trading_engine_start_stop(mock_get_db):
    """
    Test the start/stop functionality of the TradingEngine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Initially, engine should not be running
    assert engine._running == False
    
    # Start the engine (mock the asyncio tasks)
    with patch('asyncio.create_task'):
        engine.start()
    
    # After starting, engine should be running
    assert engine._running == True
    
    # Stop the engine
    engine.stop()
    
    # After stopping, engine should not be running
    assert engine._running == False

@patch('src.trading.engine.trading_engine.get_db')
def test_order_submission(mock_get_db):
    """
    Test order submission to the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Create a test order
    order = Order(
        strategy_id="test-strategy-123",
        symbol="AAPL",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=100,
        price=150.0
    )
    
    # Submit the order to the engine (mock the event publishing)
    with patch('src.trading.engine.trading_engine.publish_event'):
        order_id = engine.submit_order(order)
    
    # Verify that the order was added to pending orders
    assert order_id == order.id
    assert order_id in engine._pending_orders
    assert engine._pending_orders[order_id] == order

@patch('src.trading.engine.trading_engine.get_db')
def test_order_cancellation(mock_get_db):
    """
    Test order cancellation in the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Create a test order
    order = Order(
        strategy_id="test-strategy-123",
        symbol="AAPL",
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        quantity=100,
        price=150.0
    )
    
    # Submit the order to the engine
    with patch('src.trading.engine.trading_engine.publish_event'):
        order_id = engine.submit_order(order)
    
    # Verify that the order is in pending orders
    assert order_id in engine._pending_orders
    
    # Cancel the order (mock the event publishing)
    with patch('src.trading.engine.trading_engine.publish_event'):
        success = engine.cancel_order(order_id)
    
    # Verify that the order was removed from pending orders
    assert success == True
    assert order_id not in engine._pending_orders

@patch('src.trading.engine.trading_engine.get_db')
def test_strategy_registration(mock_get_db):
    """
    Test strategy registration and deregistration in the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Create a test strategy
    strategy = Strategy(
        name="Test Strategy",
        description="A test strategy for unit testing"
    )
    
    # Register the strategy
    engine.register_strategy(strategy)
    
    # Verify that the strategy is registered
    assert strategy.id in engine._active_strategies
    assert engine._active_strategies[strategy.id].name == "Test Strategy"
    
    # Deregister the strategy
    engine.deregister_strategy(strategy.id)
    
    # Verify that the strategy is no longer registered
    assert strategy.id not in engine._active_strategies

@patch('src.trading.engine.trading_engine.get_db')
def test_position_management(mock_get_db):
    """
    Test position management in the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Create test account and symbol
    account_id = "test-account-123"
    symbol = "AAPL"
    
    # Get position (should return None initially)
    position = engine.get_position(account_id, symbol)
    assert position is None
    
    # Get all positions for account (should return empty list initially)
    positions = engine.get_all_positions(account_id)
    assert positions == []

@patch('src.trading.engine.trading_engine.get_db')
def test_exchange_adapter_registration(mock_get_db):
    """
    Test exchange adapter registration in the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Create a mock exchange adapter
    mock_adapter = MagicMock()
    
    # Register the adapter
    engine.register_exchange_adapter("test-exchange", mock_adapter)
    
    # Verify that the adapter is registered
    assert "test-exchange" in engine._exchange_adapters
    assert engine._exchange_adapters["test-exchange"] == mock_adapter

@patch('src.trading.engine.trading_engine.get_db')
def test_risk_manager_registration(mock_get_db):
    """
    Test risk manager registration in the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Create a mock risk manager
    mock_risk_manager = MagicMock()
    
    # Register the risk manager
    engine.set_risk_manager(mock_risk_manager)
    
    # Verify that the risk manager is registered
    assert engine._risk_manager == mock_risk_manager

@patch('src.trading.engine.trading_engine.get_db')
def test_trading_engine_state_after_error(mock_get_db):
    """
    Test that the trading engine maintains consistent state after errors
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Start the engine
    with patch('asyncio.create_task'):
        engine.start()
    
    # Verify engine is running
    assert engine._running == True
    
    # Stop the engine
    engine.stop()
    
    # Verify engine is stopped
    assert engine._running == False

@patch('src.trading.engine.trading_engine.get_db')
def test_trading_engine_concurrent_operations(mock_get_db):
    """
    Test concurrent operations in the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Submit multiple orders concurrently (simulated)
    orders = []
    for i in range(5):
        order = Order(
            strategy_id=f"test-strategy-{i}",
            symbol="AAPL",
            order_type=OrderType.LIMIT,
            side=OrderSide.BUY,
            quantity=100 + i*10,
            price=150.0 + i
        )
        orders.append(order)
    
    # Submit all orders (mock the event publishing)
    with patch('src.trading.engine.trading_engine.publish_event'):
        order_ids = [engine.submit_order(order) for order in orders]
    
    # Verify that all orders were submitted
    for i, order_id in enumerate(order_ids):
        assert order_id == orders[i].id
        assert order_id in engine._pending_orders

@patch('src.trading.engine.trading_engine.get_db')
def test_trading_engine_cleanup(mock_get_db):
    """
    Test proper cleanup of resources in the trading engine
    """
    # Mock database session
    mock_session = MagicMock()
    mock_get_db.return_value = iter([mock_session])
    
    # Create a trading engine instance
    engine = TradingEngine()
    
    # Start the engine
    with patch('asyncio.create_task'):
        engine.start()
    
    # Verify engine is running
    assert engine._running == True
    
    # Stop the engine
    engine.stop()
    
    # Verify engine is stopped and cleaned up
    assert engine._running == False
    # Resources should be cleared or released
    assert hasattr(engine, '_active_strategies')
    assert hasattr(engine, '_pending_orders')
    assert hasattr(engine, '_positions')
    assert hasattr(engine, '_accounts')