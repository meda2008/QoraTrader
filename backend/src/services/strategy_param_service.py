"""
Strategy parameter service
This service handles updating strategy parameters in real-time without stopping the strategy
"""
from typing import Dict, Any, List, Optional
import logging
from src.models.base import Strategy
from src.database import get_db
from src.utils.error_handler import CustomException
import json

logger = logging.getLogger(__name__)

class StrategyParamService:
    """
    Service for managing strategy parameters in real-time
    """
    
    def __init__(self):
        logger.info("Strategy parameter service initialized")
    
    def update_strategy_parameters(self, strategy_id: str, param_updates: Dict[str, Any]) -> Strategy:
        """
        Update strategy parameters in real-time
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Parse current config
            try:
                current_config = json.loads(strategy.config) if strategy.config else {}
            except json.JSONDecodeError:
                current_config = {}
            
            # Validate parameter updates
            validation_result = self._validate_parameter_updates(strategy_id, param_updates)
            if not validation_result["valid"]:
                raise CustomException(validation_result["message"], 400)
            
            # Update parameters
            updated_config = {**current_config, **param_updates}
            
            # Update strategy config
            strategy.config = json.dumps(updated_config, ensure_ascii=False)
            from datetime import datetime
            strategy.updated_at = datetime.utcnow()
            
            # Commit changes
            db.commit()
            db.refresh(strategy)
            
            logger.info(f"Strategy {strategy_id} parameters updated successfully")
            return strategy
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating strategy {strategy_id} parameters: {str(e)}")
            raise CustomException(f"Failed to update strategy parameters: {str(e)}", 500)
        finally:
            db.close()
    
    def remove_strategy_parameter(self, strategy_id: str, param_name: str) -> Strategy:
        """
        Remove a strategy parameter
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Parse current config
            try:
                current_config = json.loads(strategy.config) if strategy.config else {}
            except json.JSONDecodeError:
                current_config = {}
            
            # Remove parameter if it exists
            if param_name in current_config:
                del current_config[param_name]
                strategy.config = json.dumps(current_config, ensure_ascii=False)
                from datetime import datetime
                strategy.updated_at = datetime.utcnow()
                
                # Commit changes
                db.commit()
                db.refresh(strategy)
                
                logger.info(f"Strategy parameter '{param_name}' removed from strategy {strategy_id}")
            else:
                logger.warning(f"Strategy parameter '{param_name}' not found in strategy {strategy_id}")
            
            return strategy
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error removing parameter '{param_name}' from strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to remove strategy parameter: {str(e)}", 500)
        finally:
            db.close()
    
    def reset_strategy_parameters(self, strategy_id: str) -> Strategy:
        """
        Reset strategy parameters to default values
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Reset to empty config (or default config if defined)
            strategy.config = "{}"  # Empty JSON object as default
            from datetime import datetime
            strategy.updated_at = datetime.utcnow()
            
            # Commit changes
            db.commit()
            db.refresh(strategy)
            
            logger.info(f"Strategy {strategy_id} parameters reset to default values")
            return strategy
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error resetting strategy {strategy_id} parameters: {str(e)}")
            raise CustomException(f"Failed to reset strategy parameters: {str(e)}", 500)
        finally:
            db.close()
    
    def validate_strategy_parameters(self, strategy_id: str, param_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate strategy parameters before updating
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Basic validation
            for param_name, param_value in param_updates.items():
                # Check for invalid parameter names
                if not param_name or not isinstance(param_name, str):
                    return {
                        "valid": False,
                        "message": f"Invalid parameter name: {param_name}"
                    }
                
                # Check for invalid parameter values (basic checks)
                if param_value is None:
                    return {
                        "valid": False,
                        "message": f"Parameter '{param_name}' cannot be null"
                    }
            
            # In a real implementation, this would check against strategy-specific validation rules
            # For example, checking numeric ranges, string formats, etc.
            
            return {
                "valid": True,
                "message": "All parameters are valid"
            }
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error validating strategy {strategy_id} parameters: {str(e)}")
            raise CustomException(f"Failed to validate strategy parameters: {str(e)}", 500)
        finally:
            db.close()
    
    def _validate_parameter_updates(self, strategy_id: str, param_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to validate parameter updates
        """
        # This is a simplified validation - in a real implementation, this would be more complex
        # and might check against strategy-specific rules
        
        # Check that we have updates
        if not param_updates:
            return {
                "valid": False,
                "message": "No parameter updates provided"
            }
        
        # Basic validation
        for param_name, param_value in param_updates.items():
            # Check parameter name
            if not isinstance(param_name, str) or not param_name.strip():
                return {
                    "valid": False,
                    "message": f"Invalid parameter name: {param_name}"
                }
            
            # Check parameter value type (basic check)
            if param_value is not None and not isinstance(param_value, (str, int, float, bool, list, dict)):
                return {
                    "valid": False,
                    "message": f"Invalid parameter value type for '{param_name}': {type(param_value)}"
                }
        
        return {
            "valid": True,
            "message": "Parameter updates are valid"
        }
    
    def get_strategy_parameters(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get current strategy parameters
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Parse config
            try:
                config = json.loads(strategy.config) if strategy.config else {}
            except json.JSONDecodeError:
                config = {}
            
            return config
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error getting strategy {strategy_id} parameters: {str(e)}")
            raise CustomException(f"Failed to get strategy parameters: {str(e)}", 500)
        finally:
            db.close()
    
    def bulk_update_strategy_parameters(self, strategy_ids: List[str], param_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update parameters for multiple strategies at once
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            results = {
                "successful": [],
                "failed": []
            }
            
            for strategy_id in strategy_ids:
                try:
                    # Get strategy from database
                    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                    if not strategy:
                        results["failed"].append({
                            "strategy_id": strategy_id,
                            "error": "Strategy not found"
                        })
                        continue
                    
                    # Parse current config
                    try:
                        current_config = json.loads(strategy.config) if strategy.config else {}
                    except json.JSONDecodeError:
                        current_config = {}
                    
                    # Update parameters
                    updated_config = {**current_config, **param_updates}
                    strategy.config = json.dumps(updated_config, ensure_ascii=False)
                    from datetime import datetime
                    strategy.updated_at = datetime.utcnow()
                    
                    results["successful"].append(strategy_id)
                    logger.info(f"Bulk update: Strategy {strategy_id} parameters updated successfully")
                except Exception as e:
                    results["failed"].append({
                        "strategy_id": strategy_id,
                        "error": str(e)
                    })
                    logger.error(f"Bulk update: Error updating strategy {strategy_id}: {str(e)}")
            
            # Commit all changes
            db.commit()
            
            return results
        except Exception as e:
            logger.error(f"Error in bulk strategy parameter update: {str(e)}")
            raise CustomException(f"Failed to perform bulk strategy parameter update: {str(e)}", 500)
        finally:
            db.close()

# Global strategy parameter service instance
strategy_param_service = StrategyParamService()