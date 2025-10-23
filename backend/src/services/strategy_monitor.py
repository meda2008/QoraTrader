from typing import Dict, List
import logging
from src.models.base import Strategy
from src.database import get_db
from src.trading.engine import trading_engine
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class StrategyMonitorService:
    """
    策略监控服务，用于监控所有运行中的策略的宏观状态
    """
    
    def __init__(self):
        logger.info("Strategy monitor service initialized")
    
    async def get_all_strategies_status(self) -> List[Dict]:
        """
        获取所有策略的状态信息
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 从数据库获取所有策略的基本信息
            strategies = db.query(Strategy).all()
            
            result = []
            for strategy in strategies:
                # 获取策略的运行时状态
                runtime_status = "stopped"  # 默认状态
                if strategy.id in trading_engine._active_strategies:
                    runtime_status = "running"
                elif strategy.status.value == "paused":
                    runtime_status = "paused"
                
                # 计算累计收益率（这里简化处理，实际应从交易记录计算）
                cumulative_return = 0.0  # 这里应该从交易记录中计算实际收益率
                
                strategy_info = {
                    "id": strategy.id,
                    "name": strategy.name,
                    "status": runtime_status,
                    "cumulative_return": cumulative_return,
                    "created_at": strategy.created_at.isoformat(),
                    "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None
                }
                
                result.append(strategy_info)
            
            return result
        except Exception as e:
            logger.error(f"Error getting strategies status: {str(e)}")
            raise CustomException(f"Failed to get strategies status: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_strategy_status(self, strategy_id: str) -> Dict:
        """
        获取特定策略的状态信息
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 从数据库获取策略信息
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # 获取策略的运行时状态
            runtime_status = "stopped"  # 默认状态
            if strategy.id in trading_engine._active_strategies:
                runtime_status = "running"
            elif strategy.status.value == "paused":
                runtime_status = "paused"
            
            # 计算累计收益率（这里简化处理）
            cumulative_return = 0.0  # 这里应该从交易记录中计算实际收益率
            
            strategy_info = {
                "id": strategy.id,
                "name": strategy.name,
                "status": runtime_status,
                "cumulative_return": cumulative_return,
                "description": strategy.description,
                "created_at": strategy.created_at.isoformat(),
                "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None
            }
            
            return strategy_info
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error getting strategy {strategy_id} status: {str(e)}")
            raise CustomException(f"Failed to get strategy status: {str(e)}", 500)
        finally:
            db.close()
    
    async def refresh_strategy_status(self, strategy_id: str) -> bool:
        """
        刷新特定策略的状态（模拟更新）
        """
        try:
            # 在实际实现中，这将重新计算策略的性能指标
            logger.info(f"Refreshing status for strategy {strategy_id}")
            return True
        except Exception as e:
            logger.error(f"Error refreshing strategy {strategy_id} status: {str(e)}")
            return False

# Global strategy monitor service instance
strategy_monitor_service = StrategyMonitorService()