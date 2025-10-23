from fastapi import APIRouter
from src.api.v1 import strategies, orders, accounts, positions, backtest, indicators, health

api_router = APIRouter()

# Include all API routes
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
api_router.include_router(health.router, prefix="/health", tags=["health"])