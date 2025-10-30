from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
import logging
from src.models import Order, Strategy, Account, Position, Trade
from src.events.bus import publish_event, EventType
from src.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class OrderExecutionResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"

@dataclass
class ExecutionReport:
    order_id: str
    execution_result: OrderExecutionResult
    filled_quantity: float
    average_fill_price: float
    commission: float
    timestamp: datetime
    message: str = ""

class TradingEngine:
    """
    Core trading engine that handles order execution, risk management, and position tracking
    """
    
    def __init__(self):
        self._active_strategies: Dict[str, Strategy] = {}
        self._pending_orders: Dict[str, Order] = {}
        self._positions: Dict[str, Position] = {}
        self._accounts: Dict[str, Account] = {}
        self._exchange_adapters = {}
        self._risk_manager = None  # To be set later
        self._running = False
        
        logger.info("Trading engine initialized")
    
    async def start(self):
        """
        Start the trading engine
        """
        self._running = True
        logger.info("Trading engine started")
        
        # Start the main execution loop
        asyncio.create_task(self._execution_loop())
        
    async def stop(self):
        """
        Stop the trading engine
        """
        self._running = False
        logger.info("Trading engine stopped")
    
    async def _execution_loop(self):
        """
        Main execution loop for processing orders
        """
        while self._running:
            try:
                # Process pending orders
                await self._process_pending_orders()
                
                # Sleep briefly to avoid busy waiting
                await asyncio.sleep(0.01)  # 10ms
            except Exception as e:
                logger.error(f"Error in trading engine execution loop: {str(e)}")
                
    async def _process_pending_orders(self):
        """
        Process all pending orders
        """
        for order_id, order in list(self._pending_orders.items()):
            try:
                # Check if order is still valid
                if order.status.value in ["cancelled", "filled", "rejected"]:
                    del self._pending_orders[order_id]
                    continue
                
                # Execute the order
                result = await self._execute_order(order)
                
                # Update order status based on execution result
                if result.execution_result == OrderExecutionResult.SUCCESS:
                    order.status = "filled"
                    order.executed_at = result.timestamp
                elif result.execution_result == OrderExecutionResult.FAILED:
                    order.status = "rejected"
                elif result.execution_result == OrderExecutionResult.CANCELLED:
                    order.status = "cancelled"
                
                # Update position if order was filled
                if result.execution_result == OrderExecutionResult.SUCCESS:
                    await self._update_position(order, result)
                
                # Publish order update event
                await publish_event(
                    EventType.ORDER_UPDATE,
                    {
                        "order_id": order.id,
                        "status": order.status.value,
                        "filled_quantity": result.filled_quantity,
                        "average_fill_price": result.average_fill_price
                    },
                    source="trading_engine"
                )
                
                # Remove from pending orders if completed
                if order.status.value in ["filled", "cancelled", "rejected"]:
                    del self._pending_orders[order_id]
                    
            except Exception as e:
                logger.error(f"Error processing order {order_id}: {str(e)}")
    
    async def _execute_order(self, order: Order) -> ExecutionReport:
        """
        Execute an order through the appropriate exchange adapter
        """
        logger.info(f"Executing order {order.id} for {order.quantity} of {order.symbol}")
        
        # In a real implementation, this would connect to actual exchanges
        # For now, we'll simulate execution
        try:
            # Simulate execution delay
            await asyncio.sleep(0.01)  # 10ms
            
            # For simulation, assume all orders fill at the specified price
            # In real implementation, this would connect to exchange APIs
            execution_price = order.price if order.price > 0 else 100.0  # Default price if market order
            execution_quantity = order.quantity
            
            # Simulate partial fills by reducing quantity slightly randomly
            import random
            if random.random() > 0.8:  # 20% chance of partial fill
                execution_quantity = execution_quantity * random.uniform(0.7, 0.95)
            
            # Simulate commission (0.03% for stock trading)
            commission = execution_price * execution_quantity * 0.0003
            
            return ExecutionReport(
                order_id=order.id,
                execution_result=OrderExecutionResult.SUCCESS,
                filled_quantity=execution_quantity,
                average_fill_price=execution_price,
                commission=commission,
                timestamp=datetime.utcnow(),
                message="Order filled successfully"
            )
        except Exception as e:
            logger.error(f"Failed to execute order {order.id}: {str(e)}")
            return ExecutionReport(
                order_id=order.id,
                execution_result=OrderExecutionResult.FAILED,
                filled_quantity=0.0,
                average_fill_price=0.0,
                commission=0.0,
                timestamp=datetime.utcnow(),
                message=str(e)
            )
    
    async def _update_position(self, order: Order, execution_report: ExecutionReport):
        """
        Update position based on order execution
        """
        # Create or get existing position
        position_key = f"{order.account_id}_{order.symbol}"
        position = self._positions.get(position_key)
        
        if not position:
            # Create new position
            from src.models.base import PositionDirection
            direction = PositionDirection.LONG if order.side.value == "buy" else PositionDirection.SHORT
            
            position = Position(
                account_id=order.account_id,
                strategy_id=order.strategy_id,
                symbol=order.symbol,
                direction=direction,
                volume=execution_report.filled_quantity,
                available_volume=execution_report.filled_quantity,
                avg_price=execution_report.average_fill_price,
                unrealized_pnl=0.0,
                realized_pnl=0.0
            )
            self._positions[position_key] = position
        else:
            # Update existing position
            # This is a simplified calculation - in reality, you'd want more complex position management
            old_volume = position.volume
            old_avg_price = position.avg_price
            
            if order.side.value == "buy":
                # Buying increases position size
                new_volume = old_volume + execution_report.filled_quantity
                new_avg_price = (
                    (old_volume * old_avg_price + 
                     execution_report.filled_quantity * execution_report.average_fill_price) / 
                    new_volume
                )
            else:
                # Selling decreases position size
                new_volume = old_volume - execution_report.filled_quantity
                new_avg_price = old_avg_price  # Average price doesn't change when selling
            
            position.volume = new_volume
            position.avg_price = new_avg_price
            position.available_volume = new_volume  # Simplified calculation
            
            # If position is closed, update realized PnL
            if new_volume == 0:
                from src.models.base import PositionDirection
                # Calculate PnL based on average open and close prices
                if position.direction == PositionDirection.LONG:
                    pnl = (execution_report.average_fill_price - old_avg_price) * execution_report.filled_quantity
                else:  # SHORT
                    pnl = (old_avg_price - execution_report.average_fill_price) * execution_report.filled_quantity
                
                position.realized_pnl += pnl
        
        # Publish position update event
        await publish_event(
            EventType.POSITION_UPDATE,
            {
                "position_id": position.id,
                "account_id": position.account_id,
                "symbol": position.symbol,
                "volume": position.volume,
                "avg_price": position.avg_price,
                "unrealized_pnl": position.unrealized_pnl,
                "realized_pnl": position.realized_pnl
            },
            source="trading_engine"
        )
    
    async def submit_order(self, order: Order) -> str:
        """
        Submit an order to the trading engine for execution
        """
        logger.info(f"Submitting order {order.id} for {order.quantity} of {order.symbol}")
        
        # Add order to pending queue
        self._pending_orders[order.id] = order
        
        # Publish order event
        await publish_event(
            EventType.ORDER_UPDATE,
            {
                "order_id": order.id,
                "status": order.status.value,
                "symbol": order.symbol,
                "quantity": order.quantity,
                "side": order.side.value,
                "order_type": order.order_type.value
            },
            source="trading_engine"
        )
        
        return order.id
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel a pending order
        """
        if order_id in self._pending_orders:
            order = self._pending_orders[order_id]
            order.status = "cancelled"
            
            # Publish cancellation event
            await publish_event(
                EventType.ORDER_UPDATE,
                {
                    "order_id": order_id,
                    "status": "cancelled"
                },
                source="trading_engine"
            )
            
            # Remove from pending orders
            del self._pending_orders[order_id]
            logger.info(f"Order {order_id} cancelled successfully")
            return True
        else:
            logger.warning(f"Attempt to cancel non-existent order {order_id}")
            return False
    
    def register_strategy(self, strategy: Strategy):
        """
        Register a strategy with the trading engine
        """
        self._active_strategies[strategy.id] = strategy
        logger.info(f"Strategy {strategy.name} ({strategy.id}) registered with trading engine")
    
    def deregister_strategy(self, strategy_id: str):
        """
        Deregister a strategy from the trading engine
        """
        if strategy_id in self._active_strategies:
            del self._active_strategies[strategy_id]
            logger.info(f"Strategy {strategy_id} deregistered from trading engine")
    
    async def get_position(self, account_id: str, symbol: str) -> Optional[Position]:
        """
        Get the position for a specific account and symbol
        """
        position_key = f"{account_id}_{symbol}"
        return self._positions.get(position_key)
    
    async def get_all_positions(self, account_id: str) -> List[Position]:
        """
        Get all positions for a specific account
        """
        return [pos for pos in self._positions.values() if pos.account_id == account_id]
    
    def register_exchange_adapter(self, exchange_name: str, adapter):
        """
        Register an exchange adapter
        """
        self._exchange_adapters[exchange_name] = adapter
        logger.info(f"Exchange adapter for {exchange_name} registered")
    
    def set_risk_manager(self, risk_manager):
        """
        Set the risk manager for the trading engine
        """
        self._risk_manager = risk_manager
        logger.info("Risk manager registered with trading engine")

# Global trading engine instance
trading_engine = TradingEngine()

async def initialize_trading_engine():
    """
    Initialize the trading engine
    """
    await trading_engine.start()
    logger.info("Trading engine initialized and started")