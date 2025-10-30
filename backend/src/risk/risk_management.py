import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from ..models.risk_params import RiskParams
from ..models.account import Account
from ..models.position import Position
from ..models.order import Order

@dataclass
class RiskEvent:
    """风险事件数据类"""
    event_type: str
    message: str
    severity: str  # low, medium, high, critical
    timestamp: datetime
    details: Dict

class RiskManagementSystem:
    """风险管理系统"""
    
    def __init__(self):
        self.risk_events = []
        self.max_order_rate_per_second = 100  # 每秒最大订单数
        self.min_time_between_orders = 1.0 / self.max_order_rate_per_second  # 秒
        self.last_order_time = {}
        
    def check_account_risk(self, account: Account, risk_params: RiskParams) -> List[RiskEvent]:
        """检查账户级别风险"""
        events = []
        
        # 检查资金风险
        if risk_params.account_risk:
            import json
            params = json.loads(risk_params.account_risk)
            
            # 检查最大持仓价值
            if 'max_position_value' in params:
                max_value = params['max_position_value']
                if account.total_funds > max_value:
                    events.append(RiskEvent(
                        event_type="ACCOUNT_MAX_VALUE_EXCEEDED",
                        message=f"账户总资金 {account.total_funds} 超过最大限制 {max_value}",
                        severity="high",
                        timestamp=datetime.now(),
                        details={"account_id": str(account.id), "current_value": account.total_funds, "limit": max_value}
                    ))
            
            # 检查最大日亏损
            if 'max_daily_loss' in params:
                max_loss = params['max_daily_loss']
                daily_loss = account.total_funds - account.cumulative_profit
                if daily_loss > max_loss:
                    events.append(RiskEvent(
                        event_type="ACCOUNT_MAX_DAILY_LOSS_EXCEEDED",
                        message=f"账户日亏损 {daily_loss} 超过最大限制 {max_loss}",
                        severity="high",
                        timestamp=datetime.now(),
                        details={"account_id": str(account.id), "current_loss": daily_loss, "limit": max_loss}
                    ))
        
        return events
    
    def check_position_risk(self, position: Position, risk_params: RiskParams) -> List[RiskEvent]:
        """检查持仓风险"""
        events = []
        
        if risk_params.stock_risk:
            import json
            params = json.loads(risk_params.stock_risk)
            
            # 检查单一标的最大持仓
            if 'max_stock_position' in params:
                max_pos = params['max_stock_position']
                if position.position_quantity > max_pos:
                    events.append(RiskEvent(
                        event_type="STOCK_MAX_POSITION_EXCEEDED",
                        message=f"标的 {position.symbol} 持仓 {position.position_quantity} 超过最大限制 {max_pos}",
                        severity="medium",
                        timestamp=datetime.now(),
                        details={"symbol": position.symbol, "current_position": position.position_quantity, "limit": max_pos}
                    ))
        
        return events
    
    def check_order_risk(self, order: Order, risk_params: RiskParams) -> List[RiskEvent]:
        """检查订单风险"""
        events = []
        
        # 检查订单频率风险
        account_id = str(order.account_id)
        current_time = datetime.now()
        
        if account_id in self.last_order_time:
            time_diff = (current_time - self.last_order_time[account_id]).total_seconds()
            if time_diff < self.min_time_between_orders:
                events.append(RiskEvent(
                    event_type="ORDER_RATE_LIMIT_EXCEEDED",
                    message=f"订单频率过高，账户 {account_id} 超过每秒 {self.max_order_rate_per_second} 个订单限制",
                    severity="medium",
                    timestamp=current_time,
                    details={"account_id": account_id, "min_interval": self.min_time_between_orders, "actual_interval": time_diff}
                ))
        
        self.last_order_time[account_id] = current_time
        
        # 检查订单级别风险参数
        if risk_params.account_risk:
            import json
            params = json.loads(risk_params.account_risk)
            
            # 检查订单数量限制
            if 'max_order_count' in params:
                max_orders = params['max_order_count']
                if order.quantity > max_orders:
                    events.append(RiskEvent(
                        event_type="ORDER_QUANTITY_EXCEEDED",
                        message=f"订单数量 {order.quantity} 超过最大限制 {max_orders}",
                        severity="medium",
                        timestamp=current_time,
                        details={"order_id": str(order.id), "current_quantity": order.quantity, "limit": max_orders}
                    ))
        
        return events
    
    def calculate_var(self, portfolio_values: List[float], confidence_level: float = 0.95) -> float:
        """计算风险价值VaR"""
        if len(portfolio_values) < 2:
            return 0.0
        
        returns = np.diff(portfolio_values) / portfolio_values[:-1]
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return var
    
    def check_global_risk(self, risk_params: RiskParams) -> List[RiskEvent]:
        """检查全局风险"""
        events = []
        
        if risk_params.global_risk:
            import json
            params = json.loads(risk_params.global_risk)
            
            # 检查最大订单速率
            if 'max_order_rate' in params:
                global_max_rate = params['max_order_rate']
                current_rate = self._calculate_current_order_rate()
                
                if current_rate > global_max_rate:
                    events.append(RiskEvent(
                        event_type="GLOBAL_ORDER_RATE_EXCEEDED",
                        message=f"全局订单速率 {current_rate} 超过最大限制 {global_max_rate}",
                        severity="high",
                        timestamp=datetime.now(),
                        details={"current_rate": current_rate, "limit": global_max_rate}
                    ))
        
        return events
    
    def _calculate_current_order_rate(self) -> float:
        """计算当前订单速率"""
        # 简化实现：返回预设的最大值
        return self.max_order_rate_per_second * 0.8  # 假设当前速率为最大值的80%
    
    def add_risk_event(self, event: RiskEvent):
        """添加风险事件"""
        self.risk_events.append(event)
        
        # 根据风险级别采取相应措施
        if event.severity in ["high", "critical"]:
            print(f"ALERT: {event.message}")
            # 在实际实现中，这里可能需要触发告警或其他措施