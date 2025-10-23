from typing import Dict, List, Optional
from datetime import datetime
import logging
from src.models.base import RiskParams, Strategy
from src.database import get_db
from src.utils.error_handler import CustomException

logger = logging.getLogger(__name__)

class RiskRuleService:
    """
    风控规则管理服务
    """
    
    def __init__(self):
        logger.info("Risk rule service initialized")
    
    async def create_risk_rule(self, rule_data: Dict) -> RiskParams:
        """
        创建风控规则
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 验证输入数据
            required_fields = ['max_position_size', 'max_order_size', 'max_daily_loss', 'max_drawdown']
            for field in required_fields:
                if field not in rule_data:
                    raise CustomException(f"Missing required field: {field}", 400)
            
            # 如果指定了strategy_id，验证策略存在
            strategy_id = rule_data.get('strategy_id')
            if strategy_id:
                strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
                if not strategy:
                    raise CustomException(f"Strategy with ID {strategy_id} not found", 404)
            
            # 创建风控参数对象
            risk_rule = RiskParams(
                strategy_id=strategy_id,
                max_position_size=rule_data['max_position_size'],
                max_order_size=rule_data['max_order_size'],
                max_daily_loss=rule_data['max_daily_loss'],
                max_drawdown=rule_data['max_drawdown'],
                position_limit_per_symbol=rule_data.get('position_limit_per_symbol'),
                daily_order_limit=rule_data.get('daily_order_limit'),
                order_frequency_limit=rule_data.get('order_frequency_limit'),
                risk_level=rule_data.get('risk_level'),
                is_active=rule_data.get('is_active', True)
            )
            
            # 保存到数据库
            db.add(risk_rule)
            db.commit()
            db.refresh(risk_rule)
            
            logger.info(f"Risk rule created with ID: {risk_rule.id}")
            return risk_rule
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating risk rule: {str(e)}")
            raise CustomException(f"Failed to create risk rule: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_risk_rule(self, rule_id: str) -> Optional[RiskParams]:
        """
        获取风控规则
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            rule = db.query(RiskParams).filter(RiskParams.id == rule_id).first()
            if not rule:
                raise CustomException(f"Risk rule with ID {rule_id} not found", 404)
            
            return rule
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving risk rule {rule_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve risk rule: {str(e)}", 500)
        finally:
            db.close()
    
    async def update_risk_rule(self, rule_id: str, update_data: Dict) -> Optional[RiskParams]:
        """
        更新风控规则
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            rule = db.query(RiskParams).filter(RiskParams.id == rule_id).first()
            if not rule:
                raise CustomException(f"Risk rule with ID {rule_id} not found", 404)
            
            # 更新可更新的字段
            updatable_fields = [
                'max_position_size', 'max_order_size', 'max_daily_loss', 'max_drawdown',
                'position_limit_per_symbol', 'daily_order_limit', 'order_frequency_limit',
                'risk_level', 'is_active'
            ]
            
            for field, value in update_data.items():
                if field in updatable_fields:
                    setattr(rule, field, value)
            
            db.commit()
            db.refresh(rule)
            
            logger.info(f"Risk rule {rule_id} updated")
            return rule
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating risk rule {rule_id}: {str(e)}")
            raise CustomException(f"Failed to update risk rule: {str(e)}", 500)
        finally:
            db.close()
    
    async def delete_risk_rule(self, rule_id: str) -> bool:
        """
        删除风控规则
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            rule = db.query(RiskParams).filter(RiskParams.id == rule_id).first()
            if not rule:
                raise CustomException(f"Risk rule with ID {rule_id} not found", 404)
            
            db.delete(rule)
            db.commit()
            
            logger.info(f"Risk rule {rule_id} deleted")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error deleting risk rule {rule_id}: {str(e)}")
            raise CustomException(f"Failed to delete risk rule: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_risk_rules_by_strategy(self, strategy_id: str) -> List[RiskParams]:
        """
        获取策略的风控规则
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            rules = db.query(RiskParams).filter(
                RiskParams.strategy_id == strategy_id
            ).all()
            
            return rules
        except Exception as e:
            logger.error(f"Error retrieving risk rules for strategy {strategy_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve risk rules: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_global_risk_rules(self) -> List[RiskParams]:
        """
        获取全局风控规则
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            rules = db.query(RiskParams).filter(RiskParams.strategy_id.is_(None)).all()
            
            return rules
        except Exception as e:
            logger.error(f"Error retrieving global risk rules: {str(e)}")
            raise CustomException(f"Failed to retrieve global risk rules: {str(e)}", 500)
        finally:
            db.close()
    
    async def validate_order_against_risk_rules(self, strategy_id: str, order_data: Dict) -> Dict:
        """
        根据风控规则验证订单
        """
        try:
            from sqlalchemy.orm import Session
            db: Session = next(get_db())
            
            # 获取策略特定的风控规则
            strategy_rules = db.query(RiskParams).filter(
                RiskParams.strategy_id == strategy_id,
                RiskParams.is_active == True
            ).all()
            
            # 获取全局风控规则
            global_rules = db.query(RiskParams).filter(
                RiskParams.strategy_id.is_(None),
                RiskParams.is_active == True
            ).all()
            
            # 合并规则（策略特定规则优先）
            all_rules = strategy_rules + global_rules
            if not all_rules:
                # 如果没有风控规则，订单有效
                return {"valid": True, "message": "Order passed risk validation"}
            
            # 检查订单是否符合风控规则
            order_value = order_data.get('price', 0) * order_data.get('quantity', 0)
            
            for rule in all_rules:
                # 检查订单大小限制
                if rule.max_order_size and order_value > rule.max_order_size:
                    return {
                        "valid": False,
                        "message": f"Order value ({order_value}) exceeds maximum allowed ({rule.max_order_size})",
                        "rule_violated": "max_order_size"
                    }
                
                # 检查下单频率（如果需要）
                # 这里需要查询最近的订单来计算频率，为简化我们跳过这一步
                # if rule.order_frequency_limit and ...:
                
                # 可以添加更多风控检查...
            
            return {"valid": True, "message": "Order passed risk validation"}
        except Exception as e:
            logger.error(f"Error validating order against risk rules: {str(e)}")
            raise CustomException(f"Failed to validate order against risk rules: {str(e)}", 500)
        finally:
            db.close()

# Global risk rule service instance
risk_rule_service = RiskRuleService()