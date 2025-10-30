from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ... import models
from .schemas.order import Order, OrderCreate, OrderUpdate
from ...database import get_db
from ...services.order_service import OrderService

router = APIRouter()

@router.get("/", response_model=List[Order])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取订单列表"""
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders

@router.post("/", response_model=Order)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """创建新订单"""
    order_service = OrderService(db)
    new_order = order_service.create_order(
        strategy_id=order.strategy_id,
        account_id=order.account_id,
        symbol=order.symbol,
        direction=order.direction,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price
    )
    return new_order

@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str, db: Session = Depends(get_db)):
    """获取特定订单"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=Order)
def update_order(order_id: str, order: OrderUpdate, db: Session = Depends(get_db)):
    """更新订单信息"""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: str, db: Session = Depends(get_db)):
    """删除订单"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return

@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(order_id: str, db: Session = Depends(get_db)):
    """取消订单"""
    order_service = OrderService(db)
    order = order_service.cancel_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found or could not be canceled")
    return order