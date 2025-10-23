from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.services.strategy_monitor import strategy_monitor_service
from src.schemas.strategy import StrategyResponse

router = APIRouter()

@router.get("/status", response_model=List[dict])
async def get_all_strategies_status(
    current_user = Depends(get_current_active_user)
):
    """
    获取所有策略的状态信息
    """
    try:
        status_list = await strategy_monitor_service.get_all_strategies_status()
        return status_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategies status: {str(e)}"
        )

@router.get("/{strategy_id}/status", response_model=dict)
async def get_strategy_status(
    strategy_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    获取特定策略的状态信息
    """
    try:
        status_info = await strategy_monitor_service.get_strategy_status(strategy_id)
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy status: {str(e)}"
        )

@router.post("/{strategy_id}/refresh-status")
async def refresh_strategy_status(
    strategy_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    刷新特定策略的状态
    """
    try:
        success = await strategy_monitor_service.refresh_strategy_status(strategy_id)
        if success:
            return {"message": f"Status for strategy {strategy_id} refreshed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to refresh status for strategy {strategy_id}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh strategy status: {str(e)}"
        )