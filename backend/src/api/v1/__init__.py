from fastapi import APIRouter

# API Router for version 1
api_router = APIRouter()

from . import strategies, orders, backtest, users, risk, indicators, dashboard

# Include all API routes
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])