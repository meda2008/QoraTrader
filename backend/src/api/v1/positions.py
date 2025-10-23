from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.base import Position, Strategy
from src.auth.security import get_current_active_user
from src.schemas.position import PositionResponse

router = APIRouter()

@router.get("/", response_model=List[PositionResponse])
async def get_positions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get all positions for the current user
    """
    positions = db.query(Position).join(Strategy).filter(Strategy.user_id == current_user.id).all()
    return positions

@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get a specific position by ID
    """
    position = db.query(Position).join(Strategy).filter(
        Position.id == position_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    return position