from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.base import BacktestReport, Strategy
from src.auth.security import get_current_active_user
from src.schemas.backtest import BacktestCreate, BacktestResponse

router = APIRouter()

@router.get("/", response_model=List[BacktestResponse])
async def get_backtest_reports(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get all backtest reports for the current user
    """
    reports = db.query(BacktestReport).join(Strategy).filter(Strategy.user_id == current_user.id).all()
    return reports

@router.get("/{report_id}", response_model=BacktestResponse)
async def get_backtest_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get a specific backtest report by ID
    """
    report = db.query(BacktestReport).join(Strategy).filter(
        BacktestReport.id == report_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest report not found"
        )
    
    return report

@router.post("/", response_model=BacktestResponse)
async def create_backtest(
    backtest_data: BacktestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a new backtest
    """
    # Verify that the strategy belongs to the current user
    strategy = db.query(Strategy).filter(
        Strategy.id == backtest_data.strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot run backtest for strategy that doesn't belong to you"
        )
    
    # Create a new backtest report with status "processing"
    report = BacktestReport(
        strategy_id=backtest_data.strategy_id,
        start_date=backtest_data.start_date,
        end_date=backtest_data.end_date,
        initial_capital=backtest_data.initial_capital,
        final_capital=backtest_data.initial_capital,  # Will be updated after processing
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # In a real implementation, we would start the backtest in the background
    # For now, we'll just return the report with "processing" status
    
    return report