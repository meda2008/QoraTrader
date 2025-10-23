from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.base import Order, Strategy
from src.auth.security import get_current_active_user
from src.schemas.order import OrderCreate, OrderResponse

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get all orders for the current user
    """
    orders = db.query(Order).join(Strategy).filter(Strategy.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get a specific order by ID
    """
    order = db.query(Order).join(Strategy).filter(
        Order.id == order_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a new order
    """
    # Verify that the strategy belongs to the current user
    strategy = db.query(Strategy).filter(
        Strategy.id == order_data.strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create order for strategy that doesn't belong to you"
        )
    
    order = Order(
        strategy_id=order_data.strategy_id,
        symbol=order_data.symbol,
        order_type=order_data.order_type,
        side=order_data.side,
        quantity=order_data.quantity,
        price=order_data.price
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order