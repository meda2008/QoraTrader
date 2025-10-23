from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user
from src.services.report_service import report_service

router = APIRouter()

@router.get("/trading-report", response_model=dict)
async def generate_trading_report(
    strategy_id: str = Query(..., description="策略ID"),
    start_date: str = Query(..., description="开始日期 (ISO format)"),
    end_date: str = Query(..., description="结束日期 (ISO format)"),
    current_user = Depends(get_current_active_user)
):
    """
    生成交易报告
    """
    try:
        report = await report_service.generate_trading_report(strategy_id, start_date, end_date)
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate trading report: {str(e)}"
        )