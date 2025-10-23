from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.base import Strategy
from src.auth.security import get_current_active_user
from src.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse

router = APIRouter()

@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get all strategies for the current user
    """
    strategies = db.query(Strategy).filter(Strategy.user_id == current_user.id).all()
    return strategies

@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get a specific strategy by ID
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    return strategy

@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a new strategy
    """
    # Create new strategy instance
    strategy = Strategy(
        name=strategy_data.name,
        description=strategy_data.description,
        config=strategy_data.config,
        code=strategy_data.code,
        user_id=current_user.id
    )
    
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return strategy

@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: str,
    strategy_data: StrategyUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update an existing strategy
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    # Update strategy properties
    if strategy_data.name is not None:
        strategy.name = strategy_data.name
    if strategy_data.description is not None:
        strategy.description = strategy_data.description
    if strategy_data.config is not None:
        strategy.config = strategy_data.config
    if strategy_data.code is not None:
        strategy.code = strategy_data.code
    
    db.commit()
    db.refresh(strategy)
    
    return strategy

@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Delete a strategy
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    db.delete(strategy)
    db.commit()
    
    return {"message": "Strategy deleted successfully"}

@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Activate a strategy
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    strategy.status = "active"
    db.commit()
    db.refresh(strategy)
    
    return {"message": "Strategy activated successfully", "strategy": strategy}

@router.post("/{strategy_id}/deactivate")
async def deactivate_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Deactivate a strategy
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    strategy.status = "inactive"
    db.commit()
    db.refresh(strategy)
    
    return {"message": "Strategy deactivated successfully", "strategy": strategy}