"""
Strategy lifecycle management
This module handles the lifecycle of trading strategies including initialization, activation, pausing, and termination
"""
from typing import Dict, Any, Optional, List
import logging
from src.models.base import Strategy, StrategyStatus
from src.database import get_db
from src.utils.error_handler import CustomException
from src.strategies.hot_loader import strategy_hot_loader

logger = logging.getLogger(__name__)

class StrategyLifecycleManager:
    """
    Manager for strategy lifecycle operations
    """
    
    def __init__(self):
        self._active_strategies: Dict[str, Strategy] = {}
        self._strategy_states: Dict[str, Dict[str, Any]] = {}
        logger.info("Strategy lifecycle manager initialized")
    
    def initialize_strategy(self, strategy_id: str) -> bool:
        """
        Initialize a strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Check current status
            if strategy.status.value != "inactive":
                raise CustomException(f"Strategy {strategy_id} is not in inactive state", 400)
            
            # Update status to initialized
            strategy.status = StrategyStatus.INACTIVE  # Still inactive but initialized
            db.commit()
            db.refresh(strategy)
            
            # Store in active strategies dict
            self._active_strategies[strategy_id] = strategy
            
            # Initialize strategy state
            self._strategy_states[strategy_id] = {
                "initialized_at": "2023-10-22T10:30:00Z",  # In a real implementation, this would be actual timestamp
                "status": "initialized",
                "config": strategy.config,
                "error_count": 0,
                "last_error": None
            }
            
            logger.info(f"Strategy {strategy_id} initialized successfully")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error initializing strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to initialize strategy: {str(e)}", 500)
        finally:
            db.close()
    
    def activate_strategy(self, strategy_id: str) -> bool:
        """
        Activate a strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Check if strategy can be activated
            if strategy.status.value not in ["inactive", "paused", "stopped", "error"]:
                raise CustomException(f"Strategy {strategy_id} cannot be activated from {strategy.status.value} state", 400)
            
            # Try to hot load the strategy
            try:
                success = strategy_hot_loader.reload_strategy(strategy_id)
                if not success:
                    raise CustomException(f"Failed to hot load strategy {strategy_id}", 500)
            except Exception as e:
                # Update strategy status to error
                strategy.status = StrategyStatus.ERROR
                db.commit()
                raise CustomException(f"Failed to load strategy {strategy_id}: {str(e)}", 500)
            
            # Update status to active
            strategy.status = StrategyStatus.ACTIVE
            db.commit()
            db.refresh(strategy)
            
            # Store in active strategies dict
            self._active_strategies[strategy_id] = strategy
            
            # Update strategy state
            if strategy_id in self._strategy_states:
                self._strategy_states[strategy_id]["status"] = "active"
                self._strategy_states[strategy_id]["activated_at"] = "2023-10-22T10:30:00Z"  # Actual timestamp in real impl
            else:
                self._strategy_states[strategy_id] = {
                    "status": "active",
                    "activated_at": "2023-10-22T10:30:00Z",
                    "config": strategy.config,
                    "error_count": 0,
                    "last_error": None
                }
            
            logger.info(f"Strategy {strategy_id} activated successfully")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error activating strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to activate strategy: {str(e)}", 500)
        finally:
            db.close()
    
    def pause_strategy(self, strategy_id: str) -> bool:
        """
        Pause a strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Check if strategy can be paused
            if strategy.status.value != "active":
                raise CustomException(f"Strategy {strategy_id} cannot be paused from {strategy.status.value} state", 400)
            
            # Update status to paused
            strategy.status = StrategyStatus.PAUSED
            db.commit()
            db.refresh(strategy)
            
            # Update strategy state
            if strategy_id in self._strategy_states:
                self._strategy_states[strategy_id]["status"] = "paused"
                self._strategy_states[strategy_id]["paused_at"] = "2023-10-22T10:30:00Z"  # Actual timestamp in real impl
            
            logger.info(f"Strategy {strategy_id} paused successfully")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error pausing strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to pause strategy: {str(e)}", 500)
        finally:
            db.close()
    
    def stop_strategy(self, strategy_id: str) -> bool:
        """
        Stop a strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Check if strategy can be stopped
            if strategy.status.value not in ["active", "paused"]:
                raise CustomException(f"Strategy {strategy_id} cannot be stopped from {strategy.status.value} state", 400)
            
            # Unload strategy from hot loader
            strategy_hot_loader.unload_strategy(strategy_id)
            
            # Update status to stopped
            strategy.status = StrategyStatus.STOPPED
            db.commit()
            db.refresh(strategy)
            
            # Remove from active strategies
            if strategy_id in self._active_strategies:
                del self._active_strategies[strategy_id]
            
            # Update strategy state
            if strategy_id in self._strategy_states:
                self._strategy_states[strategy_id]["status"] = "stopped"
                self._strategy_states[strategy_id]["stopped_at"] = "2023-10-22T10:30:00Z"  # Actual timestamp in real impl
            
            logger.info(f"Strategy {strategy_id} stopped successfully")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error stopping strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to stop strategy: {str(e)}", 500)
        finally:
            db.close()
    
    def restart_strategy(self, strategy_id: str) -> bool:
        """
        Restart a strategy (stop and then activate)
        """
        try:
            # First stop the strategy
            self.stop_strategy(strategy_id)
            
            # Then activate it again
            return self.activate_strategy(strategy_id)
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error restarting strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to restart strategy: {str(e)}", 500)
    
    def get_strategy_status(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get the current status of a strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Get strategy state if available
            state_info = self._strategy_states.get(strategy_id, {})
            
            status_info = {
                "strategy_id": strategy.id,
                "name": strategy.name,
                "status": strategy.status.value,
                "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
                "state_info": state_info
            }
            
            return status_info
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error getting status for strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to get strategy status: {str(e)}", 500)
        finally:
            db.close()
    
    def list_active_strategies(self) -> List[Dict[str, Any]]:
        """
        List all active strategies
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get all active strategies from database
            active_strategies = db.query(Strategy).filter(
                Strategy.status.in_([
                    StrategyStatus.ACTIVE,
                    StrategyStatus.PAUSED
                ])
            ).all()
            
            # Convert to dict format
            strategies_list = []
            for strategy in active_strategies:
                strategy_dict = {
                    "id": strategy.id,
                    "name": strategy.name,
                    "status": strategy.status.value,
                    "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
                    "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
                    "state_info": self._strategy_states.get(strategy.id, {})
                }
                strategies_list.append(strategy_dict)
            
            return strategies_list
        except Exception as e:
            logger.error(f"Error listing active strategies: {str(e)}")
            raise CustomException(f"Failed to list active strategies: {str(e)}", 500)
        finally:
            db.close()
    
    def handle_strategy_error(self, strategy_id: str, error_message: str) -> bool:
        """
        Handle an error in a strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Update strategy status to error
            strategy.status = StrategyStatus.ERROR
            db.commit()
            db.refresh(strategy)
            
            # Update strategy state with error info
            if strategy_id in self._strategy_states:
                self._strategy_states[strategy_id]["status"] = "error"
                self._strategy_states[strategy_id]["last_error"] = error_message
                self._strategy_states[strategy_id]["error_count"] = self._strategy_states[strategy_id].get("error_count", 0) + 1
                self._strategy_states[strategy_id]["errored_at"] = "2023-10-22T10:30:00Z"  # Actual timestamp in real impl
            
            logger.error(f"Strategy {strategy_id} encountered error: {error_message}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error handling strategy error for {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to handle strategy error: {str(e)}", 500)
        finally:
            db.close()
    
    def recover_from_error(self, strategy_id: str) -> bool:
        """
        Attempt to recover a strategy from error state
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get strategy from database
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # Check if strategy is in error state
            if strategy.status.value != "error":
                raise CustomException(f"Strategy {strategy_id} is not in error state", 400)
            
            # Try to reactivate the strategy
            return self.activate_strategy(strategy_id)
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error recovering strategy {strategy_id} from error: {str(e)}")
            raise CustomException(f"Failed to recover strategy from error: {str(e)}", 500)
        finally:
            db.close()

# Global strategy lifecycle manager instance
strategy_lifecycle_manager = StrategyLifecycleManager()