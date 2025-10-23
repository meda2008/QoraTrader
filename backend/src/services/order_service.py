from typing import Dict, List, Optional
from datetime import datetime
import logging
from src.models.base import Order, Trade, Account, Position
from src.database import get_db
from src.trading.engine import trading_engine
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class OrderService:
    """
    Service for managing orders
    """
    
    def __init__(self):
        logger.info("Order service initialized")
    
    async def create_order(self, order_data: Dict) -> Order:
        """
        Create a new order
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # Validate input data
            required_fields = ['strategy_id', 'symbol', 'order_type', 'side', 'quantity']
            for field in required_fields:
                if field not in order_data:
                    raise CustomException(f"Missing required field: {field}", 400)
            
            # Create order object
            order = Order(
                strategy_id=order_data['strategy_id'],
                symbol=order_data['symbol'],
                order_type=order_data['order_type'],
                side=order_data['side'],
                quantity=order_data['quantity'],
                price=order_data.get('price', 0)  # 0 means market order
            )
            
            # Validate order parameters
            if order.quantity <= 0:
                raise CustomException("Order quantity must be greater than 0", 400)
            
            if order.price < 0:
                raise CustomException("Order price cannot be negative", 400)
            
            # Add to database
            db.add(order)
            db.commit()
            db.refresh(order)
            
            # Submit to trading engine
            await trading_engine.submit_order(order)
            
            logger.info(f"Order {order.id} created and submitted for {order.symbol}")
            return order
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise CustomException(f"Failed to create order: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get an order by ID
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise CustomException(f"Order with ID {order_id} not found", 404)
            
            return order
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve order: {str(e)}", 500)
        finally:
            db.close()
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise CustomException(f"Order with ID {order_id} not found", 404)
            
            # Check if order can be cancelled (not already filled or cancelled)
            if order.status.value in ["filled", "cancelled", "rejected"]:
                raise CustomException(f"Order {order_id} cannot be cancelled, status is {order.status.value}", 400)
            
            # Try to cancel through trading engine
            success = await trading_engine.cancel_order(order_id)
            if success:
                order.status = "cancelled"
                db.commit()
                logger.info(f"Order {order_id} cancelled successfully")
            
            return success
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {str(e)}")
            raise CustomException(f"Failed to cancel order: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_orders_by_strategy(self, strategy_id: str) -> List[Order]:
        """
        Get all orders for a specific strategy
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            orders = db.query(Order).filter(Order.strategy_id == strategy_id).all()
            return orders
        except Exception as e:
            logger.error(f"Error retrieving orders for strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve orders: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_orders_by_account(self, account_id: str) -> List[Order]:
        """
        Get all orders for a specific account
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            orders = db.query(Order).filter(Order.account_id == account_id).all()
            return orders
        except Exception as e:
            logger.error(f"Error retrieving orders for account {account_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve orders: {str(e)}", 500)
        finally:
            db.close()