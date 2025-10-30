from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models
from .schemas.backtest import BacktestTask as BacktestTaskSchema, BacktestReport as BacktestReportSchema
from ..database import get_db
from ..backtest.service import BacktestService

router = APIRouter()

@router.post("/", response_model=BacktestTaskSchema)
def create_backtest_task(
    strategy_id: str,
    task_name: str,
    initial_funds: float,
    start_time: str,
    end_time: str,
    parameters: dict = None,
    db: Session = Depends(get_db)
):
    """创建回测任务"""
    backtest_service = BacktestService(db)
    task = backtest_service.create_backtest_task(
        strategy_id=strategy_id,
        task_name=task_name,
        initial_funds=initial_funds,
        start_time=start_time,
        end_time=end_time,
        parameters=parameters
    )
    return task

@router.get("/{task_id}", response_model=BacktestTaskSchema)
def get_backtest_task(task_id: str, db: Session = Depends(get_db)):
    """获取回测任务详情"""
    backtest_service = BacktestService(db)
    task = backtest_service.get_backtest_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Backtest task not found")
    return task

@router.get("/strategy/{strategy_id}", response_model=List[BacktestTaskSchema])
def get_backtest_tasks_by_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """获取策略的所有回测任务"""
    backtest_service = BacktestService(db)
    tasks = backtest_service.get_backtest_tasks_by_strategy(strategy_id)
    return tasks

@router.get("/report/{report_id}", response_model=BacktestReportSchema)
def get_backtest_report(report_id: str, db: Session = Depends(get_db)):
    """获取回测报告"""
    backtest_service = BacktestService(db)
    report = backtest_service.get_backtest_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Backtest report not found")
    return report

@router.get("/report/strategy/{strategy_id}", response_model=List[BacktestReportSchema])
def get_backtest_reports_by_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """获取策略的所有回测报告"""
    backtest_service = BacktestService(db)
    reports = backtest_service.get_backtest_reports_by_strategy(strategy_id)
    return reports