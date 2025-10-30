import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..config.settings import config

def setup_logging():
    """设置日志记录"""
    # 创建日志目录
    log_dir = Path(config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器 - 使用轮转日志
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 防止重复添加处理器
    logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """获取命名的日志记录器"""
    return logging.getLogger(name)

setup_logging()