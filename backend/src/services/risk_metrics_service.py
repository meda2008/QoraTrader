import logging
from typing import Dict, List
from src.models.base import Account, Position, Trade
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class RiskMetricsService:
    """
    风险指标计算服务
    """
    
    def __init__(self):
        logger.info("Risk metrics service initialized")
    
    async def calculate_account_risk_metrics(self, account_id: str) -> Dict:
        """
        计算账户的风险指标
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 查询账户信息
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                raise CustomException(f"Account with ID {account_id} not found", 404)
            
            # 获取账户的持仓
            # 注意：这里我们直接查询Position表，但实际模型中Position通过Account外键关联
            # 在实际模型中，Position表的外键可能需要调整
            from src.models.base import Position
            positions = db.query(Position).filter(Position.account_id == account_id).all()
            
            # 计算风险指标
            total_market_value = float(account.market_value) if account.market_value else 0.0
            total_pnl = float(account.total_pnl) if account.total_pnl else 0.0
            
            # 计算持仓集中度（最大单一持仓占总投资的比例）
            concentration = 0.0
            if total_market_value > 0 and positions:
                max_position_value = max([float(pos.volume * pos.avg_price) for pos in positions if pos.avg_price and pos.volume])
                concentration = max_position_value / total_market_value
            
            # 计算风险指标
            risk_metrics = {
                "account_id": account.id,
                "total_market_value": total_market_value,
                "total_pnl": total_pnl,
                "available_balance": float(account.available_balance),
                "risk_level": account.risk_level.value if account.risk_level else "unknown",
                "concentration_risk": concentration,
                "position_count": len(positions),
                "last_updated": account.updated_at.isoformat() if account.updated_at else None
            }
            
            return risk_metrics
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error calculating account risk metrics for {account_id}: {str(e)}")
            raise CustomException(f"Failed to calculate risk metrics: {str(e)}", 500)
        finally:
            db.close()
    
    async def calculate_system_wide_risk_metrics(self) -> Dict:
        """
        计算全系统的风险指标
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 获取所有账户
            accounts = db.query(Account).all()
            
            # 计算系统级指标
            total_accounts = len(accounts)
            total_market_value = sum([float(acc.market_value) for acc in accounts if acc.market_value])
            total_pnl = sum([float(acc.total_pnl) for acc in accounts if acc.total_pnl])
            
            # 计算处于不同风险等级的账户数
            risk_level_counts = {"low": 0, "medium": 0, "high": 0, "extreme": 0}
            for acc in accounts:
                if acc.risk_level:
                    level = acc.risk_level.value.lower()
                    if level in risk_level_counts:
                        risk_level_counts[level] += 1
            
            # 计算系统风险指标
            system_risk_metrics = {
                "total_accounts": total_accounts,
                "total_market_value": total_market_value,
                "total_pnl": total_pnl,
                "risk_distribution": risk_level_counts,
                "avg_concentration": 0.0,  # 这里可以计算平均集中度
                "last_updated": "2025-10-22T10:30:00Z"  # 应该使用实际时间
            }
            
            return system_risk_metrics
        except Exception as e:
            logger.error(f"Error calculating system-wide risk metrics: {str(e)}")
            raise CustomException(f"Failed to calculate system risk metrics: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_volatile_positions(self, threshold: float = 0.05) -> List[Dict]:
        """
        获取波动较大的持仓（超过阈值的持仓）
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 获取所有持仓
            positions = db.query(Position).all()
            
            volatile_positions = []
            for pos in positions:
                # 在实际系统中，这里应该基于市场数据计算波动率
                # 简化实现：使用模拟的波动率
                import random
                volatility = random.uniform(0.01, 0.1)  # 1% to 10% 波动
                
                if volatility > threshold:
                    volatile_pos = {
                        "position_id": pos.id,
                        "account_id": pos.account_id,
                        "symbol": pos.symbol,
                        "volume": float(pos.volume),
                        "avg_price": float(pos.avg_price),
                        "current_value": float(pos.volume * pos.avg_price) if pos.avg_price else 0.0,
                        "estimated_volatility": volatility
                    }
                    volatile_positions.append(volatile_pos)
            
            return volatile_positions
        except Exception as e:
            logger.error(f"Error getting volatile positions: {str(e)}")
            raise CustomException(f"Failed to get volatile positions: {str(e)}", 500)
        finally:
            db.close()

# Global risk metrics service instance
risk_metrics_service = RiskMetricsService()