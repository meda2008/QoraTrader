from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.services.risk_rule_service import risk_rule_service
from src.models.base import RiskParams

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_risk_rules(
    current_user = Depends(require_role("admin"))
):
    """
    获取所有风控规则（仅管理员）
    """
    try:
        # 从数据库查询所有风控规则
        from sqlalchemy.orm import Session
        db: Session = next(get_db())
        
        try:
            rules = db.query(RiskParams).all()
            
            # 转换为字典格式
            rules_list = []
            for rule in rules:
                rule_dict = {
                    "id": rule.id,
                    "strategy_id": rule.strategy_id,
                    "max_position_size": float(rule.max_position_size) if rule.max_position_size else None,
                    "max_order_size": float(rule.max_order_size) if rule.max_order_size else None,
                    "max_daily_loss": float(rule.max_daily_loss) if rule.max_daily_loss else None,
                    "max_drawdown": float(rule.max_drawdown) if rule.max_drawdown else None,
                    "position_limit_per_symbol": float(rule.position_limit_per_symbol) if rule.position_limit_per_symbol else None,
                    "daily_order_limit": rule.daily_order_limit,
                    "order_frequency_limit": rule.order_frequency_limit,
                    "risk_level": rule.risk_level.value if rule.risk_level else None,
                    "is_active": rule.is_active,
                    "created_at": rule.created_at.isoformat() if rule.created_at else None,
                    "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
                }
                rules_list.append(rule_dict)
            
            return rules_list
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk rules: {str(e)}"
        )

@router.get("/{rule_id}", response_model=dict)
async def get_risk_rule(
    rule_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    获取特定风控规则（仅管理员）
    """
    try:
        rule = await risk_rule_service.get_risk_rule(rule_id)
        
        rule_dict = {
            "id": rule.id,
            "strategy_id": rule.strategy_id,
            "max_position_size": float(rule.max_position_size) if rule.max_position_size else None,
            "max_order_size": float(rule.max_order_size) if rule.max_order_size else None,
            "max_daily_loss": float(rule.max_daily_loss) if rule.max_daily_loss else None,
            "max_drawdown": float(rule.max_drawdown) if rule.max_drawdown else None,
            "position_limit_per_symbol": float(rule.position_limit_per_symbol) if rule.position_limit_per_symbol else None,
            "daily_order_limit": rule.daily_order_limit,
            "order_frequency_limit": rule.order_frequency_limit,
            "risk_level": rule.risk_level.value if rule.risk_level else None,
            "is_active": rule.is_active,
            "created_at": rule.created_at.isoformat() if rule.created_at else None,
            "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
        }
        
        return rule_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk rule: {str(e)}"
        )

@router.post("/", response_model=dict)
async def create_risk_rule(
    rule_data: dict,
    current_user = Depends(require_role("admin"))
):
    """
    创建风控规则（仅管理员）
    """
    try:
        created_rule = await risk_rule_service.create_risk_rule(rule_data)
        
        rule_dict = {
            "id": created_rule.id,
            "strategy_id": created_rule.strategy_id,
            "max_position_size": float(created_rule.max_position_size) if created_rule.max_position_size else None,
            "max_order_size": float(created_rule.max_order_size) if created_rule.max_order_size else None,
            "max_daily_loss": float(created_rule.max_daily_loss) if created_rule.max_daily_loss else None,
            "max_drawdown": float(created_rule.max_drawdown) if created_rule.max_drawdown else None,
            "position_limit_per_symbol": float(created_rule.position_limit_per_symbol) if created_rule.position_limit_per_symbol else None,
            "daily_order_limit": created_rule.daily_order_limit,
            "order_frequency_limit": created_rule.order_frequency_limit,
            "risk_level": created_rule.risk_level.value if created_rule.risk_level else None,
            "is_active": created_rule.is_active,
            "created_at": created_rule.created_at.isoformat() if created_rule.created_at else None,
            "updated_at": created_rule.updated_at.isoformat() if created_rule.updated_at else None
        }
        
        return rule_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create risk rule: {str(e)}"
        )

@router.put("/{rule_id}", response_model=dict)
async def update_risk_rule(
    rule_id: str,
    update_data: dict,
    current_user = Depends(require_role("admin"))
):
    """
    更新风控规则（仅管理员）
    """
    try:
        updated_rule = await risk_rule_service.update_risk_rule(rule_id, update_data)
        
        rule_dict = {
            "id": updated_rule.id,
            "strategy_id": updated_rule.strategy_id,
            "max_position_size": float(updated_rule.max_position_size) if updated_rule.max_position_size else None,
            "max_order_size": float(updated_rule.max_order_size) if updated_rule.max_order_size else None,
            "max_daily_loss": float(updated_rule.max_daily_loss) if updated_rule.max_daily_loss else None,
            "max_drawdown": float(updated_rule.max_drawdown) if updated_rule.max_drawdown else None,
            "position_limit_per_symbol": float(updated_rule.position_limit_per_symbol) if updated_rule.position_limit_per_symbol else None,
            "daily_order_limit": updated_rule.daily_order_limit,
            "order_frequency_limit": updated_rule.order_frequency_limit,
            "risk_level": updated_rule.risk_level.value if updated_rule.risk_level else None,
            "is_active": updated_rule.is_active,
            "created_at": updated_rule.created_at.isoformat() if updated_rule.created_at else None,
            "updated_at": updated_rule.updated_at.isoformat() if updated_rule.updated_at else None
        }
        
        return rule_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update risk rule: {str(e)}"
        )

@router.delete("/{rule_id}")
async def delete_risk_rule(
    rule_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    删除风控规则（仅管理员）
    """
    try:
        success = await risk_rule_service.delete_risk_rule(rule_id)
        if success:
            return {"message": f"Risk rule {rule_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Risk rule {rule_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete risk rule: {str(e)}"
        )

@router.get("/strategy/{strategy_id}", response_model=List[dict])
async def get_risk_rules_by_strategy(
    strategy_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    获取策略的风控规则（仅管理员）
    """
    try:
        rules = await risk_rule_service.get_risk_rules_by_strategy(strategy_id)
        
        rules_list = []
        for rule in rules:
            rule_dict = {
                "id": rule.id,
                "strategy_id": rule.strategy_id,
                "max_position_size": float(rule.max_position_size) if rule.max_position_size else None,
                "max_order_size": float(rule.max_order_size) if rule.max_order_size else None,
                "max_daily_loss": float(rule.max_daily_loss) if rule.max_daily_loss else None,
                "max_drawdown": float(rule.max_drawdown) if rule.max_drawdown else None,
                "position_limit_per_symbol": float(rule.position_limit_per_symbol) if rule.position_limit_per_symbol else None,
                "daily_order_limit": rule.daily_order_limit,
                "order_frequency_limit": rule.order_frequency_limit,
                "risk_level": rule.risk_level.value if rule.risk_level else None,
                "is_active": rule.is_active,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None
            }
            rules_list.append(rule_dict)
        
        return rules_list
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get risk rules for strategy: {str(e)}"
        )