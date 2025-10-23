import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.main import app
from src.database import get_db
from src.models.user import User
from src.models.role import Role


# Mock database session
class MockDBSession:
    def __init__(self):
        self.add = AsyncMock()
        self.commit = AsyncMock()
        self.refresh = AsyncMock()
        self.get = AsyncMock()
        self.query = AsyncMock()


@pytest.fixture
def mock_db_session():
    return MockDBSession()


@pytest.fixture
def client(mock_db_session):
    def override_get_db():
        yield mock_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_user_integration(client, mock_db_session):
    """测试创建用户功能的集成测试"""
    # 准备测试数据
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "role": "策略师",
        "is_active": True
    }
    
    # 使用Mock来模拟数据库操作
    with patch('src.services.user_service.UserService.create_user') as mock_create_user:
        # 模拟返回的用户对象
        mock_user = User(
            id="test-uuid-123",
            username="test_user",
            email="test@example.com",
            role="策略师",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_create_user.return_value = mock_user

        # 发起请求
        response = client.post("/api/v1/users/", json=user_data)

        # 验证响应
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["username"] == "test_user"
        assert response_data["email"] == "test@example.com"
        assert response_data["role"] == "策略师"
        assert response_data["is_active"] is True

        # 验证服务层方法被调用
        mock_create_user.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_integration(client, mock_db_session):
    """测试获取用户信息的集成测试"""
    user_id = "test-uuid-123"
    
    with patch('src.services.user_service.UserService.get_user') as mock_get_user:
        # 模拟返回的用户对象
        mock_user = User(
            id=user_id,
            username="test_user",
            email="test@example.com",
            role="策略师",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_get_user.return_value = mock_user

        # 发起请求
        response = client.get(f"/api/v1/users/{user_id}")

        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == user_id
        assert response_data["username"] == "test_user"
        assert response_data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_update_user_integration(client, mock_db_session):
    """测试更新用户信息的集成测试"""
    user_id = "test-uuid-123"
    update_data = {
        "email": "updated@example.com",
        "role": "交易员",
        "is_active": False
    }
    
    with patch('src.services.user_service.UserService.update_user') as mock_update_user:
        # 模拟返回的用户对象
        updated_user = User(
            id=user_id,
            username="test_user",
            email="updated@example.com",
            role="交易员",
            is_active=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_update_user.return_value = updated_user

        # 发起请求
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)

        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == user_id
        assert response_data["email"] == "updated@example.com"
        assert response_data["role"] == "交易员"
        assert response_data["is_active"] is False

        # 验证服务层方法被调用
        mock_update_user.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_integration(client, mock_db_session):
    """测试删除用户的集成测试"""
    user_id = "test-uuid-123"
    
    with patch('src.services.user_service.UserService.delete_user') as mock_delete_user:
        mock_delete_user.return_value = True

        # 发起请求
        response = client.delete(f"/api/v1/users/{user_id}")

        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True

        # 验证服务层方法被调用
        mock_delete_user.assert_called_once()


@pytest.mark.asyncio
async def test_get_users_list_integration(client, mock_db_session):
    """测试获取用户列表的集成测试"""
    with patch('src.services.user_service.UserService.get_users_list') as mock_get_users:
        # 模拟返回的用户列表
        mock_users = [
            User(
                id="test-uuid-123",
                username="test_user1",
                email="user1@example.com",
                role="策略师",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            User(
                id="test-uuid-456",
                username="test_user2",
                email="user2@example.com",
                role="交易员",
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_get_users.return_value = mock_users

        # 发起请求
        response = client.get("/api/v1/users/")

        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        assert response_data[0]["username"] == "test_user1"
        assert response_data[1]["username"] == "test_user2"


@pytest.mark.asyncio
async def test_user_role_assignment_integration(client, mock_db_session):
    """测试用户角色分配的集成测试"""
    user_id = "test-uuid-123"
    role_update_data = {
        "role": "管理员"
    }
    
    with patch('src.services.user_service.UserService.update_user_role') as mock_update_role:
        # 模拟返回的用户对象
        updated_user = User(
            id=user_id,
            username="test_user",
            email="test@example.com",
            role="管理员",  # 角色已更新
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_update_role.return_value = updated_user

        # 发起请求
        response = client.patch(f"/api/v1/users/{user_id}/role", json=role_update_data)

        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["role"] == "管理员"

        # 验证服务层方法被调用
        mock_update_role.assert_called_once()


@pytest.mark.asyncio
async def test_user_activation_integration(client, mock_db_session):
    """测试用户激活/停用的集成测试"""
    user_id = "test-uuid-123"
    activation_data = {
        "is_active": False
    }
    
    with patch('src.services.user_service.UserService.update_user_activation') as mock_update_activation:
        # 模拟返回的用户对象
        updated_user = User(
            id=user_id,
            username="test_user",
            email="test@example.com",
            role="策略师",
            is_active=False,  # 用户已停用
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_update_activation.return_value = updated_user

        # 发起请求
        response = client.patch(f"/api/v1/users/{user_id}/activation", json=activation_data)

        # 验证响应
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["is_active"] is False

        # 验证服务层方法被调用
        mock_update_activation.assert_called_once()