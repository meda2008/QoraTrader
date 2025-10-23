"""
API endpoints for custom indicator registration
These endpoints handle registration, management, and calculation of custom technical indicators
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.indicators.custom_loader import custom_indicator_loader
from src.models.base import IndicatorLibrary
from src.utils.error_handler import CustomException

router = APIRouter()

@router.post("/register-custom", response_model=Dict)
async def register_custom_indicator(
    indicator_data: Dict[str, Any] = Body(...),
    current_user = Depends(require_role("admin"))
):
    """
    Register a custom technical indicator
    """
    try:
        indicator_library = custom_indicator_loader.register_custom_indicator(indicator_data)
        
        return {
            "id": indicator_library.id,
            "name": indicator_library.name,
            "description": indicator_library.description,
            "version": indicator_library.version,
            "path": indicator_library.path,
            "is_active": indicator_library.is_active,
            "created_at": indicator_library.created_at.isoformat() if indicator_library.created_at else None,
            "updated_at": indicator_library.updated_at.isoformat() if indicator_library.updated_at else None
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register custom indicator: {str(e)}"
        )

@router.get("/custom-list", response_model=List[Dict])
async def list_custom_indicators(
    current_user = Depends(get_current_active_user)
):
    """
    List all custom technical indicators
    """
    try:
        indicators = custom_indicator_loader.list_custom_indicators()
        return indicators
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list custom indicators: {str(e)}"
        )

@router.post("/calculate-custom", response_model=Dict)
async def calculate_custom_indicator(
    calculation_data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_active_user)
):
    """
    Calculate a custom technical indicator
    """
    try:
        # Validate required fields
        required_fields = ['indicator_id', 'input_data', 'parameters']
        for field in required_fields:
            if field not in calculation_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Calculate the indicator
        result = custom_indicator_loader.calculate_custom_indicator(
            calculation_data['indicator_id'],
            calculation_data['input_data'],
            calculation_data['parameters']
        )
        
        return {
            "indicator_id": calculation_data['indicator_id'],
            "input_data": calculation_data['input_data'],
            "parameters": calculation_data['parameters'],
            "result": result
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate custom indicator: {str(e)}"
        )

@router.delete("/remove-custom/{indicator_id}")
async def remove_custom_indicator(
    indicator_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    Remove a custom technical indicator
    """
    try:
        success = custom_indicator_loader.remove_custom_indicator(indicator_id)
        if success:
            return {"message": f"Custom indicator {indicator_id} removed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Custom indicator {indicator_id} not found"
            )
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove custom indicator: {str(e)}"
        )

@router.post("/{indicator_id}/activate")
async def activate_custom_indicator(
    indicator_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    Activate a custom technical indicator
    """
    try:
        indicator_library = custom_indicator_loader.activate_custom_indicator(indicator_id)
        
        return {
            "id": indicator_library.id,
            "name": indicator_library.name,
            "description": indicator_library.description,
            "version": indicator_library.version,
            "path": indicator_library.path,
            "is_active": indicator_library.is_active,
            "created_at": indicator_library.created_at.isoformat() if indicator_library.created_at else None,
            "updated_at": indicator_library.updated_at.isoformat() if indicator_library.updated_at else None
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate custom indicator: {str(e)}"
        )

@router.post("/{indicator_id}/deactivate")
async def deactivate_custom_indicator(
    indicator_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    Deactivate a custom technical indicator
    """
    try:
        indicator_library = custom_indicator_loader.deactivate_custom_indicator(indicator_id)
        
        return {
            "id": indicator_library.id,
            "name": indicator_library.name,
            "description": indicator_library.description,
            "version": indicator_library.version,
            "path": indicator_library.path,
            "is_active": indicator_library.is_active,
            "created_at": indicator_library.created_at.isoformat() if indicator_library.created_at else None,
            "updated_at": indicator_library.updated_at.isoformat() if indicator_library.updated_at else None
        }
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate custom indicator: {str(e)}"
        )

@router.get("/{indicator_id}/info")
async def get_custom_indicator_info(
    indicator_id: str,
    current_user = Depends(get_current_active_user)
):
    """
    Get information about a custom technical indicator
    """
    try:
        from sqlalchemy.orm import Session
        db: Session = next(get_db())
        
        indicator = db.query(IndicatorLibrary).filter(
            IndicatorLibrary.id == indicator_id
        ).first()
        
        if not indicator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Custom indicator {indicator_id} not found"
            )
        
        return {
            "id": indicator.id,
            "name": indicator.name,
            "description": indicator.description,
            "version": indicator.version,
            "path": indicator.path,
            "is_active": indicator.is_active,
            "created_at": indicator.created_at.isoformat() if indicator.created_at else None,
            "updated_at": indicator.updated_at.isoformat() if indicator.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get custom indicator info: {str(e)}"
        )
    finally:
        db.close()