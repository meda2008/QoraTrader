from typing import Dict, List
from datetime import datetime
from enum import Enum
from ..models.strategy import Strategy
from ..models.order import Order
from ..models.position import Position
from ..database import get_db

class StrategyStatus(Enum):
    UNACTIVATED = "未激活"
    ACTIVATED = "已激活"
    PAUSED = "暂停"
    STOPPED = "已停止"
    ERROR = "异常"

class StrategyLifecycleManager:
    """
    策略生命周期管理器
    """
    
    def __init__(self, db):
        self.db = db
        self.strategy_states: Dict[str, StrategyStatus] = {}
        self.strategy_start_times: Dict[str, datetime] = {}
        self.strategy_last_error: Dict[str, str] = {}
    
    def register_strategy(self, strategy_id: str):
        """
        注册策略
        """
        self.strategy_states[strategy_id] = StrategyStatus.UNACTIVATED
        self.strategy_start_times[strategy_id] = datetime.now()
        if strategy_id in self.strategy_last_error:
            del self.strategy_last_error[strategy_id]
    
    def activate_strategy(self, strategy_id: str) -> bool:
        """
        激活策略
        """
        current_status = self.get_strategy_status(strategy_id)
        if current_status in [StrategyStatus.UNACTIVATED, StrategyStatus.PAUSED, StrategyStatus.STOPPED]:
            self.strategy_states[strategy_id] = StrategyStatus.ACTIVATED
            self.update_strategy_db_status(strategy_id, StrategyStatus.ACTIVATED.value)
            return True
        return False
    
    def pause_strategy(self, strategy_id: str) -> bool:
        """
        暂停策略
        """
        current_status = self.get_strategy_status(strategy_id)
        if current_status == StrategyStatus.ACTIVATED:
            self.strategy_states[strategy_id] = StrategyStatus.PAUSED
            self.update_strategy_db_status(strategy_id, StrategyStatus.PAUSED.value)
            return True
        return False
    
    def stop_strategy(self, strategy_id: str) -> bool:
        """
        停止策略
        """
        current_status = self.get_strategy_status(strategy_id)
        if current_status in [StrategyStatus.ACTIVATED, StrategyStatus.PAUSED]:
            self.strategy_states[strategy_id] = StrategyStatus.STOPPED
            self.update_strategy_db_status(strategy_id, StrategyStatus.STOPPED.value)
            return True
        return False
    
    def set_strategy_error(self, strategy_id: str, error_message: str):
        """
        设置策略错误状态
        """
        self.strategy_states[strategy_id] = StrategyStatus.ERROR
        self.strategy_last_error[strategy_id] = error_message
        self.update_strategy_db_status(strategy_id, StrategyStatus.ERROR.value)
    
    def get_strategy_status(self, strategy_id: str) -> StrategyStatus:
        """
        获取策略状态
        """
        return self.strategy_states.get(strategy_id, StrategyStatus.UNACTIVATED)
    
    def get_all_strategy_statuses(self) -> Dict[str, StrategyStatus]:
        """
        获取所有策略状态
        """
        return self.strategy_states.copy()
    
    def get_strategy_uptime(self, strategy_id: str) -> float:
        """
        获取策略运行时间（秒）
        """
        start_time = self.strategy_start_times.get(strategy_id)
        if start_time:
            return (datetime.now() - start_time).total_seconds()
        return 0.0
    
    def reset_strategy(self, strategy_id: str):
        """
        重置策略状态
        """
        # 保留原始启动时间，设置为未激活状态
        start_time = self.strategy_start_times.get(strategy_id)
        self.strategy_states[strategy_id] = StrategyStatus.UNACTIVATED
        if start_time:
            self.strategy_start_times[strategy_id] = start_time
        if strategy_id in self.strategy_last_error:
            del self.strategy_last_error[strategy_id]
        self.update_strategy_db_status(strategy_id, StrategyStatus.UNACTIVATED.value)
    
    def update_strategy_db_status(self, strategy_id: str, status: str):
        """
        更新数据库中的策略状态
        """
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if strategy:
            strategy.status = status
            strategy.updated_at = datetime.now()
            self.db.commit()
    
    def cleanup_strategy(self, strategy_id: str):
        """
        清理策略资源
        """
        # 在这里可以添加清理订单、持仓等资源的逻辑
        # 例如：撤销所有未成交订单
        self.cleanup_orders(strategy_id)
        
        # 从状态映射中移除
        if strategy_id in self.strategy_states:
            del self.strategy_states[strategy_id]
        if strategy_id in self.strategy_start_times:
            del self.strategy_start_times[strategy_id]
        if strategy_id in self.strategy_last_error:
            del self.strategy_last_error[strategy_id]
    
    def cleanup_orders(self, strategy_id: str):
        """
        清理策略的所有未成交订单
        """
        # 实现撤销所有未成交订单的逻辑
        orders = self.db.query(Order).filter(
            Order.strategy_id == strategy_id,
            Order.status.in_(["未提交", "已提交"])
        ).all()
        
        for order in orders:
            order.status = "已取消"
            order.updated_at = datetime.now()
        
        self.db.commit()
    
    def get_error_message(self, strategy_id: str) -> str:
        """
        获取策略错误信息
        """
        return self.strategy_last_error.get(strategy_id, "")