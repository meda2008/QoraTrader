from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from src.config.settings import settings
from src.models.base import User
from sqlalchemy.orm import Session
from src.database import get_db

security = HTTPBearer()

def verify_token(token: str) -> dict:
    """
    验证JWT令牌
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(request: Request) -> User:
    """
    获取当前认证用户
    """
    credentials: HTTPAuthorizationCredentials = await security(request)
    token = credentials.credentials
    
    payload = verify_token(token)
    user_id = payload.get("user_id")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: no user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    db: Session = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    finally:
        db.close()

async def require_role(required_role: str):
    """
    角色权限装饰器
    """
    async def role_checker(request: Request):
        current_user = await get_current_user(request)
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

async def require_any_role(*required_roles):
    """
    多角色权限装饰器
    """
    async def role_checker(request: Request):
        current_user = await get_current_user(request)
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker