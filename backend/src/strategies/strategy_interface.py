from abc import ABC, abstractmethod
from typing import Dict, Any, List
import importlib.util
import sys
from pathlib import Path
from ..models.strategy import Strategy

class StrategyInterface(ABC):
    """
    策略接口，所有策略都必须实现此接口
    """
    
    def __init__(self, strategy_id: str, config: Dict[str, Any] = None):
        self.strategy_id = strategy_id
        self.config = config or {}
        self.is_active = False
        self.is_paused = False
    
    @abstractmethod
    def initialize(self):
        """
        初始化策略，加载参数和状态
        """
        pass
    
    @abstractmethod
    def on_market_data(self, symbol: str, data: Dict[str, Any]):
        """
        市场数据回调，当有新的市场数据时调用
        """
        pass
    
    @abstractmethod
    def on_order_update(self, order_id: str, status: str):
        """
        订单更新回调，当订单状态更新时调用
        """
        pass
    
    @abstractmethod
    def on_trade(self, trade: Dict[str, Any]):
        """
        成交回调，当策略相关的成交发生时调用
        """
        pass
    
    @abstractmethod
    def get_signals(self) -> List[Dict[str, Any]]:
        """
        获取策略信号，返回需要执行的订单列表
        """
        pass
    
    def activate(self):
        """激活策略"""
        self.is_active = True
        self.is_paused = False
    
    def pause(self):
        """暂停策略"""
        self.is_paused = True
    
    def stop(self):
        """停止策略"""
        self.is_active = False
        self.is_paused = False

class StrategyLoader:
    """
    策略加载器，负责动态加载和卸载策略
    """
    
    def __init__(self):
        self.loaded_strategies = {}
    
    def load_strategy_from_file(self, strategy_id: str, file_path: str, config: Dict[str, Any] = None) -> StrategyInterface:
        """
        从文件加载策略
        """
        # 动态加载策略模块
        spec = importlib.util.spec_from_file_location(f"strategy_{strategy_id}", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 假设策略类名为 'Strategy'
        if hasattr(module, 'Strategy'):
            strategy_class = getattr(module, 'Strategy')
            strategy_instance = strategy_class(strategy_id, config)
            self.loaded_strategies[strategy_id] = strategy_instance
            return strategy_instance
        else:
            raise ValueError(f"模块 {file_path} 中没有找到 Strategy 类")
    
    def load_strategy_from_db(self, strategy: Strategy) -> StrategyInterface:
        """
        从数据库加载策略
        """
        if not strategy.code_path:
            raise ValueError(f"策略 {strategy.id} 没有指定代码路径")
        
        return self.load_strategy_from_file(str(strategy.id), strategy.code_path, strategy.config)
    
    def unload_strategy(self, strategy_id: str):
        """
        卸载策略
        """
        if strategy_id in self.loaded_strategies:
            del self.loaded_strategies[strategy_id]
    
    def reload_strategy(self, strategy_id: str, file_path: str = None, config: Dict[str, Any] = None) -> StrategyInterface:
        """
        重新加载策略
        """
        # 先卸载旧策略
        self.unload_strategy(strategy_id)
        
        # 重新加载
        if file_path:
            return self.load_strategy_from_file(strategy_id, file_path, config)
        elif strategy_id in self.loaded_strategies:
            # 如果没有提供新路径，使用现有的路径重新加载
            raise ValueError("需要提供新的策略文件路径")
        else:
            raise ValueError("策略未找到，无法重新加载")
    
    def get_strategy(self, strategy_id: str) -> StrategyInterface:
        """
        获取已加载的策略
        """
        return self.loaded_strategies.get(strategy_id)