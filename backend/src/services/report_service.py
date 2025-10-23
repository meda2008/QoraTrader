from typing import Dict, List
import logging
from src.models.base import Trade, Order, BacktestReport
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class ReportService:
    """
    报告生成服务，用于生成交易报表和绩效归因分析
    """
    
    def __init__(self):
        logger.info("Report service initialized")
    
    async def generate_trading_report(self, strategy_id: str, start_date: str, end_date: str) -> Dict:
        """
        生成交易报告
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 获取策略的交易记录
            trades = db.query(Trade).join(Order).filter(
                Order.strategy_id == strategy_id,
                Trade.executed_at >= start_date,
                Trade.executed_at <= end_date
            ).all()
            
            # 计算绩效指标
            total_trades = len(trades)
            winning_trades = 0
            losing_trades = 0
            total_pnl = 0.0
            winning_pnl = 0.0
            losing_pnl = 0.0
            
            # 计算每笔交易的盈亏（简化计算）
            for i in range(0, len(trades), 2):  # 假设买入和卖出成对出现
                if i + 1 < len(trades):
                    buy_trade = trades[i]
                    sell_trade = trades[i+1]
                    pnl = (float(sell_trade.price) - float(buy_trade.price)) * float(buy_trade.quantity)
                    total_pnl += pnl
                    
                    if pnl > 0:
                        winning_trades += 1
                        winning_pnl += pnl
                    else:
                        losing_trades += 1
                        losing_pnl += pnl
            
            win_rate = winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) > 0 else 0
            avg_win = winning_pnl / winning_trades if winning_trades > 0 else 0
            avg_loss = losing_pnl / losing_trades if losing_trades > 0 else 0
            profit_factor = abs(winning_pnl / losing_pnl) if losing_pnl != 0 else float('inf')
            
            # 生成报告
            report = {
                "strategy_id": strategy_id,
                "report_period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "performance_metrics": {
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "losing_trades": losing_trades,
                    "win_rate": win_rate,
                    "total_pnl": total_pnl,
                    "profit_factor": profit_factor,
                    "avg_win": avg_win,
                    "avg_loss": avg_loss
                },
                "trade_list": self._format_trades(trades),
                "summary": f"策略 {strategy_id} 在 {start_date} 到 {end_date} 期间共执行 {total_trades} 笔交易，胜率 {win_rate:.2%}"
            }
            
            return report
        except Exception as e:
            logger.error(f"Error generating trading report for strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to generate trading report: {str(e)}", 500)
        finally:
            db.close()
    
    def _format_trades(self, trades: List[Trade]) -> List[Dict]:
        """
        格式化交易记录
        """
        formatted_trades = []
        for trade in trades:
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

# Global report service instance
report_service = ReportService()