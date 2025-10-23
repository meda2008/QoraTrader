from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
import logging
from src.models.base import Strategy, BacktestReport
from src.services.backtest_service import BacktestService
from src.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)

class BacktestEngine:
    """
    Engine for running strategy backtests
    """
    
    def __init__(self):
        self.backtest_service = BacktestService()
        self.active_backtests = {}  # Track running backtests
        logger.info("Backtest engine initialized")
    
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
        logger.info(f"Starting backtest engine for strategy {strategy.name}")
        
        try:
            # Activate the strategy for backtesting
            strategy.activate()
            
            # Run the backtest through the service
            report = await self.backtest_service.run_backtest(
                strategy=strategy,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                data_frequency=data_frequency
            )
            
            logger.info(f"Backtest completed for strategy {strategy.name}")
            return report
            
        except Exception as e:
            logger.error(f"Error in backtest engine for strategy {strategy.name}: {str(e)}")
            raise
        finally:
            # Deactivate the strategy after backtesting
            strategy.deactivate()
    
    async def run_parameter_optimization(
        self,
        strategy_class,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float,
        param_ranges: Dict[str, List[Any]],
        optimization_metric: str = "sharpe_ratio"
    ) -> Dict[str, Any]:
        """
        Run parameter optimization for a strategy
        This is a simplified implementation - real implementation would use more sophisticated algorithms
        """
        logger.info(f"Starting parameter optimization for strategy {strategy_class.__name__}")
        
        best_params = {}
        best_metric_value = float('-inf') if optimization_metric in ['sharpe_ratio', 'total_return', 'win_rate'] else float('inf')
        results = []
        
        # Generate all parameter combinations (grid search)
        param_combinations = self._generate_param_combinations(param_ranges)
        
        for params in param_combinations:
            try:
                # Create strategy instance with specific parameters
                strategy = strategy_class(
                    strategy_id="temp",
                    name=f"Optimization-{hash(str(params))}",
                    config=params
                )
                
                # Run backtest with these parameters
                report = await self.run_backtest(
                    strategy,
                    symbol,
                    start_date,
                    end_date,
                    initial_capital
                )
                
                # Extract the optimization metric
                metric_value = getattr(report, optimization_metric, 0)
                
                result = {
                    "params": params,
                    "metric_value": metric_value,
                    "report": report
                }
                
                results.append(result)
                
                # Update best parameters if this is better
                if optimization_metric in ['sharpe_ratio', 'total_return', 'win_rate']:  # Higher is better
                    if metric_value > best_metric_value:
                        best_metric_value = metric_value
                        best_params = params
                else:  # Lower is better (e.g., max_drawdown)
                    if metric_value < best_metric_value:
                        best_metric_value = metric_value
                        best_params = params
                        
            except Exception as e:
                logger.error(f"Error testing parameter combination {params}: {str(e)}")
        
        logger.info(f"Parameter optimization completed for strategy {strategy_class.__name__}")
        
        return {
            "best_params": best_params,
            "best_metric_value": best_metric_value,
            "all_results": results
        }
    
    def _generate_param_combinations(self, param_ranges: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Generate all combinations of parameters from the provided ranges
        """
        import itertools
        
        # Get all parameter names and their possible values
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        
        # Generate all combinations
        combinations = list(itertools.product(*param_values))
        
        # Convert to list of dictionaries
        param_combinations = []
        for combo in combinations:
            param_dict = {}
            for i, name in enumerate(param_names):
                param_dict[name] = combo[i]
            param_combinations.append(param_dict)
        
        return param_combinations

# Global backtest engine instance
backtest_engine = BacktestEngine()