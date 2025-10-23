"""
Exchange adapter registry
This module manages the registration and retrieval of exchange adapters
"""
from typing import Dict, List, Type, Optional, Any
import logging
from src.exchanges.base_adapter import ExchangeAdapterInterface
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class ExchangeRegistry:
    """
    Registry for managing exchange adapters
    """
    
    def __init__(self):
        self._adapters: Dict[str, ExchangeAdapterInterface] = {}
        self._adapter_classes: Dict[str, Type[ExchangeAdapterInterface]] = {}
        self._default_adapter: Optional[str] = None
        logger.info("Exchange registry initialized")
    
    def register_adapter_class(self, name: str, adapter_class: Type[ExchangeAdapterInterface]) -> bool:
        """
        Register an adapter class
        This allows for dynamic instantiation of adapters
        """
        try:
            # Validate that the class implements the interface
            if not issubclass(adapter_class, ExchangeAdapterInterface):
                raise CustomException(f"Adapter class {adapter_class.__name__} does not implement ExchangeAdapterInterface", 400)
            
            self._adapter_classes[name] = adapter_class
            logger.info(f"Registered adapter class '{name}': {adapter_class.__name__}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error registering adapter class '{name}': {str(e)}")
            raise CustomException(f"Failed to register adapter class: {str(e)}", 500)
    
    def register_adapter(self, name: str, adapter: ExchangeAdapterInterface) -> bool:
        """
        Register an instantiated adapter
        """
        try:
            # Validate that the adapter implements the interface
            if not isinstance(adapter, ExchangeAdapterInterface):
                raise CustomException(f"Adapter {name} does not implement ExchangeAdapterInterface", 400)
            
            self._adapters[name] = adapter
            logger.info(f"Registered adapter '{name}': {adapter.__class__.__name__}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error registering adapter '{name}': {str(e)}")
            raise CustomException(f"Failed to register adapter: {str(e)}", 500)
    
    def unregister_adapter(self, name: str) -> bool:
        """
        Unregister an adapter
        """
        try:
            if name in self._adapters:
                # Disconnect the adapter before removing
                adapter = self._adapters[name]
                import asyncio
                try:
                    asyncio.run(adapter.disconnect())
                except Exception as e:
                    logger.warning(f"Error disconnecting adapter '{name}' before removal: {str(e)}")
                
                del self._adapters[name]
                logger.info(f"Unregistered adapter '{name}'")
                return True
            else:
                logger.warning(f"Adapter '{name}' not found for unregistration")
                return False
        except Exception as e:
            logger.error(f"Error unregistering adapter '{name}': {str(e)}")
            raise CustomException(f"Failed to unregister adapter: {str(e)}", 500)
    
    def get_adapter(self, name: str) -> Optional[ExchangeAdapterInterface]:
        """
        Get an adapter by name
        """
        return self._adapters.get(name)
    
    def get_adapter_class(self, name: str) -> Optional[Type[ExchangeAdapterInterface]]:
        """
        Get an adapter class by name
        """
        return self._adapter_classes.get(name)
    
    def create_adapter(self, name: str, **kwargs) -> Optional[ExchangeAdapterInterface]:
        """
        Create a new adapter instance from a registered class
        """
        try:
            adapter_class = self._adapter_classes.get(name)
            if not adapter_class:
                raise CustomException(f"Adapter class '{name}' not found", 404)
            
            # Create new adapter instance
            adapter = adapter_class(**kwargs)
            return adapter
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating adapter '{name}': {str(e)}")
            raise CustomException(f"Failed to create adapter: {str(e)}", 500)
    
    def list_adapters(self) -> List[str]:
        """
        List all registered adapter names
        """
        return list(self._adapters.keys())
    
    def list_adapter_classes(self) -> List[str]:
        """
        List all registered adapter class names
        """
        return list(self._adapter_classes.keys())
    
    def has_adapter(self, name: str) -> bool:
        """
        Check if an adapter is registered
        """
        return name in self._adapters
    
    def has_adapter_class(self, name: str) -> bool:
        """
        Check if an adapter class is registered
        """
        return name in self._adapter_classes
    
    def set_default_adapter(self, name: str) -> bool:
        """
        Set the default adapter
        """
        try:
            if name not in self._adapters and name not in self._adapter_classes:
                raise CustomException(f"Adapter '{name}' not found", 404)
            
            self._default_adapter = name
            logger.info(f"Set default adapter to '{name}'")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error setting default adapter '{name}': {str(e)}")
            raise CustomException(f"Failed to set default adapter: {str(e)}", 500)
    
    def get_default_adapter(self) -> Optional[ExchangeAdapterInterface]:
        """
        Get the default adapter
        """
        if not self._default_adapter:
            return None
        
        return self._adapters.get(self._default_adapter)
    
    def get_default_adapter_name(self) -> Optional[str]:
        """
        Get the name of the default adapter
        """
        return self._default_adapter
    
    def connect_all_adapters(self) -> Dict[str, bool]:
        """
        Connect all registered adapters
        Returns a dictionary mapping adapter names to connection success status
        """
        try:
            results = {}
            for name, adapter in self._adapters.items():
                try:
                    import asyncio
                    success = asyncio.run(adapter.connect())
                    results[name] = success
                    if success:
                        logger.info(f"Connected adapter '{name}' successfully")
                    else:
                        logger.warning(f"Failed to connect adapter '{name}'")
                except Exception as e:
                    logger.error(f"Error connecting adapter '{name}': {str(e)}")
                    results[name] = False
            return results
        except Exception as e:
            logger.error(f"Error connecting all adapters: {str(e)}")
            raise CustomException(f"Failed to connect adapters: {str(e)}", 500)
    
    def disconnect_all_adapters(self) -> Dict[str, bool]:
        """
        Disconnect all registered adapters
        Returns a dictionary mapping adapter names to disconnection success status
        """
        try:
            results = {}
            for name, adapter in self._adapters.items():
                try:
                    import asyncio
                    success = asyncio.run(adapter.disconnect())
                    results[name] = success
                    if success:
                        logger.info(f"Disconnected adapter '{name}' successfully")
                    else:
                        logger.warning(f"Failed to disconnect adapter '{name}'")
                except Exception as e:
                    logger.error(f"Error disconnecting adapter '{name}': {str(e)}")
                    results[name] = False
            return results
        except Exception as e:
            logger.error(f"Error disconnecting all adapters: {str(e)}")
            raise CustomException(f"Failed to disconnect adapters: {str(e)}", 500)
    
    def get_adapter_status(self, name: str) -> Dict[str, Any]:
        """
        Get the status of a specific adapter
        """
        try:
            adapter = self._adapters.get(name)
            if not adapter:
                raise CustomException(f"Adapter '{name}' not found", 404)
            
            return {
                "name": name,
                "connected": adapter.connected,
                "supported_markets": adapter.get_supported_markets(),
                "class_name": adapter.__class__.__name__,
                "last_updated": "2023-10-22T10:30:00Z"  # In a real implementation, this would be actual timestamp
            }
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error getting status for adapter '{name}': {str(e)}")
            raise CustomException(f"Failed to get adapter status: {str(e)}", 500)
    
    def get_all_adapter_statuses(self) -> List[Dict[str, Any]]:
        """
        Get the status of all registered adapters
        """
        try:
            statuses = []
            for name in self._adapters.keys():
                try:
                    status = self.get_adapter_status(name)
                    statuses.append(status)
                except Exception as e:
                    logger.error(f"Error getting status for adapter '{name}': {str(e)}")
                    # Add error status
                    statuses.append({
                        "name": name,
                        "connected": False,
                        "supported_markets": [],
                        "class_name": "Unknown",
                        "error": str(e),
                        "last_updated": "2023-10-22T10:30:00Z"
                    })
            return statuses
        except Exception as e:
            logger.error(f"Error getting all adapter statuses: {str(e)}")
            raise CustomException(f"Failed to get adapter statuses: {str(e)}", 500)

# Global exchange registry instance
exchange_registry = ExchangeRegistry()