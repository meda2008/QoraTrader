import os
import sys
import importlib
import importlib.util
from typing import Dict, Optional, Any
import asyncio
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)

class StrategyHotReloader:
    """
    策略热重载器，支持在不重启系统的情况下重新加载策略
    """
    
    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}
        self.strategy_paths: Dict[str, str] = {}
        self.observer = Observer()
        self.watch_paths = set()
        logger.info("Strategy hot reloader initialized")
    
    def register_strategy(self, strategy_id: str, strategy: BaseStrategy, file_path: str):
        """
        注册一个策略用于热重载监控
        """
        self.strategies[strategy_id] = strategy
        self.strategy_paths[strategy_id] = file_path
        strategy_dir = os.path.dirname(file_path)
        
        if strategy_dir not in self.watch_paths:
            event_handler = StrategyFileHandler(self, strategy_dir)
            self.observer.schedule(event_handler, strategy_dir, recursive=False)
            self.watch_paths.add(strategy_dir)
        
        logger.info(f"Registered strategy {strategy_id} for hot reloading: {file_path}")
    
    def unregister_strategy(self, strategy_id: str):
        """
        取消注册一个策略
        """
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            if strategy_id in self.strategy_paths:
                del self.strategy_paths[strategy_id]
            logger.info(f"Unregistered strategy {strategy_id} from hot reloading")
    
    def start_monitoring(self):
        """
        开始监控策略文件变化
        """
        self.observer.start()
        logger.info("Started monitoring strategies for hot reloading")
    
    def stop_monitoring(self):
        """
        停止监控策略文件变化
        """
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped monitoring strategies for hot reloading")
    
    def reload_strategy(self, strategy_id: str) -> bool:
        """
        重新加载一个策略
        """
        try:
            if strategy_id not in self.strategy_paths:
                logger.warning(f"Strategy {strategy_id} not registered for hot reloading")
                return False
            
            file_path = self.strategy_paths[strategy_id]
            if not os.path.exists(file_path):
                logger.error(f"Strategy file does not exist: {file_path}")
                return False
            
            # 获取策略类名
            module_name = os.path.basename(file_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找策略类 (假设策略类名与文件名相似)
            strategy_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseStrategy) and 
                    attr != BaseStrategy):
                    strategy_class = attr
                    break
            
            if not strategy_class:
                logger.error(f"No valid strategy class found in {file_path}")
                return False
            
            # 获取旧策略的配置
            old_strategy = self.strategies[strategy_id]
            strategy_config = old_strategy.config
            strategy_name = old_strategy.name
            
            # 创建新策略实例
            new_strategy = strategy_class(
                strategy_id=strategy_id,
                name=strategy_name,
                config=strategy_config
            )
            
            # 激活新策略
            if old_strategy.is_active:
                new_strategy.activate()
            
            # 替换策略
            self.strategies[strategy_id] = new_strategy
            
            logger.info(f"Successfully reloaded strategy {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error reloading strategy {strategy_id}: {str(e)}", exc_info=True)
            return False


class StrategyFileHandler(FileSystemEventHandler):
    """
    监控策略文件变化的事件处理器
    """
    
    def __init__(self, hot_reloader: StrategyHotReloader, watched_dir: str):
        super().__init__()
        self.hot_reloader = hot_reloader
        self.watched_dir = watched_dir
    
    def on_modified(self, event):
        """
        当文件被修改时触发
        """
        if event.is_directory:
            return
        
        # 检查是否是Python文件
        if not event.src_path.endswith('.py'):
            return
        
        # 根据文件路径找到对应的策略ID
        strategy_id = None
        for sid, path in self.hot_reloader.strategy_paths.items():
            if path == event.src_path:
                strategy_id = sid
                break
        
        if strategy_id:
            logger.info(f"Detected change in strategy {strategy_id} file, reloading...")
            
            # 等待一小段时间以确保文件写入完成
            import time
            time.sleep(0.1)
            
            # 重新加载策略
            self.hot_reloader.reload_strategy(strategy_id)


# 全局策略热重载器实例
strategy_hot_reloader = StrategyHotReloader()


async def initialize_hot_reload():
    """
    初始化策略热重载功能
    """
    strategy_hot_reloader.start_monitoring()
    logger.info("Strategy hot reload system initialized")


async def shutdown_hot_reload():
    """
    关闭策略热重载功能
    """
    strategy_hot_reloader.stop_monitoring()
    logger.info("Strategy hot reload system shut down")