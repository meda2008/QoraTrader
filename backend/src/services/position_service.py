from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.position import Position
from ..models.account import Account
from ..models.strategy import Strategy

class PositionService:
    def __init__(self, db: Session):
        self.db = db

    def get_position(self, account_id: str, strategy_id: str, symbol: str) -> Optional[Position]:
        """获取特定账户、策略和交易标的的持仓"""
        return self.db.query(Position).filter(
            Position.account_id == account_id,
            Position.strategy_id == strategy_id,
            Position.symbol == symbol
        ).first()

    def get_positions_by_account(self, account_id: str) -> List[Position]:
        """获取账户的所有持仓"""
        return self.db.query(Position).filter(Position.account_id == account_id).all()

    def get_positions_by_strategy(self, strategy_id: str) -> List[Position]:
        """获取策略的所有持仓"""
        return self.db.query(Position).filter(Position.strategy_id == strategy_id).all()

    def update_position(self, account_id: str, strategy_id: str, symbol: str, 
                       direction: str, quantity: int, available_quantity: int, 
                       cost: float, current_price: float = None) -> Position:
        """更新持仓信息"""
        position = self.get_position(account_id, strategy_id, symbol)
        if position:
            # 更新现有持仓
            position.position_quantity += quantity
            position.available_quantity += available_quantity
            if cost > 0:  # 如果提供了成本价，则更新
                total_qty = position.position_quantity
                if total_qty > 0:
                    position.position_cost = ((position.position_cost * (total_qty - quantity)) + (cost * quantity)) / total_qty
            if current_price:
                position.current_price = current_price
                position.floating_pnl = (current_price - position.position_cost) * position.position_quantity
                if position.position_cost != 0:
                    position.pnl_ratio = (current_price - position.position_cost) / position.position_cost * 100
        else:
            # 创建新持仓
            position = Position(
                account_id=account_id,
                strategy_id=strategy_id,
                symbol=symbol,
                direction=direction,
                position_quantity=quantity,
                available_quantity=available_quantity,
                position_cost=cost,
                current_price=current_price or cost,
            )
            if current_price:
                position.floating_pnl = (current_price - cost) * quantity
                if cost != 0:
                    position.pnl_ratio = (current_price - cost) / cost * 100
            self.db.add(position)
        
        self.db.commit()
        if position:
            self.db.refresh(position)
        return position

    def reduce_position(self, account_id: str, strategy_id: str, symbol: str, 
                        quantity: int, current_price: float = None) -> Optional[Position]:
        """减少持仓（平仓）"""
        position = self.get_position(account_id, strategy_id, symbol)
        if position and position.position_quantity >= quantity:
            position.position_quantity -= quantity
            position.available_quantity -= quantity
            
            if current_price:
                position.current_price = current_price
                position.floating_pnl = (current_price - position.position_cost) * position.position_quantity
                if position.position_cost != 0:
                    position.pnl_ratio = (current_price - position.position_cost) / position.position_cost * 100
            
            # 如果持仓数量为0，可以考虑删除记录或保留以供历史查询
            if position.position_quantity == 0:
                position.position_cost = 0.0
            
            self.db.commit()
            self.db.refresh(position)
        
        return position