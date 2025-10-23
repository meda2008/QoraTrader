from typing import Dict, List, Optional
from datetime import datetime
import logging
from src.models.base import Trade, Order
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class TradeService:
    """
    Service for managing trades
    """
    
    def __init__(self):
        logger.info("Trade service initialized")
    
    async def create_trade(self, trade_data: Dict) -> Trade:
        """
        Create a new trade
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Validate input data
            required_fields = ['order_id', 'symbol', 'side', 'quantity', 'price']
            for field in required_fields:
                if field not in trade_data:
                    raise CustomException(f"Missing required field: {field}", 400)
            
            # Verify the order exists
            order = db.query(Order).filter(Order.id == trade_data['order_id']).first()
            if not order:
                raise CustomException(f"Order with ID {trade_data['order_id']} not found", 404)
            
            # Create trade object
            trade = Trade(
                order_id=trade_data['order_id'],
                symbol=trade_data['symbol'],
                side=trade_data['side'],
                quantity=trade_data['quantity'],
                price=trade_data['price'],
                executed_at=trade_data.get('executed_at', datetime.utcnow()),
                commission=trade_data.get('commission', 0)
            )
            
            # Validate trade parameters
            if trade.quantity <= 0:
                raise CustomException("Trade quantity must be greater than 0", 400)
            
            if trade.price <= 0:
                raise CustomException("Trade price must be greater than 0", 400)
            
            # Add to database
            db.add(trade)
            db.commit()
            db.refresh(trade)
            
            logger.info(f"Trade {trade.id} created for order {trade.order_id}")
            return trade
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating trade: {str(e)}")
            raise CustomException(f"Failed to create trade: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_trade(self, trade_id: str) -> Optional[Trade]:
        """
        Get a trade by ID
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            trade = db.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                raise CustomException(f"Trade with ID {trade_id} not found", 404)
            
            return trade
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving trade {trade_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve trade: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_trades_by_order(self, order_id: str) -> List[Trade]:
        """
        Get all trades for a specific order
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            trades = db.query(Trade).filter(Trade.order_id == order_id).all()
            return trades
        except Exception as e:
            logger.error(f"Error retrieving trades for order {order_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve trades: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_trades_by_strategy(self, strategy_id: str) -> List[Trade]:
        """
        Get all trades for a specific strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Join Trade with Order to get trades by strategy
            trades = db.query(Trade).join(Order).filter(Order.strategy_id == strategy_id).all()
            return trades
        except Exception as e:
            logger.error(f"Error retrieving trades for strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve trades: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_trades_by_symbol(self, symbol: str, limit: int = 100) -> List[Trade]:
        """
        Get recent trades for a specific symbol
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            trades = db.query(Trade).filter(Trade.symbol == symbol).order_by(Trade.executed_at.desc()).limit(limit).all()
            return trades
        except Exception as e:
            logger.error(f"Error retrieving trades for symbol {symbol}: {str(e)}")
            raise CustomException(f"Failed to retrieve trades: {str(e)}", 500)
        finally:
            db.close()