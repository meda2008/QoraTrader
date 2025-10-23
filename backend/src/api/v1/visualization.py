from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user
from src.services.visualization_service import visualization_service

router = APIRouter()

@router.get("/signal-trade-visualization", response_model=dict)
async def get_signal_trade_visualization(
    strategy_id: str = Query(..., description="策略ID"),
    symbol: str = Query(..., description="交易标的"),
    start_date: str = Query(..., description="开始日期 (ISO format)"),
    end_date: str = Query(..., description="结束日期 (ISO format)"),
    current_user = Depends(get_current_active_user)
):
    """
    获取策略信号与成交的可视化数据
    """
    try:
        visualization_data = await visualization_service.get_signal_trade_visualization_data(
            strategy_id, symbol, start_date, end_date
        )
        return visualization_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get visualization data: {str(e)}"
        )