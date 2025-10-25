from typing import Dict, Any, List
import logging
from src.indicators.service import IndicatorService as IndicatorServiceImpl

logger = logging.getLogger(__name__)

class IndicatorService:
    """
    Service for managing technical indicators calculations
    """
    
    def __init__(self):
        self.indicator_impl = IndicatorServiceImpl()
        
    async def calculate_indicator(
        self,
        indicator_name: str,
        data: List[Dict[str, Any]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Calculate technical indicator for given data
        
        Args:
            indicator_name: Name of the indicator to calculate
            data: Market data to calculate indicator on
            **kwargs: Additional parameters for the indicator
            
        Returns:
            Calculated indicator values
        """
        try:
            logger.info(f"Calculating indicator {indicator_name}")
            result = await self.indicator_impl.calculate(indicator_name, data, **kwargs)
            logger.info(f"Indicator {indicator_name} calculated successfully")
            return result
        except Exception as e:
            logger.error(f"Error calculating indicator {indicator_name}: {str(e)}")
            raise
            
    async def register_indicator_library(
        self,
        library_name: str,
        library_path: str
    ) -> bool:
        """
        Register a new indicator library
        
        Args:
            library_name: Name of the library
            library_path: Path to the library
            
        Returns:
            True if registration successful, False otherwise
        """
        try:
            logger.info(f"Registering indicator library {library_name}")
            result = await self.indicator_impl.register_library(library_name, library_path)
            logger.info(f"Indicator library {library_name} registered successfully")
            return result
        except Exception as e:
            logger.error(f"Error registering indicator library {library_name}: {str(e)}")
            raise
            
    async def get_available_indicators(self) -> List[str]:
        """
        Get list of all available indicators
        
        Returns:
            List of available indicator names
        """
        try:
            result = await self.indicator_impl.list_indicators()
            return result
        except Exception as e:
            logger.error(f"Error getting available indicators: {str(e)}")
            raise