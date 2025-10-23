from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.models.base import Strategy, Order, Position
from src.services.indicator_service import IndicatorService
from src.services.market_data_service import MarketDataService
import logging

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    """
    Base class for all trading strategies
    """
    
    def __init__(self, strategy_id: str, name: str, config: Dict[str, Any]):
        self.strategy_id = strategy_id
        self.name = name
        self.config = config
        self.indicator_service = IndicatorService()
        self.market_data_service = MarketDataService()
        self.is_active = False
        
        # Initialize strategy parameters from config
        self._init_parameters()
    
    def _init_parameters(self):
        """
        Initialize strategy-specific parameters from config
        """
        pass  # To be overridden by subclasses
    
    def activate(self):
        """
        Activate the strategy
        """
        self.is_active = True
        logger.info(f"Strategy {self.name} ({self.strategy_id}) activated")
    
    def deactivate(self):
        """
        Deactivate the strategy
        """
        self.is_active = False
        logger.info(f"Strategy {self.name} ({self.strategy_id}) deactivated")
    
    @abstractmethod
    def on_bar(self, symbol: str, data: Dict[str, Any]):
        """
        Called on each bar update
        """
        pass
    
    @abstractmethod
    def on_tick(self, symbol: str, data: Dict[str, Any]):
        """
        Called on each tick update
        """
        pass
    
    @abstractmethod
    def on_order_update(self, order: Order):
        """
        Called when order status changes
        """
        pass
    
    @abstractmethod
    def on_position_update(self, position: Position):
        """
        Called when position changes
        """
        pass
    
    def calculate_indicator(self, indicator_name: str, data: Any, **kwargs) -> Any:
        """
        Calculate an indicator using the indicator service
        """
        return self.indicator_service.calculate(indicator_name, data, **kwargs)
    
    def get_market_data(self, symbol: str, data_type: str, start_time: Optional[str] = None, 
                       end_time: Optional[str] = None) -> Any:
        """
        Get market data from the market data service
        """
        return self.market_data_service.get_data(symbol, data_type, start_time, end_time)
    
    def place_order(self, symbol: str, order_type: str, side: str, quantity: float, 
                   price: Optional[float] = None) -> Order:
        """
        Place an order - this would typically interact with a trading service
        """
        # This is a simplified version - in a real implementation, 
        # this would interact with the trading engine
        logger.info(f"Strategy {self.name} is attempting to place order: {side} {quantity} of {symbol}")
        # In a real implementation, return an actual order object
        pass
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order - this would typically interact with a trading service
        """
        logger.info(f"Strategy {self.name} is attempting to cancel order: {order_id}")
        # In a real implementation, return the actual result
        pass
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get current position for a symbol
        """
        # In a real implementation, this would retrieve the actual position
        pass