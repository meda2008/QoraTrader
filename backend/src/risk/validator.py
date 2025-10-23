from typing import Dict, Optional
import logging
from src.models.base import RiskParams, Order, Account, Position
from src.database import get_db
from src.services.risk_rule_service import risk_rule_service
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class RiskValidator:
    """
    风控验证器，用于在订单执行前验证是否符合风控规则
    """
    
    def __init__(self):
        logger.info("Risk validator initialized")
    
    async def validate_order(self, order: Order) -> Dict:
        """
        验证订单是否符合风控规则
        """
        try:
            # 首先通过服务验证订单
            order_data = {
                "price": float(order.price) if order.price else 0,
                "quantity": float(order.quantity),
                "symbol": order.symbol
            }
            
            validation_result = await risk_rule_service.validate_order_against_risk_rules(
                order.strategy_id, 
                order_data
            )
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating order {order.id}: {str(e)}")
            raise CustomException(f"Risk validation failed: {str(e)}", 500)
    
    async def check_account_risk_limits(self, account_id: str) -> Dict:
        """
        检查账户是否超过风险限制
        """
        try:
            # 获取账户的风控规则
            global_rules = await risk_rule_service.get_global_risk_rules()
            account_rules = []  # 实际上应该从数据库获取账户特定的风控规则
            
            # 这里我们只检查全局规则
            violations = []
            
            # 实现具体的风控检查逻辑
            # 例如：检查账户总亏损是否超过日亏损限制
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            try:
                account = db.query(Account).filter(Account.id == account_id).first()
                if account:
                    for rule in global_rules:
                        if rule.max_daily_loss and account.daily_pnl and account.daily_pnl < -float(rule.max_daily_loss):
                            violations.append({
                                "rule_id": rule.id,
                                "type": "daily_loss_limit",
                                "limit": float(rule.max_daily_loss),
                                "actual": float(account.daily_pnl),
                                "message": f"Daily loss {account.daily_pnl} exceeds limit {rule.max_daily_loss}"
                            })
                        
                        if rule.max_drawdown and account.total_pnl and account.market_value:
                            current_drawdown = abs(account.total_pnl) / float(account.market_value) if float(account.market_value) != 0 else 0
                            if current_drawdown > float(rule.max_drawdown):
                                violations.append({
                                    "rule_id": rule.id,
                                    "type": "max_drawdown",
                                    "limit": float(rule.max_drawdown),
                                    "actual": current_drawdown,
                                    "message": f"Current drawdown {current_drawdown} exceeds limit {rule.max_drawdown}"
                                })
            finally:
                db.close()
            
            return {
                "account_id": account_id,
                "violations": violations,
                "is_valid": len(violations) == 0
            }
        except Exception as e:
            logger.error(f"Error checking account risk limits for {account_id}: {str(e)}")
            raise CustomException(f"Failed to check account risk limits: {str(e)}", 500)
    
    async def enforce_risk_controls(self, event_type: str, data: Dict) -> Dict:
        """
        执行风控控制，根据事件类型和数据执行相应的风控措施
        """
        try:
            result = {
                "action_taken": "none",
                "message": "No risk controls triggered",
                "risk_level": "normal"
            }
            
            if event_type == "ORDER_SUBMISSION":
                # 检查订单是否符合风控规则
                order_validation = await self.validate_order(data['order'])
                if not order_validation['valid']:
                    result["action_taken"] = "BLOCK_ORDER"
                    result["message"] = order_validation['message']
                    result["risk_level"] = "high"
                    return result
            
            elif event_type == "ACCOUNT_CHECK":
                # 检查账户风险限制
                account_check = await self.check_account_risk_limits(data['account_id'])
                if not account_check['is_valid']:
                    result["action_taken"] = "ACCOUNT_RESTRICTION"
                    result["message"] = f"Risk violations found: {[v['message'] for v in account_check['violations']]}"
                    result["violations"] = account_check['violations']
                    result["risk_level"] = "high"
                    return result
            
            elif event_type == "POSITION_CHECK":
                # 检查持仓风险
                # 实现持仓风险检查逻辑
                position = data['position']
                global_rules = await risk_rule_service.get_global_risk_rules()
                
                for rule in global_rules:
                    if rule.max_position_size:
                        position_value = float(position.volume) * float(position.avg_price) if position.avg_price else 0
                        if position_value > float(rule.max_position_size):
                            result["action_taken"] = "POSITION_LIMIT_EXCEEDED"
                            result["message"] = f"Position value {position_value} exceeds max allowed {rule.max_position_size}"
                            result["risk_level"] = "high"
                            return result
            
            return result
        except Exception as e:
            logger.error(f"Error enforcing risk controls for {event_type}: {str(e)}")
            raise CustomException(f"Failed to enforce risk controls: {str(e)}", 500)

# Global risk validator instance
risk_validator = RiskValidator()