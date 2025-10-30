import asyncio
import importlib.util
import sys
import os
from pathlib import Path
from typing import Dict, Optional
from ..strategies.strategy_interface import StrategyInterface, StrategyLoader
from ..models.strategy import Strategy
from ..core.trading_engine import CoreEngine

class StrategyHotLoader:
    """
    策略热加载器，允许在不重启系统的情况下加载、卸载或更新策略
    """
    
    def __init__(self, db, trading_engine: CoreEngine):
        self.db = db
        self.trading_engine = trading_engine
        self.strategy_loader = StrategyLoader()
        self.active_strategies: Dict[str, StrategyInterface] = {}
        self.strategy_files: Dict[str, str] = {}  # 策略ID到文件路径的映射
    
    async def load_strategy(self, strategy_id: str, file_path: Optional[str] = None) -> bool:
        """
        加载策略
        """
        try:
            # 获取策略信息
            strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                print(f"策略 {strategy_id} 不存在")
                return False
            
            if file_path:
                # 如果提供了文件路径，更新策略的代码路径
                strategy.code_path = file_path
                self.db.commit()
            
            if not strategy.code_path:
                print(f"策略 {strategy_id} 没有指定代码路径")
                return False
            
            # 加载策略
            strategy_instance = self.strategy_loader.load_strategy_from_file(
                strategy_id, 
                strategy.code_path, 
                strategy.config
            )
            
            # 初始化策略
            strategy_instance.initialize()
            
            # 激活策略
            strategy_instance.activate()
            
            # 保存到活动策略列表
            self.active_strategies[strategy_id] = strategy_instance
            self.strategy_files[strategy_id] = strategy.code_path
            
            print(f"策略 {strategy_id} 加载成功")
            return True
            
        except Exception as e:
            print(f"加载策略 {strategy_id} 失败: {e}")
            return False
    
    async def unload_strategy(self, strategy_id: str) -> bool:
        """
        卸载策略
        """
        try:
            if strategy_id in self.active_strategies:
                # 停止策略
                strategy_instance = self.active_strategies[strategy_id]
                strategy_instance.stop()
                
                # 从活动策略中移除
                del self.active_strategies[strategy_id]
                
                # 从策略加载器中卸载
                self.strategy_loader.unload_strategy(strategy_id)
                
                # 如果有相关订单，可能需要取消这些订单
                # 这里可以根据需要添加相关逻辑
                
                print(f"策略 {strategy_id} 卸载成功")
                return True
            else:
                print(f"策略 {strategy_id} 未在运行")
                return False
                
        except Exception as e:
            print(f"卸载策略 {strategy_id} 失败: {e}")
            return False
    
    async def reload_strategy(self, strategy_id: str, file_path: Optional[str] = None) -> bool:
        """
        重新加载策略
        """
        # 首先卸载当前策略
        unload_success = await self.unload_strategy(strategy_id)
        if not unload_success:
            print(f"重新加载策略 {strategy_id} 失败：无法卸载原策略")
            return False
        
        # 然后加载新策略
        if file_path:
            load_success = await self.load_strategy(strategy_id, file_path)
        else:
            # 如果未提供文件路径，使用原路径重新加载
            original_path = self.strategy_files.get(strategy_id)
            if original_path:
                load_success = await self.load_strategy(strategy_id, original_path)
            else:
                print(f"重新加载策略 {strategy_id} 失败：未找到原文件路径")
                return False
        
        if load_success:
            print(f"策略 {strategy_id} 重新加载成功")
            return True
        else:
            print(f"策略 {strategy_id} 重新加载失败")
            return False
    
    async def start_strategy(self, strategy_id: str) -> bool:
        """
        启动策略
        """
        if strategy_id in self.active_strategies:
            self.active_strategies[strategy_id].activate()
            print(f"策略 {strategy_id} 启动成功")
            return True
        else:
            print(f"策略 {strategy_id} 未加载，无法启动")
            return False
    
    async def pause_strategy(self, strategy_id: str) -> bool:
        """
        暂停策略
        """
        if strategy_id in self.active_strategies:
            self.active_strategies[strategy_id].pause()
            print(f"策略 {strategy_id} 暂停成功")
            return True
        else:
            print(f"策略 {strategy_id} 未在运行，无法暂停")
            return False
    
    def get_active_strategies(self) -> Dict[str, StrategyInterface]:
        """
        获取所有活动策略
        """
        return self.active_strategies.copy()
    
    async def process_market_data(self, symbol: str, data: Dict[str, any]):
        """
        将市场数据分发给所有活动策略
        """
        for strategy_id, strategy in self.active_strategies.items():
            if not strategy.is_paused:
                try:
                    strategy.on_market_data(symbol, data)
                except Exception as e:
                    print(f"策略 {strategy_id} 处理市场数据时出错: {e}")
    
    async def process_order_update(self, order_id: str, status: str):
        """
        将订单更新分发给相关策略
        """
        for strategy_id, strategy in self.active_strategies.items():
            try:
                strategy.on_order_update(order_id, status)
            except Exception as e:
                print(f"策略 {strategy_id} 处理订单更新时出错: {e}")
    
    async def process_trade(self, trade: Dict[str, any]):
        """
        将成交信息分发给相关策略
        """
        for strategy_id, strategy in self.active_strategies.items():
            try:
                strategy.on_trade(trade)
            except Exception as e:
                print(f"策略 {strategy_id} 处理成交信息时出错: {e}")