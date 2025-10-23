"""
Base exchange adapter interface
This module defines the abstract interface that all exchange adapters must implement
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
from src.models.base import Order, OrderType, OrderSide, OrderStatus
from src.utils.error_handler import CustomException

class ExchangeAdapterInterface(ABC):
    """
    Abstract interface for exchange adapters
    """
    
    def __init__(self, name: str, api_key: str = None, api_secret: str = None):
        self._name = name
        self._api_key = api_key
        self._api_secret = api_secret
        self._connected = False
        self._supported_markets = set()
    
    @property
    def name(self) -> str:
        """Get the adapter name"""
        return self._name
    
    @property
    def connected(self) -> bool:
        """Check if the adapter is connected"""
        return self._connected
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to the exchange
        Returns True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the exchange
        Returns True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def place_order(self, order: Order) -> str:
        """
        Place an order on the exchange
        Returns the exchange order ID
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """
        Cancel an order on the exchange
        Returns True if cancellation successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str, symbol: str = None) -> Dict[str, Any]:
        """
        Get the status of an order
        Returns a dictionary with order status information
        """
        pass
    
    @abstractmethod
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information
        Returns a dictionary with account information
        """
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions
        Returns a list of position dictionaries
        """
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str, data_type: str = "tick") -> Any:
        """
        Get market data for a symbol
        Returns market data in appropriate format based on data_type
        """
        pass
    
    @abstractmethod
    async def get_symbols(self) -> List[str]:
        """
        Get list of supported symbols
        Returns a list of symbol strings
        """
        pass
    
    @abstractmethod
    async def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """
        Get order book for a symbol
        Returns a dictionary with bid and ask data
        """
        pass
    
    @abstractmethod
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent trades for a symbol
        Returns a list of trade dictionaries
        """
        pass
    
    @abstractmethod
    async def subscribe_to_market_data(self, symbol: str, callback) -> bool:
        """
        Subscribe to real-time market data updates
        Returns True if subscription successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def unsubscribe_from_market_data(self, symbol: str) -> bool:
        """
        Unsubscribe from real-time market data updates
        Returns True if unsubscription successful, False otherwise
        """
        pass
    
    def is_market_supported(self, symbol: str) -> bool:
        """
        Check if a market/symbol is supported by this adapter
        """
        return symbol in self._supported_markets
    
    def get_supported_markets(self) -> List[str]:
        """
        Get list of all supported markets/symbols
        """
        return list(self._supported_markets)
    
    async def validate_order(self, order: Order) -> Dict[str, Any]:
        """
        Validate an order before submitting to the exchange
        Returns validation result dictionary
        """
        try:
            # Basic validation
            if not order.symbol:
                return {
                    "valid": False,
                    "message": "Order symbol is required"
                }
            
            if order.quantity <= 0:
                return {
                    "valid": False,
                    "message": "Order quantity must be positive"
                }
            
            if order.order_type == OrderType.LIMIT and (order.price is None or order.price <= 0):
                return {
                    "valid": False,
                    "message": "Limit order price must be positive"
                }
            
            if order.side not in [OrderSide.BUY, OrderSide.SELL]:
                return {
                    "valid": False,
                    "message": "Invalid order side"
                }
            
            if order.order_type not in [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP]:
                return {
                    "valid": False,
                    "message": "Invalid order type"
                }
            
            # Check if market is supported
            if not self.is_market_supported(order.symbol):
                return {
                    "valid": False,
                    "message": f"Market {order.symbol} is not supported by {self._name} adapter"
                }
            
            return {
                "valid": True,
                "message": "Order is valid"
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Error validating order: {str(e)}"
            }
    
    async def normalize_order_response(self, exchange_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize exchange-specific order response to standard format
        """
        # This is a placeholder implementation - each adapter should override this
        return exchange_response
    
    async def normalize_account_response(self, exchange_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize exchange-specific account response to standard format
        """
        # This is a placeholder implementation - each adapter should override this
        return exchange_response
    
    async def normalize_position_response(self, exchange_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize exchange-specific position response to standard format
        """
        # This is a placeholder implementation - each adapter should override this
        return exchange_response
    
    async def normalize_market_data_response(self, exchange_response: Any) -> Any:
        """
        Normalize exchange-specific market data response to standard format
        """
        # This is a placeholder implementation - each adapter should override this
        return exchange_response

class BaseExchangeAdapter(ExchangeAdapterInterface):
    """
    Base implementation of the exchange adapter interface
    Provides common functionality that most adapters will need
    """
    
    def __init__(self, name: str, api_key: str = None, api_secret: str = None):
        super().__init__(name, api_key, api_secret)
        self._session = None
        self._market_subscriptions = {}
        self._rate_limiter = None
    
    async def connect(self) -> bool:
        """
        Base implementation of connect method
        Subclasses should override this and call super().connect() at the end
        """
        try:
            # Initialize session and other common setup
            # This would typically involve authenticating with the exchange API
            self._connected = True
            return True
        except Exception as e:
            self._connected = False
            raise CustomException(f"Failed to connect to {self._name}: {str(e)}", 500)
    
    async def disconnect(self) -> bool:
        """
        Base implementation of disconnect method
        Subclasses should override this and call super().disconnect() at the end
        """
        try:
            # Clean up session and other resources
            self._connected = False
            return True
        except Exception as e:
            raise CustomException(f"Failed to disconnect from {self._name}: {str(e)}", 500)
    
    async def get_order_status(self, order_id: str, symbol: str = None) -> Dict[str, Any]:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"get_order_status not implemented for {self._name}")
    
    async def get_account_info(self) -> Dict[str, Any]:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"get_account_info not implemented for {self._name}")
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"get_positions not implemented for {self._name}")
    
    async def get_market_data(self, symbol: str, data_type: str = "tick") -> Any:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"get_market_data not implemented for {self._name}")
    
    async def get_symbols(self) -> List[str]:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"get_symbols not implemented for {self._name}")
    
    async def get_order_book(self, symbol: str, depth: int = 20) -> Dict[str, Any]:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"get_order_book not implemented for {self._name}")
    
    async def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"get_recent_trades not implemented for {self._name}")
    
    async def subscribe_to_market_data(self, symbol: str, callback) -> bool:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"subscribe_to_market_data not implemented for {self._name}")
    
    async def unsubscribe_from_market_data(self, symbol: str) -> bool:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"unsubscribe_from_market_data not implemented for {self._name}")
    
    async def place_order(self, order: Order) -> str:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"place_order not implemented for {self._name}")
    
    async def cancel_order(self, order_id: str, symbol: str = None) -> bool:
        """
        Base implementation that throws NotImplementedError
        Subclasses must override this method
        """
        raise NotImplementedError(f"cancel_order not implemented for {self._name}")
    
    def _handle_api_error(self, error_response: Dict[str, Any]) -> CustomException:
        """
        Handle API error responses and convert to appropriate CustomException
        """
        try:
            error_code = error_response.get("code", "UNKNOWN_ERROR")
            error_message = error_response.get("message", "Unknown error occurred")
            
            # Map common error codes to appropriate HTTP status codes
            error_mapping = {
                "INSUFFICIENT_FUNDS": 400,
                "INVALID_SYMBOL": 400,
                "INVALID_ORDER": 400,
                "ORDER_NOT_FOUND": 404,
                "RATE_LIMIT_EXCEEDED": 429,
                "AUTHENTICATION_FAILED": 401,
                "PERMISSION_DENIED": 403
            }
            
            status_code = error_mapping.get(error_code, 500)
            return CustomException(f"Exchange API error [{error_code}]: {error_message}", status_code)
        except Exception as e:
            return CustomException(f"Failed to handle API error: {str(e)}", 500)
    
    async def _rate_limit_request(self, request_func, *args, **kwargs):
        """
        Apply rate limiting to API requests
        """
        # In a real implementation, this would integrate with a rate limiting system
        # For now, we'll just execute the request directly
        return await request_func(*args, **kwargs)
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """
        Parse timestamp string to Unix timestamp
        """
        try:
            from datetime import datetime
            # Try common timestamp formats
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"]:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.timestamp()
                except ValueError:
                    continue
            # If none work, try parsing as float (Unix timestamp)
            return float(timestamp_str)
        except Exception:
            # Return current time as fallback
            from time import time
            return time()