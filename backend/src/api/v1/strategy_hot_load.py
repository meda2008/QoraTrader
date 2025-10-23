"""
API endpoints for strategy hot loading
These endpoints handle hot loading, unloading, and management of trading strategies
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.strategies.hot_loader import strategy_hot_loader
from src.models.base import Strategy
from src.utils.error_handler import CustomException

router = APIRouter()

@router.post("/hot-load", response_model=Dict)
async def hot_load_strategy(
    strategy_data: Dict[str, Any] = Body(...),
    current_user = Depends(require_role("admin"))
):
    """
    Hot load a trading strategy
    """
    try:
        # Validate required fields
        required_fields = ['strategy_id', 'strategy_code']
        for field in required_fields:
            if field not in strategy_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        strategy_id = strategy_data['strategy_id']
        strategy_code = strategy_data['strategy_code']
        config = strategy_data.get('config', {})
        
        # Reload the strategy
        success = strategy_hot_loader.reload_strategy(strategy_id, strategy_code, config)
        
        if success:
            return {
                "strategy_id": strategy_id,
                "status": "loaded",
                "message": f"Strategy {strategy_id} loaded successfully",
                "loaded_at": "2023-10-22T10:30:00Z"  # In a real implementation, this would be the actual timestamp
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load strategy {strategy_id}"
            )
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to hot load strategy: {str(e)}"
        )

@router.post("/{strategy_id}/unload")
async def unload_strategy(
    strategy_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    Unload a trading strategy
    """
    try:
        success = strategy_hot_loader.unload_strategy(strategy_id)
        
        if success:
            return {
                "strategy_id": strategy_id,
                "status": "unloaded",
                "message": f"Strategy {strategy_id} unloaded successfully",
                "unloaded_at": "2023-10-22T10:30:00Z"  # In a real implementation, this would be the actual timestamp
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to unload strategy {strategy_id}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unload strategy: {str(e)}"
        )

@router.post("/{strategy_id}/reload")
async def reload_strategy(
    strategy_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    Reload a trading strategy
    """
    try:
        success = strategy_hot_loader.reload_strategy(strategy_id)
        
        if success:
            return {
                "strategy_id": strategy_id,
                "status": "reloaded",
                "message": f"Strategy {strategy_id} reloaded successfully",
                "reloaded_at": "2023-10-22T10:30:00Z"  # In a real implementation, this would be the actual timestamp
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reload strategy {strategy_id}"
            )
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload strategy: {str(e)}"
        )

@router.get("/{strategy_id}/hot-load-status", response_model=Dict)
async def get_strategy_hot_load_status(
    strategy_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get the hot load status of a trading strategy
    """
    try:
        status_info = strategy_hot_loader.get_strategy_status(strategy_id)
        return status_info
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy status: {str(e)}"
        )

@router.get("/loaded-strategies", response_model=Dict)
async def list_loaded_strategies(
    current_user = Depends(get_current_active_user)
):
    """
    List all currently loaded strategies
    """
    try:
        strategies = strategy_hot_loader.list_loaded_strategies()
        return {
            "loaded_strategies": strategies,
            "count": len(strategies)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list loaded strategies: {str(e)}"
        )

@router.get("/{strategy_id}/validate", response_model=Dict)
async def validate_strategy_code(
    strategy_id: str,
    strategy_data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_active_user)
):
    """
    Validate strategy code before hot loading
    """
    try:
        # In a real implementation, this would actually validate the Python code
        # For now, we'll just check basic structure
        strategy_code = strategy_data.get('strategy_code', '')
        
        # Basic validation
        if not strategy_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Strategy code is required"
            )
        
        # Check for basic Python syntax (simplified)
        if 'def strategy_logic(' not in strategy_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Strategy code must contain a 'strategy_logic' function"
            )
        
        return {
            "strategy_id": strategy_id,
            "valid": True,
            "message": "Strategy code appears valid",
            "validation_time": "2023-10-22T10:30:00Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate strategy code: {str(e)}"
        )