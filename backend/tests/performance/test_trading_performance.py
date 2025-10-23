"""
Performance tests for core trading path
These tests verify that the core trading path meets the <1ms P99 latency requirement
"""
import time
import asyncio
import pytest
from typing import List
from src.trading.engine import trading_engine
from src.models.base import Order, OrderType, OrderSide
from src.utils.error_handler import CustomException

# Mock market data service for performance testing
class MockMarketDataService:
    @staticmethod
    async def get_data(symbol: str, data_type: str, start_time=None, end_time=None):
        return [{"timestamp": "2023-01-01T00:00:00", "close": 100.0}]

# Performance test parameters
NUM_ORDERS_PER_TEST = 1000
WARMUP_ROUNDS = 100

async def measure_order_execution_performance():
    """
    Measure the performance of order execution in the trading engine
    """
    # Initialize trading engine
    await trading_engine.start()
    
    # Warmup period to ensure the engine is fully operational
    for _ in range(WARMUP_ROUNDS):
        order = Order(
            id=f"warmup_order_{_}",
            strategy_id="perf_test_strategy",
            symbol="AAPL",
            order_type=OrderType.LIMIT,
            side=OrderSide.BUY,
            quantity=100,
            price=150.0
        )
        try:
            await trading_engine.submit_order(order)
        except:
            pass  # Ignore errors during warmup
    
    # Measure performance for actual test
    execution_times = []
    
    for i in range(NUM_ORDERS_PER_TEST):
        order = Order(
            id=f"perf_test_order_{i}",
            strategy_id="perf_test_strategy",
            symbol="AAPL",
            order_type=OrderType.LIMIT,
            side=OrderSide.BUY,
            quantity=100,
            price=150.0
        )
        
        start_time = time.perf_counter()
        try:
            await trading_engine.submit_order(order)
        except Exception as e:
            # If there's an error, we still record the time
            pass
        end_time = time.perf_counter()
        
        execution_time_ms = (end_time - start_time) * 1000
        execution_times.append(execution_time_ms)
    
    # Calculate performance metrics
    execution_times.sort()
    p50 = execution_times[len(execution_times) // 2]
    p90 = execution_times[int(0.9 * len(execution_times))]
    p95 = execution_times[int(0.95 * len(execution_times))]
    p99 = execution_times[int(0.99 * len(execution_times))]
    
    # Clean up
    await trading_engine.stop()
    
    return {
        "p50": p50,
        "p90": p90,
        "p95": p95,
        "p99": p99,
        "min": min(execution_times),
        "max": max(execution_times),
        "avg": sum(execution_times) / len(execution_times),
        "count": len(execution_times)
    }

def test_core_trading_path_latency():
    """
    Test that the core trading path meets the <1ms P99 latency requirement
    """
    # Run the performance test
    import asyncio
    perf_metrics = asyncio.run(measure_order_execution_performance())
    
    print(f"Performance metrics:")
    print(f"  P50: {perf_metrics['p50']:.3f}ms")
    print(f"  P90: {perf_metrics['p90']:.3f}ms") 
    print(f"  P95: {perf_metrics['p95']:.3f}ms")
    print(f"  P99: {perf_metrics['p99']:.3f}ms")
    print(f"  AVG: {perf_metrics['avg']:.3f}ms")
    print(f"  MIN: {perf_metrics['min']:.3f}ms")
    print(f"  MAX: {perf_metrics['max']:.3f}ms")
    
    # Assert that P99 is less than 1ms as required
    assert perf_metrics['p99'] < 1.0, f"P99 latency {perf_metrics['p99']:.3f}ms exceeds 1ms requirement"
    
    print("✅ Core trading path latency requirement (<1ms P99) satisfied")

if __name__ == "__main__":
    test_core_trading_path_latency()