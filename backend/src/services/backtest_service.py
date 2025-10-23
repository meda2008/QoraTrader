from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from src.models.base import BacktestReport, Strategy, MarketData
from src.database import get_db
from src.trading.engine import TradingEngine
from src.market_data.service import MarketDataService
from src.strategies.base import BaseStrategy
from src.utils.error_handler import CustomException
import logging

logger = logging.getLogger(__name__)

class BacktestService:
    """
    Service for managing backtesting operations
    """
    
    def __init__(self):
        self.trading_engine = TradingEngine()
        self.market_data_service = MarketDataService()
        logger.info("Backtest service initialized")
    
    async def run_backtest(
        self, 
        strategy: BaseStrategy, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime, 
        initial_capital: float,
        data_frequency: str = "1min"
    ) -> BacktestReport:
        """
        Run a backtest for the given strategy and parameters
        """
        # Input validation
        if not symbol or len(symbol.strip()) == 0:
            logger.error("Invalid symbol provided for backtest")
            raise CustomException("Symbol is required for backtesting", status_code=400)
        
        if initial_capital <= 0:
            logger.error(f"Invalid initial capital provided: {initial_capital}")
            raise CustomException("Initial capital must be greater than 0", status_code=400)
        
        if start_date >= end_date:
            logger.error(f"Invalid date range: start {start_date} is not before end {end_date}")
            raise CustomException("Start date must be before end date", status_code=400)
        
        logger.info(f"Starting backtest for strategy {strategy.name} on {symbol} from {start_date} to {end_date}")
        
        try:
            # Get market data for the specified period
            market_data = await self.market_data_service.get_data(
                symbol=symbol,
                data_type=data_frequency,
                start_time=start_date,
                end_time=end_date
            )
            
            if not market_data:
                logger.error(f"No market data available for {symbol} in the specified period")
                raise CustomException(f"No market data available for {symbol} in the specified period", status_code=404)
            
            logger.info(f"Retrieved {len(market_data)} data points for backtest")
            
            # Initialize backtest state
            current_capital = initial_capital
            initial_capital_value = initial_capital
            position = 0  # Position size
            avg_cost = 0  # Average cost basis
            trades = []  # Track all trades
            equity_curve = []  # Track equity over time
            max_equity = initial_capital  # For calculating max drawdown
            
            # Process each data point in chronological order
            for i, data_point in enumerate(market_data):
                current_time = datetime.fromisoformat(data_point['timestamp'])
                current_price = data_point['close']
                
                # Simulate strategy signal based on simple technical indicators
                # In a real implementation, this would call the strategy's on_bar or on_tick method
                signal = self._generate_signal(market_data, i, symbol)
                
                # Execute strategy logic
                if signal == "BUY" and position <= 0:  # Buy signal and not already long
                    # Calculate position size based on risk management (simplified)
                    max_risk = current_capital * 0.02  # Risk 2% of capital
                    risk_per_share = abs(current_price - current_price * 0.95)  # 5% stop loss
                    if risk_per_share > 0:
                        shares_to_buy = min(
                            int(max_risk / risk_per_share),
                            int(current_capital * 0.1 / current_price)  # Max 10% allocation
                        )
                    else:
                        shares_to_buy = int(current_capital * 0.1 / current_price)
                    
                    if shares_to_buy > 0 and shares_to_buy * current_price <= current_capital:
                        # Execute buy
                        cost = shares_to_buy * current_price
                        position += shares_to_buy
                        avg_cost = (avg_cost * (position - shares_to_buy) + cost) / position
                        current_capital -= cost
                        
                        trades.append({
                            "timestamp": current_time,
                            "symbol": symbol,
                            "type": "BUY",
                            "quantity": shares_to_buy,
                            "price": current_price,
                            "cost": cost,
                            "capital_after": current_capital
                        })
                        
                elif signal == "SELL" and position > 0:  # Sell signal and holding long position
                    # Execute sell
                    proceeds = position * current_price
                    current_capital += proceeds
                    
                    trades.append({
                        "timestamp": current_time,
                        "symbol": symbol,
                        "type": "SELL",
                        "quantity": position,
                        "price": current_price,
                        "proceeds": proceeds,
                        "capital_after": current_capital
                    })
                    
                    # Calculate PnL for this trade
                    pnl = (current_price - avg_cost) * position
                    position = 0
                    avg_cost = 0
                
                # Calculate current equity (capital + unrealized PnL)
                current_equity = current_capital + (position * current_price if position > 0 else 0)
                equity_curve.append({
                    "timestamp": current_time,
                    "equity": current_equity
                })
                
                # Track maximum equity for drawdown calculation
                if current_equity > max_equity:
                    max_equity = current_equity
            
            # If still holding position at end, close it
            if position > 0:
                proceeds = position * current_price
                current_capital += proceeds
                pnl = (current_price - avg_cost) * position
                
                trades.append({
                    "timestamp": current_time,
                    "symbol": symbol,
                    "type": "SELL",
                    "quantity": position,
                    "price": current_price,
                    "proceeds": proceeds,
                    "capital_after": current_capital
                })
                
                position = 0
                avg_cost = 0
            
            # Calculate performance metrics
            final_capital = current_capital
            total_return = (final_capital - initial_capital_value) / initial_capital_value
            total_return_pct = total_return * 100
            
            # Calculate Sharpe ratio (simplified, using 0.03 as risk-free rate)
            if len(equity_curve) > 1:
                returns = []
                for i in range(1, len(equity_curve)):
                    prev_equity = equity_curve[i-1]["equity"]
                    curr_equity = equity_curve[i]["equity"]
                    if prev_equity > 0:
                        returns.append((curr_equity - prev_equity) / prev_equity)
                
                if returns:
                    avg_return = np.mean(returns) * len(returns)  # Annualized
                    risk_free_rate = 0.03 / 252  # Daily risk-free rate
                    excess_return = avg_return - risk_free_rate
                    volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
                    sharpe_ratio = excess_return / volatility if volatility != 0 else 0
                else:
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            # Calculate max drawdown
            max_drawdown = 0.0
            if equity_curve:
                running_max = equity_curve[0]["equity"]
                for point in equity_curve:
                    equity = point["equity"]
                    if equity > running_max:
                        running_max = equity
                    drawdown = (running_max - equity) / running_max
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
            
            # Calculate other metrics
            total_trades = len([t for t in trades if t["type"] == "SELL"])  # Only count closes
            winning_trades = 0
            losing_trades = 0
            total_pnl = final_capital - initial_capital_value
            
            for trade in trades:
                if trade["type"] == "SELL":
                    # For this simplified example, we're not calculating individual trade PnL
                    # In a real implementation, this would be more detailed
                    pass
            
            # Win rate calculation would require individual trade PnL
            # For now, we'll use a simplified approach
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Create backtest report
            report = BacktestReport(
                strategy_id=strategy.strategy_id,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital_value,
                final_capital=final_capital,
                total_return=total_return,
                annual_return=total_return * 252,  # Simplified annualization
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                profit_factor=0.0,  # Would need to calculate gains vs losses
                alpha=0.0,  # Would need benchmark for comparison
                beta=0.0,   # Would need benchmark for comparison
                data=str({"trades": trades, "equity_curve": equity_curve})  # Store as JSON string
            )
            
            logger.info(f"Backtest completed for strategy {strategy.name}. Total return: {total_return_pct:.2f}%")
            return report
            
        except CustomException:
            # Re-raise custom exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error running backtest for strategy {strategy.name}: {str(e)}")
            raise CustomException(f"Backtest failed due to internal error: {str(e)}", status_code=500)
    
    def _generate_signal(self, market_data: List[Dict], current_idx: int, symbol: str) -> str:
        """
        Generate a simple buy/sell signal based on technical indicators
        This is a very simplified implementation for demonstration
        """
        try:
            # This is a simple example - a real implementation would use actual strategy logic
            if current_idx < 20:  # Need at least 20 data points for indicators
                return "HOLD"
            
            # Simple moving average crossover example
            prices = [data["close"] for data in market_data[max(0, current_idx-20):current_idx+1]]
            
            if len(prices) < 20:
                return "HOLD"
            
            # Calculate simple moving averages
            sma_short = sum(prices[-5:]) / 5  # 5-period SMA
            sma_long = sum(prices[-20:]) / 20  # 20-period SMA
            
            # Generate signal based on crossover
            if sma_short > sma_long:  # Bullish signal
                return "BUY"
            elif sma_short < sma_long:  # Bearish signal
                return "SELL"
            else:
                return "HOLD"
        except Exception as e:
            logger.error(f"Error generating signal for {symbol} at index {current_idx}: {str(e)}")
            return "HOLD"  # Default to holding if there's an error

# Global backtest service instance
backtest_service = BacktestService()