from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
import threading
from ..models.order import Order
from ..models.trade import Trade
from ..models.position import Position
from ..events.event_bus import event_bus, Event, EventType
from ..risk.risk_management import RiskManagementSystem
from ..services.order_service import OrderService
from ..services.position_service import PositionService

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class ExecutionReport:
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    status: OrderStatus
    timestamp: datetime

class CoreEngine:
    """
    核心交易引擎，负责订单执行、交易匹配和基本交易逻辑
    """
    
    def __init__(self):
        self.order_service = None
        self.position_service = None
        self.risk_manager = RiskManagementSystem()
        self.active_orders: Dict[str, Order] = {}
        self.execution_reports: List[ExecutionReport] = []
        self.lock = threading.Lock()
        
    def set_services(self, order_service: OrderService, position_service: PositionService):
        """设置服务引用"""
        self.order_service = order_service
        self.position_service = position_service
    
    async def submit_order(self, order: Order) -> bool:
        """提交订单"""
        # 检查风险控制
        risk_events = self.risk_manager.check_order_risk(order, order.strategy.risk_params)
        for event in risk_events:
            self.risk_manager.add_risk_event(event)
            if event.severity in ["high", "critical"]:
                # 如果风险级别高，拒绝订单
                order.status = "已拒绝"
                return False
        
        # 更新订单状态
        with self.lock:
            order.status = "已提交"
            self.active_orders[str(order.id)] = order
            
        # 发布订单提交事件
        await event_bus.publish(Event(
            type=EventType.ORDER_SUBMITTED,
            data={
                "order_id": str(order.id),
                "strategy_id": str(order.strategy_id),
                "symbol": order.symbol,
                "direction": order.direction,
                "quantity": order.quantity,
                "price": order.price
            }
        ))
        
        return True
    
    async def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        with self.lock:
            if order_id not in self.active_orders:
                return False
            
            order = self.active_orders[order_id]
            order.status = "已取消"
            
            # 从活跃订单中移除
            del self.active_orders[order_id]
            
        # 发布订单取消事件
        await event_bus.publish(Event(
            type=EventType.ORDER_CANCELLED,
            data={
                "order_id": order_id,
                "strategy_id": str(order.strategy_id),
                "symbol": order.symbol
            }
        ))
        
        return True
    
    async def execute_trade(self, order: Order, fill_price: float, fill_quantity: int):
        """执行交易"""
        # 更新订单状态
        if fill_quantity == order.quantity:
            order.status = "完全成交"
        else:
            order.status = "部分成交"
            order.filled_quantity += fill_quantity
        
        order.average_fill_price = fill_price
        
        # 记录成交
        trade = Trade(
            order_id=order.id,
            strategy_id=order.strategy_id,
            account_id=order.account_id,
            symbol=order.symbol,
            direction=order.direction,
            trade_price=fill_price,
            trade_quantity=fill_quantity
        )
        
        # 更新持仓
        if self.position_service:
            direction_multi = 1 if order.direction == "买入" else -1
            self.position_service.update_position(
                account_id=str(order.account_id),
                strategy_id=str(order.strategy_id),
                symbol=order.symbol,
                direction=order.direction,
                quantity=fill_quantity * direction_multi,
                available_quantity=fill_quantity * direction_multi,
                cost=fill_price,
                current_price=fill_price
            )
        
        # 发布成交事件
        await event_bus.publish(Event(
            type=EventType.ORDER_FILLED,
            data={
                "order_id": str(order.id),
                "strategy_id": str(order.strategy_id),
                "symbol": order.symbol,
                "direction": order.direction,
                "fill_quantity": fill_quantity,
                "fill_price": fill_price,
                "remaining_quantity": order.quantity - order.filled_quantity
            }
        ))
        
        # 创建执行报告
        report = ExecutionReport(
            order_id=str(order.id),
            symbol=order.symbol,
            side=OrderSide.BUY if order.direction == "买入" else OrderSide.SELL,
            quantity=fill_quantity,
            price=fill_price,
            status=OrderStatus.FILLED if order.status == "完全成交" else OrderStatus.PARTIALLY_FILLED,
            timestamp=datetime.now()
        )
        
        with self.lock:
            self.execution_reports.append(report)
    
    def get_active_orders(self) -> List[Order]:
        """获取活跃订单"""
        with self.lock:
            return list(self.active_orders.values())
    
    def get_execution_reports(self, limit: int = 100) -> List[ExecutionReport]:
        """获取执行报告"""
        with self.lock:
            return self.execution_reports[-limit:]