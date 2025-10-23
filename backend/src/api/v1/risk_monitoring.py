from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.services.risk_metrics_service import risk_metrics_service

router = APIRouter()

@router.get("/account-risk/{account_id}", response_model=dict)
async def get_account_risk_metrics(
    account_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    获取账户的风险指标
    """
    try:
        risk_metrics = await risk_metrics_service.calculate_account_risk_metrics(account_id)
        return risk_metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account risk metrics: {str(e)}"
        )

@router.get("/system-risk", response_model=dict)
async def get_system_wide_risk_metrics(
    current_user = Depends(require_role("admin"))
):
    """
    获取全系统的风险指标（仅管理员）
    """
    try:
        system_risk_metrics = await risk_metrics_service.calculate_system_wide_risk_metrics()
        return system_risk_metrics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system risk metrics: {str(e)}"
        )

@router.get("/volatile-positions", response_model=List[dict])
async def get_volatile_positions(
    threshold: float = 0.05,
    current_user = Depends(require_role("admin"))
):
    """
    获取波动较大的持仓（仅管理员）
    """
    try:
        volatile_positions = await risk_metrics_service.get_volatile_positions(threshold)
        return volatile_positions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get volatile positions: {str(e)}"
        )