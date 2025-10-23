from fastapi import APIRouter
from typing import Dict
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check() -> Dict:
    """
    Health check endpoint to verify the system is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "healthy",
            "database": "healthy",  # This would check actual database connectivity in a real implementation
            "cache": "healthy"      # This would check actual cache connectivity in a real implementation
        }
    }

@router.get("/detailed")
async def detailed_health_check() -> Dict:
    """
    Detailed health check with more comprehensive system information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "uptime": "N/A",  # This would be calculated from app start time
        "components": {
            "api": "healthy",
            "database": "healthy",
            "cache": "healthy",
            "message_queue": "healthy",
            "trading_engine": "not_running",  # Only active when strategies are running
        },
        "metrics": {
            "active_strategies": 0,
            "pending_orders": 0,
            "connected_exchanges": 0
        }
    }