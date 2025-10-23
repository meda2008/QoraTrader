from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.security import get_current_active_user, require_role
from src.services.user_service import user_service
from src.models.base import User

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_users(
    current_user = Depends(require_role("admin"))
):
    """
    获取所有用户（仅管理员）
    """
    try:
        users = await user_service.get_all_users()
        
        users_list = []
        for user in users:
            user_dict = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            users_list.append(user_dict)
        
        return users_list
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    获取特定用户信息（仅管理员）
    """
    try:
        user = await user_service.get_user(user_id)
        
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
        
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.post("/", response_model=dict)
async def create_user(
    user_data: dict,
    current_user = Depends(require_role("admin"))
):
    """
    创建新用户（仅管理员）
    """
    try:
        created_user = await user_service.create_user(user_data)
        
        user_dict = {
            "id": created_user.id,
            "username": created_user.username,
            "email": created_user.email,
            "role": created_user.role,
            "is_active": created_user.is_active,
            "created_at": created_user.created_at.isoformat() if created_user.created_at else None
        }
        
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: str,
    update_data: dict,
    current_user = Depends(require_role("admin"))
):
    """
    更新用户信息（仅管理员）
    """
    try:
        updated_user = await user_service.update_user(user_id, update_data)
        
        user_dict = {
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "role": updated_user.role,
            "is_active": updated_user.is_active,
            "created_at": updated_user.created_at.isoformat() if updated_user.created_at else None,
            "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
        }
        
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    删除用户（仅管理员）
    """
    try:
        success = await user_service.delete_user(user_id)
        if success:
            return {"message": f"User {user_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.patch("/{user_id}/role", response_model=dict)
async def change_user_role(
    user_id: str,
    role_data: dict,
    current_user = Depends(require_role("admin"))
):
    """
    更改用户角色（仅管理员）
    """
    try:
        if "role" not in role_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role field is required"
            )
        
        updated_user = await user_service.change_user_role(user_id, role_data["role"])
        
        user_dict = {
            "id": updated_user.id,
            "username": updated_user.username,
            "email": updated_user.email,
            "role": updated_user.role,
            "is_active": updated_user.is_active
        }
        
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change user role: {str(e)}"
        )

@router.patch("/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    激活用户账户（仅管理员）
    """
    try:
        updated_user = await user_service.update_user(user_id, {"is_active": True})
        return {"message": f"User {user_id} activated successfully", "user": updated_user.username}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )

@router.patch("/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user = Depends(require_role("admin"))
):
    """
    停用用户账户（仅管理员）
    """
    try:
        updated_user = await user_service.update_user(user_id, {"is_active": False})
        return {"message": f"User {user_id} deactivated successfully", "user": updated_user.username}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )