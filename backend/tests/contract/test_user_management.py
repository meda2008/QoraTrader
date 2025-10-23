import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db
from src.models.base import Base

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_user_management.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 重写依赖项以使用测试数据库
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 创建测试客户端
client = TestClient(app)

# 创建测试数据
@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)

def test_user_creation_contract(db_session):
    """
    Contract test for user creation endpoint
    """
    # 测试创建用户的基本功能
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
        "role": "trader"
    }
    
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    # 验证响应格式
    user = response.json()
    assert "id" in user
    assert user["username"] == user_data["username"]
    assert user["email"] == user_data["email"]
    assert user["role"] == user_data["role"]
    assert "created_at" in user
    assert "updated_at" in user
    assert user["is_active"] is True  # 默认应该是激活状态

def test_get_user_contract(db_session):
    """
    Contract test for getting a specific user
    """
    # 首先创建一个用户
    user_data = {
        "username": "getusertest",
        "email": "getuser@example.com",
        "password": "securepassword123",
        "role": "strategist"
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    assert create_response.status_code == 200
    created_user = create_response.json()
    user_id = created_user["id"]
    
    # 获取用户信息
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    
    # 验证响应格式
    user = response.json()
    assert user["id"] == user_id
    assert user["username"] == user_data["username"]
    assert user["email"] == user_data["email"]
    assert user["role"] == user_data["role"]
    assert "created_at" in user
    assert "updated_at" in user

def test_get_users_list_contract(db_session):
    """
    Contract test for getting users list
    """
    # 首先创建几个用户
    users_data = [
        {
            "username": "user1",
            "email": "user1@example.com",
            "password": "securepassword123",
            "role": "trader"
        },
        {
            "username": "user2",
            "email": "user2@example.com",
            "password": "securepassword123",
            "role": "admin"
        }
    ]
    
    for user_data in users_data:
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 200
    
    # 获取用户列表
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    
    # 验证响应格式
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 2
    
    # 检查每个用户都有必要的字段
    for user in users:
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "role" in user
        assert "is_active" in user
        assert "created_at" in user
        assert "updated_at" in user

def test_update_user_contract(db_session):
    """
    Contract test for updating a user
    """
    # 首先创建一个用户
    user_data = {
        "username": "updateusertest",
        "email": "updateuser@example.com",
        "password": "securepassword123",
        "role": "trader"
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    assert create_response.status_code == 200
    created_user = create_response.json()
    user_id = created_user["id"]
    
    # 更新用户信息
    update_data = {
        "email": "updated@example.com",
        "role": "admin",
        "is_active": False
    }
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    
    # 验证响应格式
    updated_user = response.json()
    assert updated_user["id"] == user_id
    assert updated_user["email"] == update_data["email"]
    assert updated_user["role"] == update_data["role"]
    assert updated_user["is_active"] == update_data["is_active"]

def test_delete_user_contract(db_session):
    """
    Contract test for deleting a user
    """
    # 首先创建一个用户
    user_data = {
        "username": "deleteusertest",
        "email": "deleteuser@example.com",
        "password": "securepassword123",
        "role": "trader"
    }
    create_response = client.post("/api/v1/users/", json=user_data)
    assert create_response.status_code == 200
    created_user = create_response.json()
    user_id = created_user["id"]
    
    # 删除用户
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    
    result = response.json()
    assert result["message"] == "User deleted successfully"

def test_user_auth_fields_not_exposed(db_session):
    """
    Contract test to ensure sensitive fields are not exposed
    """
    # 创建一个用户
    user_data = {
        "username": "secureusertest",
        "email": "secureuser@example.com",
        "password": "securepassword123",
        "role": "trader"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    
    user = response.json()
    # 验证敏感字段不被返回
    assert "password" not in user
    assert "password_hash" not in user