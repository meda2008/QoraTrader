from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.strategy import Strategy
from ..models.backtest_report import BacktestReport

class StrategyService:
    def __init__(self, db: Session):
        self.db = db

    def create_strategy(self, name: str, description: str, version: str, config: dict = None, code_path: str = None) -> Strategy:
        """创建新策略"""
        strategy = Strategy(
            name=name,
            description=description,
            version=version,
            config=str(config) if config else None,
            code_path=code_path
        )
        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy

    def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """根据ID获取策略"""
        return self.db.query(Strategy).filter(Strategy.id == strategy_id).first()

    def get_strategies(self, skip: int = 0, limit: int = 100) -> List[Strategy]:
        """获取策略列表"""
        return self.db.query(Strategy).offset(skip).limit(limit).all()

    def update_strategy(self, strategy_id: str, **kwargs) -> Optional[Strategy]:
        """更新策略信息"""
        strategy = self.get_strategy(strategy_id)
        if strategy:
            for key, value in kwargs.items():
                setattr(strategy, key, value)
            self.db.commit()
            self.db.refresh(strategy)
        return strategy

    def delete_strategy(self, strategy_id: str) -> bool:
        """删除策略"""
        strategy = self.get_strategy(strategy_id)
        if strategy:
            self.db.delete(strategy)
            self.db.commit()
            return True
        return False

    def activate_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """激活策略"""
        strategy = self.get_strategy(strategy_id)
        if strategy and strategy.status != "已激活":
            strategy.status = "已激活"
            self.db.commit()
            self.db.refresh(strategy)
        return strategy

    def pause_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """暂停策略"""
        strategy = self.get_strategy(strategy_id)
        if strategy and strategy.status == "已激活":
            strategy.status = "暂停"
            self.db.commit()
            self.db.refresh(strategy)
        return strategy

    def stop_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """停止策略"""
        strategy = self.get_strategy(strategy_id)
        if strategy and strategy.status in ["已激活", "暂停"]:
            strategy.status = "已停止"
            self.db.commit()
            self.db.refresh(strategy)
        return strategy