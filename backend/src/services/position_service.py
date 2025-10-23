from typing import Dict, List, Optional
from datetime import datetime
import logging
from src.models.base import Position, Account, Strategy
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class PositionService:
    """
    Service for managing positions
    """
    
    def __init__(self):
        logger.info("Position service initialized")
    
    async def get_position(self, position_id: str) -> Optional[Position]:
        """
        Get a position by ID
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            position = db.query(Position).filter(Position.id == position_id).first()
            if not position:
                raise CustomException(f"Position with ID {position_id} not found", 404)
            
            return position
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving position {position_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve position: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_position_by_account_and_symbol(self, account_id: str, symbol: str) -> Optional[Position]:
        """
        Get a position for a specific account and symbol
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            position = db.query(Position).filter(
                Position.account_id == account_id,
                Position.symbol == symbol
            ).first()
            
            return position
        except Exception as e:
            logger.error(f"Error retrieving position for account {account_id} and symbol {symbol}: {str(e)}")
            raise CustomException(f"Failed to retrieve position: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_positions_by_account(self, account_id: str) -> List[Position]:
        """
        Get all positions for a specific account
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            positions = db.query(Position).filter(Position.account_id == account_id).all()
            return positions
        except Exception as e:
            logger.error(f"Error retrieving positions for account {account_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve positions: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_positions_by_strategy(self, strategy_id: str) -> List[Position]:
        """
        Get all positions for a specific strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            positions = db.query(Position).filter(Position.strategy_id == strategy_id).all()
            return positions
        except Exception as e:
            logger.error(f"Error retrieving positions for strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve positions: {str(e)}", 500)
        finally:
            db.close()
    
    async def update_position(self, position_data: Dict) -> Optional[Position]:
        """
        Update a position after a trade
        This method would typically be called by the trading engine after a trade execution
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Get the existing position or create a new one if it doesn't exist
            position = await self.get_position_by_account_and_symbol(
                position_data['account_id'], 
                position_data['symbol']
            )
            
            if not position:
                # Create a new position if one doesn't exist
                position = Position(
                    account_id=position_data['account_id'],
                    strategy_id=position_data['strategy_id'],
                    symbol=position_data['symbol'],
                    direction=position_data['direction'],
                    volume=position_data['volume'],
                    available_volume=position_data['available_volume'],
                    avg_price=position_data['avg_price'],
                    unrealized_pnl=0.0,
                    realized_pnl=0.0
                )
                db.add(position)
            else:
                # Update existing position
                position.volume += position_data.get('volume_delta', 0)
                position.available_volume += position_data.get('available_volume_delta', 0)
                
                # Update average price if buying more of the same position
                if position_data.get('volume_delta', 0) > 0:
                    total_value = (position.avg_price * (position.volume - position_data['volume_delta'])) + \
                                  (position_data['avg_price'] * position_data['volume_delta'])
                    if position.volume != 0:
                        position.avg_price = total_value / position.volume
                
                # If position is closed (volume is 0), reset avg_price
                if position.volume == 0:
                    position.avg_price = 0.0
                    position.available_volume = 0.0
            
            db.commit()
            db.refresh(position)
            
            logger.info(f"Position for {position.symbol} updated: volume={position.volume}, avg_price={position.avg_price}")
            return position
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating position: {str(e)}")
            raise CustomException(f"Failed to update position: {str(e)}", 500)
        finally:
            db.close()
    
    async def calculate_unrealized_pnl(self, position: Position, current_price: float) -> float:
        """
        Calculate the unrealized profit and loss for a position
        """
        if position.volume == 0:
            return 0.0
        
        try:
            from src.models.base import PositionDirection
            
            if position.direction == PositionDirection.LONG:
                # Long position: PnL = (current_price - avg_price) * volume
                pnl = (current_price - position.avg_price) * position.volume
            else:  # SHORT
                # Short position: PnL = (avg_price - current_price) * volume
                pnl = (position.avg_price - current_price) * position.volume
            
            return pnl
        except Exception as e:
            logger.error(f"Error calculating unrealized PnL for position {position.id}: {str(e)}")
            raise CustomException(f"Failed to calculate PnL: {str(e)}", 500)
    
    async def close_position(self, position_id: str) -> bool:
        """
        Close a position (set volume to 0)
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            position = db.query(Position).filter(Position.id == position_id).first()
            if not position:
                raise CustomException(f"Position with ID {position_id} not found", 404)
            
            # Move the current unrealized PnL to realized PnL
            # This would require getting the current market price, which we'll simulate
            # In a real implementation, you'd get the current market price from the market data service
            current_price = 100.0  # Simulated current price
            unrealized_pnl = await self.calculate_unrealized_pnl(position, current_price)
            
            position.realized_pnl += unrealized_pnl
            position.volume = 0
            position.available_volume = 0
            position.avg_price = 0.0
            
            db.commit()
            logger.info(f"Position {position_id} closed, realized PnL: {unrealized_pnl}")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error closing position {position_id}: {str(e)}")
            raise CustomException(f"Failed to close position: {str(e)}", 500)
        finally:
            db.close()