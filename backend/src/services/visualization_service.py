from typing import Dict, List
import logging
from src.models.base import Strategy, Trade, Order
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class VisualizationService:
    """
    可视化服务，用于生成策略信号与成交的对比图表
    """
    
    def __init__(self):
        logger.info("Visualization service initialized")
    
    async def get_signal_trade_visualization_data(self, strategy_id: str, symbol: str, start_date: str, end_date: str) -> Dict:
        """
        获取策略信号与成交的可视化数据
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 获取策略的交易记录
            trade_records = db.query(Trade).join(Order).filter(
                Order.strategy_id == strategy_id,
                Trade.symbol == symbol
            ).all()
            
            # 获取策略的信号记录（在实际系统中，这会从策略执行日志中获取）
            # 这里我们模拟生成一些信号数据
            signals = self._generate_signal_data(symbol, start_date, end_date)
            
            # 获取价格数据（在实际系统中，这会从市场数据服务获取）
            price_data = self._generate_price_data(symbol, start_date, end_date)
            
            # 整合数据
            visualization_data = {
                "symbol": symbol,
                "strategy_id": strategy_id,
                "start_date": start_date,
                "end_date": end_date,
                "price_data": price_data,
                "trades": self._format_trades(trade_records),
                "signals": signals,
                "summary": {
                    "total_trades": len(trade_records),
                    "total_signals": len(signals),
                    "trade_success_rate": self._calculate_trade_success_rate(trade_records, signals)
                }
            }
            
            return visualization_data
        except Exception as e:
            logger.error(f"Error generating visualization data for strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to generate visualization data: {str(e)}", 500)
        finally:
            db.close()
    
    def _generate_signal_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        生成模拟信号数据
        """
        # 在实际实现中，这将从策略执行日志中获取真实的信号数据
        # 简化实现：返回模拟数据
        import random
        from datetime import datetime, timedelta
        
        signals = []
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date.endswith('Z') else datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date.endswith('Z') else datetime.fromisoformat(end_date)
        
        current = start
        signal_count = 0
        while current < end and signal_count < 20:  # 最多生成20个信号
            if random.random() > 0.7:  # 30%概率生成信号
                signal_type = "BUY" if random.random() > 0.5 else "SELL"
                signals.append({
                    "timestamp": current.isoformat(),
                    "type": signal_type,
                    "price": round(random.uniform(90, 110), 2)  # 随机价格
                })
                signal_count += 1
            current += timedelta(hours=1)  # 每小时检查一次
        
        return signals
    
    def _generate_price_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """
        生成模拟价格数据
        """
        # 在实际实现中，这将从市场数据服务获取真实的价格数据
        # 简化实现：返回模拟数据
        import random
        from datetime import datetime, timedelta
        
        prices = []
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date.endswith('Z') else datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date.endswith('Z') else datetime.fromisoformat(end_date)
        
        current = start
        base_price = 100.0
        while current < end:
            # 随机价格变动
            change = random.uniform(-1, 1)
            base_price += change
            if base_price < 10:  # 价格不能低于10
                base_price = 10.0
            prices.append({
                "timestamp": current.isoformat(),
                "open": round(base_price, 2),
                "high": round(base_price + abs(change), 2),
                "low": round(base_price - abs(change), 2),
                "close": round(base_price + change/2, 2),  # 收盘价在开盘价和最高/最低价之间
                "volume": random.randint(1000, 10000)
            })
            current += timedelta(minutes=1)  # 每分钟数据
        
        return prices
    
    def _format_trades(self, trade_records: List[Trade]) -> List[Dict]:
        """
        格式化交易记录
        """
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
    
    def _calculate_trade_success_rate(self, trade_records: List[Trade], signals: List[Dict]) -> float:
        """
        计算交易成功率（简化计算）
        """
        # 在实际实现中，这将基于信号和实际成交之间的关系进行复杂计算
        if not signals:
            return 0.0
        # 简化模型：返回一个模拟的成功率
        import random
        return round(random.uniform(0.6, 0.9), 2)

# Global visualization service instance
visualization_service = VisualizationService()