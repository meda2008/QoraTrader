"""
API endpoints for strategy parameter updates
These endpoints handle updating strategy parameters in real-time without stopping the strategy
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.services.strategy_param_service import strategy_param_service
from src.models.base import Strategy
from src.utils.error_handler import CustomException

router = APIRouter()

@router.put("/{strategy_id}/parameters", response_model=Dict)
async def update_strategy_parameters(
    strategy_id: str,
    param_updates: Dict[str, Any] = Body(...),
    current_user = Depends(require_role("admin"))
):
    """
    Update strategy parameters in real-time
    """
    try:
        # Validate that param_updates is not empty
        if not param_updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parameter updates are required"
            )
        
        # Update strategy parameters
        updated_strategy = strategy_param_service.update_strategy_parameters(strategy_id, param_updates)
        
        return {
            "strategy_id": updated_strategy.id,
            "name": updated_strategy.name,
            "message": "Strategy parameters updated successfully",
            "updated_at": updated_strategy.updated_at.isoformat() if updated_strategy.updated_at else None,
            "updated_parameters": list(param_updates.keys())
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update strategy parameters: {str(e)}"
        )

@router.patch("/{strategy_id}/parameters/{param_name}", response_model=Dict)
async def update_single_strategy_parameter(
    strategy_id: str,
    param_name: str,
    param_value: Any = Body(..., embed=True),
    current_user = Depends(require_role("admin"))
):
    """
    Update a single strategy parameter
    """
    try:
        # Create parameter update dict
        param_update = {param_name: param_value}
        
        # Update strategy parameter
        updated_strategy = strategy_param_service.update_strategy_parameters(strategy_id, param_update)
        
        return {
            "strategy_id": updated_strategy.id,
            "name": updated_strategy.name,
            "message": f"Strategy parameter '{param_name}' updated successfully",
            "updated_at": updated_strategy.updated_at.isoformat() if updated_strategy.updated_at else None,
            "updated_parameter": param_name,
            "new_value": param_value
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update strategy parameter: {str(e)}"
        )

@router.get("/{strategy_id}/parameters", response_model=Dict)
async def get_strategy_parameters(
    strategy_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get current strategy parameters
    """
    try:
        from sqlalchemy.orm import Session
        db: Session = next(get_db())
        
        # Get strategy from database
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy with ID {strategy_id} not found"
            )
        
        # Parse strategy config (assuming it's JSON)
        import json
        try:
            config = json.loads(strategy.config) if strategy.config else {}
        except json.JSONDecodeError:
            config = {}
        
        return {
            "strategy_id": strategy.id,
            "name": strategy.name,
            "parameters": config,
            "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
            "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy parameters: {str(e)}"
        )
    finally:
        db.close()

@router.delete("/{strategy_id}/parameters/{param_name}", response_model=Dict)
async def remove_strategy_parameter(
    strategy_id: str,
    param_name: str,
    current_user = Depends(require_role("admin"))
):
    """
    Remove a strategy parameter
    """
    try:
        # Remove strategy parameter
        updated_strategy = strategy_param_service.remove_strategy_parameter(strategy_id, param_name)
        
        return {
            "strategy_id": updated_strategy.id,
            "name": updated_strategy.name,
            "message": f"Strategy parameter '{param_name}' removed successfully",
            "updated_at": updated_strategy.updated_at.isoformat() if updated_strategy.updated_at else None,
            "removed_parameter": param_name
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove strategy parameter: {str(e)}"
        )

@router.post("/{strategy_id}/parameters/reset", response_model=Dict)
async def reset_strategy_parameters(
    strategy_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    Reset strategy parameters to default values
    """
    try:
        # Reset strategy parameters
        updated_strategy = strategy_param_service.reset_strategy_parameters(strategy_id)
        
        return {
            "strategy_id": updated_strategy.id,
            "name": updated_strategy.name,
            "message": "Strategy parameters reset to default values successfully",
            "updated_at": updated_strategy.updated_at.isoformat() if updated_strategy.updated_at else None
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset strategy parameters: {str(e)}"
        )

@router.post("/{strategy_id}/parameters/validate", response_model=Dict)
async def validate_strategy_parameters(
    strategy_id: str,
    param_updates: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_active_user)
):
    """
    Validate strategy parameters before updating
    """
    try:
        # Validate strategy parameters
        validation_result = strategy_param_service.validate_strategy_parameters(strategy_id, param_updates)
        
        return {
            "strategy_id": strategy_id,
            "valid": validation_result["valid"],
            "message": validation_result["message"],
            "validation_time": "2023-10-22T10:30:00Z",  # Actual timestamp in real implementation
            "validated_parameters": list(param_updates.keys()) if param_updates else []
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate strategy parameters: {str(e)}"
        )

@router.get("/{strategy_id}/parameters/history", response_model=Dict)
async def get_parameter_update_history(
    strategy_id: str,
    limit: int = 10,
    current_user = Depends(get_current_active_user)
):
    """
    Get history of parameter updates for a strategy
    """
    try:
        # In a real implementation, this would query a parameter history table
        # For now, we'll return mock data
        history_data = [
            {
                "timestamp": "2023-10-22T10:30:00Z",
                "parameter": "threshold",
                "old_value": 0.05,
                "new_value": 0.07,
                "updated_by": "admin_user"
            },
            {
                "timestamp": "2023-10-21T15:45:00Z",
                "parameter": "window_size",
                "old_value": 20,
                "new_value": 25,
                "updated_by": "admin_user"
            }
        ]
        
        return {
            "strategy_id": strategy_id,
            "history": history_data[:limit],
            "count": len(history_data[:limit])
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get parameter update history: {str(e)}"
        )