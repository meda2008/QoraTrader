from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging
from src.indicators.custom_loader import custom_indicator_loader

logger = logging.getLogger(__name__)

class IndicatorServiceInterface(ABC):
    """
    Abstract interface for indicator services
    """
    
    @abstractmethod
    def calculate(self, indicator_name: str, data: Any, **kwargs) -> Any:
        """
        Calculate an indicator
        """
        pass
    
    @abstractmethod
    def register_indicator(self, name: str, calculation_func) -> bool:
        """
        Register a new indicator calculation function
        """
        pass
    
    @abstractmethod
    def list_indicators(self) -> list:
        """
        List all available indicators
        """
        pass

class IndicatorService(IndicatorServiceInterface):
    """
    Default implementation of the indicator service
    """
    
    def __init__(self):
        self._indicators = {}
        self._custom_loader = custom_indicator_loader
        self._init_default_indicators()
    
    def _init_default_indicators(self):
        """
        Initialize default indicators
        """
        # For now, this is a placeholder - in a real implementation,
        # we would connect to actual indicator libraries like TA-Lib
        logger.info("Initializing default indicators")
        pass
    
    def calculate(self, indicator_name: str, data: Any, **kwargs) -> Any:
        """
        Calculate an indicator using the registered function
        """
        if indicator_name not in self._indicators:
            raise ValueError(f"Indicator '{indicator_name}' is not registered")
        
        try:
            calculation_func = self._indicators[indicator_name]
            result = calculation_func(data, **kwargs)
            logger.info(f"Calculated indicator '{indicator_name}' successfully")
            return result
        except Exception as e:
            logger.error(f"Error calculating indicator '{indicator_name}': {str(e)}")
            raise
    
    def register_indicator(self, name: str, calculation_func) -> bool:
        """
        Register a new indicator calculation function
        """
        try:
            self._indicators[name] = calculation_func
            logger.info(f"Registered indicator '{name}'")
            return True
        except Exception as e:
            logger.error(f"Error registering indicator '{name}': {str(e)}")
            return False
    
    def list_indicators(self) -> list:
        """
        List all available indicators
        """
        return list(self._indicators.keys())
    
    def get_indicator_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a specific indicator
        """
        if name not in self._indicators:
            raise ValueError(f"Indicator '{name}' is not registered")
        
        # In a real implementation, we would return more detailed info about the indicator
        return {
            "name": name,
            "registered": True
        }
    
    def calculate_custom_indicator(self, indicator_id: str, data: List[float], parameters: Dict) -> List[float]:
        """
        Calculate a custom indicator
        """
        try:
            return self._custom_loader.calculate_custom_indicator(indicator_id, data, parameters)
        except Exception as e:
            logger.error(f"Error calculating custom indicator {indicator_id}: {str(e)}")
            raise
    
    def list_custom_indicators(self) -> List[Dict]:
        """
        List all custom indicators
        """
        try:
            return self._custom_loader.list_custom_indicators()
        except Exception as e:
            logger.error(f"Error listing custom indicators: {str(e)}")
            raise
    
    def register_custom_indicator(self, indicator_data: Dict) -> Dict:
        """
        Register a custom indicator
        """
        try:
            indicator_library = self._custom_loader.register_custom_indicator(indicator_data)
            
            # Convert to dict format
            indicator_dict = {
                "id": indicator_library.id,
                "name": indicator_library.name,
                "description": indicator_library.description,
                "version": indicator_library.version,
                "path": indicator_library.path,
                "is_active": indicator_library.is_active,
                "created_at": indicator_library.created_at.isoformat() if indicator_library.created_at else None,
                "updated_at": indicator_library.updated_at.isoformat() if indicator_library.updated_at else None
            }
            
            return indicator_dict
        except Exception as e:
            logger.error(f"Error registering custom indicator: {str(e)}")
            raise
    
    def remove_custom_indicator(self, indicator_id: str) -> bool:
        """
        Remove a custom indicator
        """
        try:
            return self._custom_loader.remove_custom_indicator(indicator_id)
        except Exception as e:
            logger.error(f"Error removing custom indicator {indicator_id}: {str(e)}")
            raise
    
    def activate_custom_indicator(self, indicator_id: str) -> Dict:
        """
        Activate a custom indicator
        """
        try:
            indicator_library = self._custom_loader.activate_custom_indicator(indicator_id)
            
            # Convert to dict format
            indicator_dict = {
                "id": indicator_library.id,
                "name": indicator_library.name,
                "description": indicator_library.description,
                "version": indicator_library.version,
                "path": indicator_library.path,
                "is_active": indicator_library.is_active,
                "created_at": indicator_library.created_at.isoformat() if indicator_library.created_at else None,
                "updated_at": indicator_library.updated_at.isoformat() if indicator_library.updated_at else None
            }
            
            return indicator_dict
        except Exception as e:
            logger.error(f"Error activating custom indicator {indicator_id}: {str(e)}")
            raise
    
    def deactivate_custom_indicator(self, indicator_id: str) -> Dict:
        """
        Deactivate a custom indicator
        """
        try:
            indicator_library = self._custom_loader.deactivate_custom_indicator(indicator_id)
            
            # Convert to dict format
            indicator_dict = {
                "id": indicator_library.id,
                "name": indicator_library.name,
                "description": indicator_library.description,
                "version": indicator_library.version,
                "path": indicator_library.path,
                "is_active": indicator_library.is_active,
                "created_at": indicator_library.created_at.isoformat() if indicator_library.created_at else None,
                "updated_at": indicator_library.updated_at.isoformat() if indicator_library.updated_at else None
            }
            
            return indicator_dict
        except Exception as e:
            logger.error(f"Error deactivating custom indicator {indicator_id}: {str(e)}")
            raise

# Global indicator service instance
indicator_service = IndicatorService()