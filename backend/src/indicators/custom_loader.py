"""
Custom indicator loader
This module handles loading and managing custom technical indicators
"""
import os
import sys
import importlib
import importlib.util
from typing import Dict, Any, List, Optional
import logging
from src.models.base import IndicatorLibrary
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class CustomIndicatorLoader:
    """
    Loader for custom technical indicators
    """
    
    def __init__(self):
        self._custom_indicators: Dict[str, Any] = {}
        self._indicator_metadata: Dict[str, Dict] = {}
        logger.info("Custom indicator loader initialized")
    
    def register_custom_indicator(self, indicator_data: Dict) -> IndicatorLibrary:
        """
        Register a custom indicator
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Validate required fields
            required_fields = ['name', 'description', 'version', 'library_path', 'function_name']
            for field in required_fields:
                if field not in indicator_data:
                    raise CustomException(f"Missing required field: {field}", 400)
            
            # Check if indicator with same name already exists
            existing_indicator = db.query(IndicatorLibrary).filter(
                IndicatorLibrary.name == indicator_data['name'],
                IndicatorLibrary.is_active == True
            ).first()
            
            if existing_indicator:
                raise CustomException(f"Indicator with name '{indicator_data['name']}' already exists", 400)
            
            # Validate library path exists
            library_path = indicator_data['library_path']
            if not os.path.exists(library_path):
                raise CustomException(f"Library path does not exist: {library_path}", 400)
            
            # Create indicator library entry
            indicator_library = IndicatorLibrary(
                name=indicator_data['name'],
                description=indicator_data['description'],
                version=indicator_data['version'],
                path=library_path,
                is_active=True
            )
            
            # Save to database
            db.add(indicator_library)
            db.commit()
            db.refresh(indicator_library)
            
            # Load the indicator function
            self._load_indicator_function(indicator_library.id, library_path, indicator_data['function_name'])
            
            logger.info(f"Custom indicator '{indicator_data['name']}' registered successfully")
            return indicator_library
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error registering custom indicator: {str(e)}")
            raise CustomException(f"Failed to register custom indicator: {str(e)}", 500)
        finally:
            db.close()
    
    def _load_indicator_function(self, indicator_id: str, library_path: str, function_name: str):
        """
        Load a custom indicator function from a library file
        """
        try:
            # Get module name from file path
            module_name = os.path.basename(library_path).replace('.py', '')
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, library_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the function
            if not hasattr(module, function_name):
                raise CustomException(f"Function '{function_name}' not found in module '{module_name}'", 400)
            
            function = getattr(module, function_name)
            
            # Store the loaded function
            self._custom_indicators[indicator_id] = function
            
            # Store metadata
            self._indicator_metadata[indicator_id] = {
                'module_name': module_name,
                'function_name': function_name,
                'library_path': library_path
            }
            
            logger.info(f"Indicator function '{function_name}' loaded for indicator ID: {indicator_id}")
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error loading indicator function: {str(e)}")
            raise CustomException(f"Failed to load indicator function: {str(e)}", 500)
    
    def calculate_custom_indicator(self, indicator_id: str, input_data: List[float], parameters: Dict) -> List[float]:
        """
        Calculate a custom indicator
        """
        try:
            # Check if indicator is loaded
            if indicator_id not in self._custom_indicators:
                # Try to load it
                self._load_indicator_from_database(indicator_id)
            
            # Get the indicator function
            if indicator_id not in self._custom_indicators:
                raise CustomException(f"Custom indicator with ID {indicator_id} not found or not loaded", 404)
            
            indicator_function = self._custom_indicators[indicator_id]
            
            # Call the indicator function with input data and parameters
            try:
                result = indicator_function(input_data, **parameters)
                return result
            except Exception as e:
                logger.error(f"Error calculating custom indicator {indicator_id}: {str(e)}")
                raise CustomException(f"Error calculating custom indicator: {str(e)}", 400)
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error in custom indicator calculation: {str(e)}")
            raise CustomException(f"Failed to calculate custom indicator: {str(e)}", 500)
    
    def _load_indicator_from_database(self, indicator_id: str):
        """
        Load an indicator from the database
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get indicator from database
            indicator = db.query(IndicatorLibrary).filter(
                IndicatorLibrary.id == indicator_id,
                IndicatorLibrary.is_active == True
            ).first()
            
            if not indicator:
                raise CustomException(f"Indicator with ID {indicator_id} not found or not active", 404)
            
            # Load the indicator function
            self._load_indicator_function(indicator.id, indicator.path, "calculate_indicator")
            
            db.close()
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error loading indicator from database: {str(e)}")
            # Don't raise here as this is called internally
            pass
    
    def list_custom_indicators(self) -> List[Dict]:
        """
        List all custom indicators
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get all active custom indicators
            indicators = db.query(IndicatorLibrary).filter(
                IndicatorLibrary.is_active == True
            ).all()
            
            # Convert to dict format
            indicators_list = []
            for indicator in indicators:
                indicator_dict = {
                    "id": indicator.id,
                    "name": indicator.name,
                    "description": indicator.description,
                    "version": indicator.version,
                    "path": indicator.path,
                    "is_active": indicator.is_active,
                    "created_at": indicator.created_at.isoformat() if indicator.created_at else None,
                    "updated_at": indicator.updated_at.isoformat() if indicator.updated_at else None
                }
                indicators_list.append(indicator_dict)
            
            return indicators_list
        except Exception as e:
            logger.error(f"Error listing custom indicators: {str(e)}")
            raise CustomException(f"Failed to list custom indicators: {str(e)}", 500)
        finally:
            db.close()
    
    def remove_custom_indicator(self, indicator_id: str) -> bool:
        """
        Remove a custom indicator
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get indicator from database
            indicator = db.query(IndicatorLibrary).filter(
                IndicatorLibrary.id == indicator_id
            ).first()
            
            if not indicator:
                raise CustomException(f"Indicator with ID {indicator_id} not found", 404)
            
            # Remove from database
            db.delete(indicator)
            db.commit()
            
            # Remove from memory if loaded
            if indicator_id in self._custom_indicators:
                del self._custom_indicators[indicator_id]
            if indicator_id in self._indicator_metadata:
                del self._indicator_metadata[indicator_id]
            
            logger.info(f"Custom indicator {indicator_id} removed successfully")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error removing custom indicator {indicator_id}: {str(e)}")
            raise CustomException(f"Failed to remove custom indicator: {str(e)}", 500)
        finally:
            db.close()
    
    def activate_custom_indicator(self, indicator_id: str) -> IndicatorLibrary:
        """
        Activate a custom indicator
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get indicator from database
            indicator = db.query(IndicatorLibrary).filter(
                IndicatorLibrary.id == indicator_id
            ).first()
            
            if not indicator:
                raise CustomException(f"Indicator with ID {indicator_id} not found", 404)
            
            # Activate the indicator
            indicator.is_active = True
            db.commit()
            db.refresh(indicator)
            
            logger.info(f"Custom indicator {indicator_id} activated successfully")
            return indicator
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error activating custom indicator {indicator_id}: {str(e)}")
            raise CustomException(f"Failed to activate custom indicator: {str(e)}", 500)
        finally:
            db.close()
    
    def deactivate_custom_indicator(self, indicator_id: str) -> IndicatorLibrary:
        """
        Deactivate a custom indicator
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get indicator from database
            indicator = db.query(IndicatorLibrary).filter(
                IndicatorLibrary.id == indicator_id
            ).first()
            
            if not indicator:
                raise CustomException(f"Indicator with ID {indicator_id} not found", 404)
            
            # Deactivate the indicator
            indicator.is_active = False
            db.commit()
            db.refresh(indicator)
            
            # Remove from memory if loaded
            if indicator_id in self._custom_indicators:
                del self._custom_indicators[indicator_id]
            if indicator_id in self._indicator_metadata:
                del self._indicator_metadata[indicator_id]
            
            logger.info(f"Custom indicator {indicator_id} deactivated successfully")
            return indicator
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error deactivating custom indicator {indicator_id}: {str(e)}")
            raise CustomException(f"Failed to deactivate custom indicator: {str(e)}", 500)
        finally:
            db.close()

# Global custom indicator loader instance
custom_indicator_loader = CustomIndicatorLoader()