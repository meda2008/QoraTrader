from typing import Dict, List, Optional
import logging
from src.models.base import User
from src.database import get_db
from src.auth.security import get_password_hash
from src.utils.error_handler import CustomException
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class UserService:
    """
    用户管理服务，用于管理用户账户和角色
    """
    
    def __init__(self):
        logger.info("User service initialized")
    
    async def create_user(self, user_data: Dict) -> User:
        """
        创建新用户
        """
        try:
            db: Session = next(get_db())
            
            # 验证必需字段
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in user_data:
                    raise CustomException(f"Missing required field: {field}", 400)
            
            # 检查用户名和邮箱是否已存在
            existing_user = db.query(User).filter(
                (User.username == user_data['username']) | (User.email == user_data['email'])
            ).first()
            
            if existing_user:
                raise CustomException("Username or email already exists", 400)
            
            # 创建新用户
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data.get('role', 'trader'),  # 默认为交易员角色
                password_hash=get_password_hash(user_data['password']),
                is_active=user_data.get('is_active', True)
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User {user.username} created with ID: {user.id}")
            return user
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating user {user_data.get('username', 'unknown')}: {str(e)}")
            raise CustomException(f"Failed to create user: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        获取用户信息
        """
        try:
            db: Session = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(f"User with ID {user_id} not found", 404)
            
            return user
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            raise CustomException(f"Failed to retrieve user: {str(e)}", 500)
        finally:
            db.close()
    
    async def update_user(self, user_id: str, update_data: Dict) -> Optional[User]:
        """
        更新用户信息
        """
        try:
            db: Session = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(f"User with ID {user_id} not found", 404)
            
            # 更新可更新的字段
            updatable_fields = ['username', 'email', 'role', 'is_active']
            
            for field, value in update_data.items():
                if field in updatable_fields:
                    if field == 'password':
                        value = get_password_hash(value)
                    setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"User {user.id} updated")
            return user
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise CustomException(f"Failed to update user: {str(e)}", 500)
        finally:
            db.close()
    
    async def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        """
        try:
            db: Session = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(f"User with ID {user_id} not found", 404)
            
            db.delete(user)
            db.commit()
            
            logger.info(f"User {user_id} deleted")
            return True
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise CustomException(f"Failed to delete user: {str(e)}", 500)
        finally:
            db.close()
    
    async def get_all_users(self) -> List[User]:
        """
        获取所有用户
        """
        try:
            db: Session = next(get_db())
            
            users = db.query(User).all()
            return users
        except Exception as e:
            logger.error(f"Error retrieving users: {str(e)}")
            raise CustomException(f"Failed to retrieve users: {str(e)}", 500)
        finally:
            db.close()
    
    async def change_user_role(self, user_id: str, new_role: str) -> Optional[User]:
        """
        更改用户角色
        """
        try:
            valid_roles = ['admin', 'strategist', 'trader']
            if new_role not in valid_roles:
                raise CustomException(f"Invalid role: {new_role}. Valid roles are: {valid_roles}", 400)
            
            db: Session = next(get_db())
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(f"User with ID {user_id} not found", 404)
            
            old_role = user.role
            user.role = new_role
            db.commit()
            db.refresh(user)
            
            logger.info(f"User {user_id} role changed from {old_role} to {new_role}")
            return user
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error changing role for user {user_id}: {str(e)}")
            raise CustomException(f"Failed to change user role: {str(e)}", 500)
        finally:
            db.close()

# Global user service instance
user_service = UserService()