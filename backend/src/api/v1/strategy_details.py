from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user
from src.services.strategy_report_service import strategy_report_service

router = APIRouter()

@router.get("/{strategy_id}/report", response_model=dict)
async def get_strategy_detailed_report(
    strategy_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    获取策略的详细报告
    """
    try:
        report = await strategy_report_service.get_strategy_report(strategy_id)
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy report: {str(e)}"
        )