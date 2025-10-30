from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ... import models
from .schemas.strategy import Strategy, StrategyCreate, StrategyUpdate
from ...database import get_db
from ...services.strategy_service import StrategyService

router = APIRouter()

@router.get("/", response_model=List[Strategy])
def get_strategies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取策略列表"""
    strategies = db.query(models.Strategy).offset(skip).limit(limit).all()
    return strategies

@router.post("/", response_model=Strategy)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """创建新策略"""
    db_strategy = models.Strategy(
        name=strategy.name,
        description=strategy.description,
        version=strategy.version,
        config=strategy.config,
        code_path=strategy.code_path
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@router.get("/{strategy_id}", response_model=Strategy)
def get_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """获取特定策略"""
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy

@router.put("/{strategy_id}", response_model=Strategy)
def update_strategy(strategy_id: str, strategy: StrategyUpdate, db: Session = Depends(get_db)):
    """更新策略"""
    db_strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    for key, value in strategy.dict(exclude_unset=True).items():
        setattr(db_strategy, key, value)
    
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """删除策略"""
    strategy = db.query(models.Strategy).filter(models.Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(strategy)
    db.commit()
    return

@router.post("/{strategy_id}/activate", response_model=Strategy)
def activate_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """激活策略"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.activate_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found or could not be activated")
    return strategy

@router.post("/{strategy_id}/pause", response_model=Strategy)
def pause_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """暂停策略"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.pause_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found or could not be paused")
    return strategy

@router.post("/{strategy_id}/stop", response_model=Strategy)
def stop_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """停止策略"""
    strategy_service = StrategyService(db)
    strategy = strategy_service.stop_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found or could not be stopped")
    return strategy