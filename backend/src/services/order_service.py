from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.order import Order
from ..models.account import Account
from ..models.strategy import Strategy

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(
        self,
        strategy_id: str,
        account_id: str,
        symbol: str,
        direction: str,
        order_type: str,
        quantity: int,
        price: float = None
    ) -> Order:
        """创建新订单"""
        order = Order(
            strategy_id=strategy_id,
            account_id=account_id,
            symbol=symbol,
            direction=direction,
            order_type=order_type,
            quantity=quantity,
            price=price,
            status="未提交"
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """根据ID获取订单"""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_orders_by_strategy(self, strategy_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取策略的所有订单"""
        return self.db.query(Order).filter(Order.strategy_id == strategy_id).offset(skip).limit(limit).all()

    def get_orders_by_account(self, account_id: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """获取账户的所有订单"""
        return self.db.query(Order).filter(Order.account_id == account_id).offset(skip).limit(limit).all()

    def update_order_status(self, order_id: str, status: str) -> Optional[Order]:
        """更新订单状态"""
        order = self.get_order(order_id)
        if order:
            order.status = status
            order.update_time = None  # Let the database update this automatically
            self.db.commit()
            self.db.refresh(order)
        return order

    def cancel_order(self, order_id: str) -> Optional[Order]:
        """取消订单"""
        order = self.get_order(order_id)
        if order and order.status in ["未提交", "已提交"]:
            order.status = "已取消"
            order.update_time = None  # Let the database update this automatically
            self.db.commit()
            self.db.refresh(order)
        return order