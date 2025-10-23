from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from src.auth.security import get_current_active_user
from src.indicators.service import IndicatorService
from src.schemas.indicator import IndicatorCalculationRequest, IndicatorInfoResponse

router = APIRouter()

@router.get("/list", response_model=List[str])
async def list_indicators(
    current_user = Depends(get_current_active_user)
):
    """
    List all available indicators
    """
    indicator_service = IndicatorService()
    return indicator_service.list_indicators()

@router.post("/calculate")
async def calculate_indicator(
    request: IndicatorCalculationRequest,
    current_user = Depends(get_current_active_user)
):
    """
    Calculate an indicator
    """
    indicator_service = IndicatorService()
    
    try:
        result = indicator_service.calculate(
            request.indicator_name,
            request.data,
            **request.params
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{indicator_name}", response_model=IndicatorInfoResponse)
async def get_indicator_info(
    indicator_name: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get information about a specific indicator
    """
    indicator_service = IndicatorService()
    
    try:
        info = indicator_service.get_indicator_info(indicator_name)
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )