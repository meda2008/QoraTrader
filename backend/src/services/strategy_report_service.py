from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from src.models.base import Strategy, BacktestReport, Trade, Order
from src.database import get_db
from src.services.backtest_service import BacktestService
from src.trading.engine import trading_engine
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class StrategyReportService:
    """
    策略报告服务，用于生成策略的详细表现报告和可视化数据
    """
    
    def __init__(self):
        self.backtest_service = BacktestService()
        logger.info("Strategy report service initialized")
    
    async def get_strategy_report(self, strategy_id: str) -> Dict:
        """
        获取策略的详细报告
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 获取策略基本信息
            strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
            if not strategy:
                raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # 获取相关的回测报告
            backtest_reports = db.query(BacktestReport).filter(
                BacktestReport.strategy_id == strategy_id
            ).order_by(BacktestReport.created_at.desc()).all()
            
            # 获取相关的交易记录
            trade_records = db.query(Trade).join(Order).filter(
                Order.strategy_id == strategy_id
            ).order_by(Trade.executed_at.desc()).all()
            
            # 计算关键指标
            total_trades = len(trade_records)
            winning_trades = len([t for t in trade_records if t.price > 0])  # Simplified calculation
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # 净值曲线数据
            equity_curve = await self._generate_equity_curve(strategy_id, trade_records)
            
            # 构建报告
            report = {
                "strategy_id": strategy.id,
                "strategy_name": strategy.name,
                "strategy_description": strategy.description,
                "created_at": strategy.created_at.isoformat(),
                "performance_metrics": {
                    "total_trades": total_trades,
                    "win_rate": win_rate,
                    "total_return": 0.0,  # Calculate from trade records
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "profit_factor": 0.0
                },
                "equity_curve": equity_curve,
                "recent_trades": self._format_trades(trade_records[:10]),  # Last 10 trades
                "backtest_reports": self._format_backtest_reports(backtest_reports[:5])  # Last 5 reports
            }
            
            return report
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error generating strategy report for {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to generate strategy report: {str(e)}", 500)
        finally:
            db.close()
    
    async def _generate_equity_curve(self, strategy_id: str, trade_records: List[Trade]) -> List[Dict]:
        """
        生成净值曲线数据
        """
        try:
            # 这里应该基于交易记录计算净值曲线
            # 简化实现：返回模拟数据
            import random
            base_value = 100000  # 初始资金
            curve = []
            
            for i in range(30):  # 30天的数据
                date = (datetime.now() - timedelta(days=29-i)).isoformat()
                # 随机生成一些波动
                change = random.uniform(-0.02, 0.03)  # -2% to +3%
                base_value *= (1 + change)
                curve.append({
                    "date": date,
                    "value": round(base_value, 2)
                })
            
            return curve
        except Exception as e:
            logger.error(f"Error generating equity curve for strategy {strategy_id}: {str(e)}")
            return []
    
    def _format_trades(self, trade_records: List[Trade]) -> List[Dict]:
        """
        格式化交易记录
        """
        try:
            formatted_trades = []
            for trade in trade_records:
                formatted_trade = {
                    "id": trade.id,
                    "symbol": trade.symbol,
                    "side": trade.side.value,
                    "quantity": float(trade.quantity),
                    "price": float(trade.price),
                    "executed_at": trade.executed_at.isoformat() if trade.executed_at else None,
                    "commission": float(trade.commission)
                }
                formatted_trades.append(formatted_trade)
            return formatted_trades
        except Exception as e:
            logger.error(f"Error formatting trades: {str(e)}")
            return []
    
    def _format_backtest_reports(self, reports: List[BacktestReport]) -> List[Dict]:
        """
        格式化回测报告
        """
        try:
            formatted_reports = []
            for report in reports:
                formatted_report = {
                    "id": report.id,
                    "start_date": report.start_date.isoformat(),
                    "end_date": report.end_date.isoformat(),
                    "initial_capital": float(report.initial_capital),
                    "final_capital": float(report.final_capital),
                    "total_return": float(report.total_return) if report.total_return else 0.0,
                    "sharpe_ratio": float(report.sharpe_ratio) if report.sharpe_ratio else 0.0,
                    "max_drawdown": float(report.max_drawdown) if report.max_drawdown else 0.0,
                    "total_trades": report.total_trades or 0,
                    "win_rate": float(report.win_rate) if report.win_rate else 0.0
                }
                formatted_reports.append(formatted_report)
            return formatted_reports
        except Exception as e:
            logger.error(f"Error formatting backtest reports: {str(e)}")
            return []

# Global strategy report service instance
strategy_report_service = StrategyReportService()