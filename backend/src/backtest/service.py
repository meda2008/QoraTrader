from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.backtest_task import BacktestTask
from ..models.backtest_report import BacktestReport
from ..models.strategy import Strategy

class BacktestService:
    def __init__(self, db: Session):
        self.db = db

    def create_backtest_task(
        self,
        strategy_id: str,
        task_name: str,
        initial_funds: float,
        start_time: str,
        end_time: str,
        parameters: dict = None
    ) -> BacktestTask:
        """创建回测任务"""
        task = BacktestTask(
            strategy_id=strategy_id,
            task_name=task_name,
            initial_funds=initial_funds,
            start_time=start_time,
            end_time=end_time,
            parameters=parameters or {}
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_backtest_task(self, task_id: str) -> Optional[BacktestTask]:
        """获取回测任务"""
        return self.db.query(BacktestTask).filter(BacktestTask.id == task_id).first()

    def get_backtest_tasks_by_strategy(self, strategy_id: str) -> List[BacktestTask]:
        """获取策略的所有回测任务"""
        return self.db.query(BacktestTask).filter(BacktestTask.strategy_id == strategy_id).all()

    def update_task_status(self, task_id: str, status: str) -> Optional[BacktestTask]:
        """更新任务状态"""
        task = self.get_backtest_task(task_id)
        if task:
            task.status = status
            self.db.commit()
            self.db.refresh(task)
        return task

    def create_backtest_report(
        self,
        strategy_id: str,
        backtest_name: str,
        start_time: str,
        end_time: str,
        initial_funds: float,
        final_funds: float,
        total_return: float,
        annualized_return: float,
        sharpe_ratio: float,
        max_drawdown: float,
        win_rate: float,
        profit_loss_ratio: float,
        trade_count: int,
        parameters: dict = None,
        detailed_trades: list = None
    ) -> BacktestReport:
        """创建回测报告"""
        report = BacktestReport(
            strategy_id=strategy_id,
            backtest_name=backtest_name,
            start_time=start_time,
            end_time=end_time,
            initial_funds=initial_funds,
            final_funds=final_funds,
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_loss_ratio=profit_loss_ratio,
            trade_count=trade_count,
            parameters=str(parameters) if parameters else None,
            detailed_trades=str(detailed_trades) if detailed_trades else None
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_backtest_report(self, report_id: str) -> Optional[BacktestReport]:
        """获取回测报告"""
        return self.db.query(BacktestReport).filter(BacktestReport.id == report_id).first()

    def get_backtest_reports_by_strategy(self, strategy_id: str) -> List[BacktestReport]:
        """获取策略的所有回测报告"""
        return self.db.query(BacktestReport).filter(BacktestReport.strategy_id == strategy_id).all()