"""
Strategy hot loader
This module handles hot loading of trading strategies without restarting the system
"""
import os
import sys
import importlib
import importlib.util
from typing import Dict, Any, Optional
import logging
from src.models.base import Strategy
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class StrategyHotLoader:
    """
    Hot loader for trading strategies
    """
    
    def __init__(self):
        self._loaded_strategies: Dict[str, Any] = {}
        self._strategy_modules: Dict[str, Any] = {}
        logger.info("Strategy hot loader initialized")
    
    def reload_strategy(self, strategy_id: str, strategy_code: str = None, config: Dict = None) -> bool:
        """
        Reload a strategy by ID
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database if not provided
            if strategy_code is None:
                strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                if not strategy:
                    raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
                
                strategy_code = strategy.code
                config = strategy.config if strategy.config else "{}"
            
            # Create temporary file for the strategy code
            temp_file_path = self._create_temp_strategy_file(strategy_id, strategy_code)
            
            # Load the strategy module
            module_name = f"strategy_{strategy_id}"
            
            # If module was previously loaded, unload it first
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Load the new module
            spec = importlib.util.spec_from_file_location(module_name, temp_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the strategy class in the module
            strategy_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, 'strategy_logic') and 
                    callable(getattr(attr, 'strategy_logic'))):
                    strategy_class = attr
                    break
            
            if not strategy_class:
                raise CustomException(f"No valid strategy class found in module for strategy {strategy_id}", 400)
            
            # Create strategy instance
            strategy_instance = strategy_class(
                strategy_id=strategy_id,
                config=config
            )
            
            # Store the loaded strategy
            self._loaded_strategies[strategy_id] = strategy_instance
            self._strategy_modules[strategy_id] = module
            
            # Clean up temporary file
            os.remove(temp_file_path)
            
            logger.info(f"Strategy {strategy_id} reloaded successfully")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error reloading strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to reload strategy: {str(e)}", 500)
        finally:
            db.close()
    
    def _create_temp_strategy_file(self, strategy_id: str, strategy_code: str) -> str:
        """
        Create a temporary file for the strategy code
        """
        try:
            # Create temp directory if it doesn't exist
            temp_dir = "temp_strategies"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Create temp file path
            temp_file_path = os.path.join(temp_dir, f"strategy_{strategy_id}.py")
            
            # Write strategy code to temp file
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(strategy_code)
            
            return temp_file_path
        except Exception as e:
            logger.error(f"Error creating temp strategy file: {str(e)}")
            raise CustomException(f"Failed to create temp strategy file: {str(e)}", 500)
    
    def get_strategy(self, strategy_id: str) -> Optional[Any]:
        """
        Get a loaded strategy by ID
        """
        return self._loaded_strategies.get(strategy_id)
    
    def unload_strategy(self, strategy_id: str) -> bool:
        """
        Unload a strategy by ID
        """
        try:
            # Remove from loaded strategies
            if strategy_id in self._loaded_strategies:
                del self._loaded_strategies[strategy_id]
            
            # Remove module if loaded
            module_name = f"strategy_{strategy_id}"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Remove from modules dict
            if strategy_id in self._strategy_modules:
                del self._strategy_modules[strategy_id]
            
            logger.info(f"Strategy {strategy_id} unloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error unloading strategy {strategy_id}: {str(e)}")
            return False
    
    def list_loaded_strategies(self) -> Dict[str, str]:
        """
        List all loaded strategies
        """
        try:
            strategy_info = {}
            for strategy_id, strategy_instance in self._loaded_strategies.items():
                strategy_info[strategy_id] = {
                    "class_name": strategy_instance.__class__.__name__,
                    "module": strategy_instance.__class__.__module__
                }
            return strategy_info
        except Exception as e:
            logger.error(f"Error listing loaded strategies: {str(e)}")
            raise CustomException(f"Failed to list loaded strategies: {str(e)}", 500)
    
    def is_strategy_loaded(self, strategy_id: str) -> bool:
        """
        Check if a strategy is loaded
        """
        return strategy_id in self._loaded_strategies
    
    def get_strategy_status(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get the status of a strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Check if loaded
            is_loaded = self.is_strategy_loaded(strategy_id)
            
            status_info = {
                "strategy_id": strategy.id,
                "name": strategy.name,
                "is_loaded": is_loaded,
                "is_active": strategy.status.value == "active",
                "loaded_at": None,  # This would be stored elsewhere in a real implementation
                "last_modified": strategy.updated_at.isoformat() if strategy.updated_at else None,
                "config": strategy.config,
                "status": strategy.status.value
            }
            
            return status_info
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error getting strategy status for {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to get strategy status: {str(e)}", 500)
        finally:
            db.close()

# Global strategy hot loader instance
strategy_hot_loader = StrategyHotLoader()