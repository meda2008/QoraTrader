import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db
from src.models.base import Base
from src.schemas.report import ReportCreate

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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

def test_report_generation_integration(db_session):
    """
    Integration test for report generation functionality
    """
    # 首先创建一个用户
    user_data = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password",
        "role": "trader"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    user_id = user["id"]
    
    # 创建一个策略
    strategy_data = {
        "name": "Test Strategy",
        "description": "A test strategy for integration testing",
        "user_id": user_id
    }
    response = client.post("/api/v1/strategies/", json=strategy_data)
    assert response.status_code == 200
    strategy = response.json()
    strategy_id = strategy["id"]
    
    # 执行报告生成
    report_data = {
        "strategy_id": strategy_id,
        "report_type": "performance",
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T23:59:59"
    }
    response = client.post("/api/v1/reports/", json=report_data)
    assert response.status_code == 200
    
    report = response.json()
    assert report["strategy_id"] == strategy_id
    assert report["report_type"] == "performance"
    
    # 获取报告列表
    response = client.get("/api/v1/reports/")
    assert response.status_code == 200
    reports = response.json()
    assert len(reports) >= 1
    
    # 获取特定报告
    report_id = report["id"]
    response = client.get(f"/api/v1/reports/{report_id}")
    assert response.status_code == 200
    retrieved_report = response.json()
    assert retrieved_report["id"] == report_id

def test_trade_report_generation(db_session):
    """
    Integration test for trade report generation
    """
    # 创建用户
    user_data = {
        "username": "test_trader",
        "email": "trader@example.com",
        "password": "secure_password",
        "role": "trader"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    user_id = user["id"]
    
    # 创建策略
    strategy_data = {
        "name": "Trade Strategy",
        "description": "A strategy to test trade reports",
        "user_id": user_id
    }
    response = client.post("/api/v1/strategies/", json=strategy_data)
    assert response.status_code == 200
    strategy = response.json()
    strategy_id = strategy["id"]
    
    # 生成交易报告
    report_data = {
        "strategy_id": strategy_id,
        "report_type": "trade",
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T23:59:59"
    }
    response = client.post("/api/v1/reports/", json=report_data)
    assert response.status_code == 200
    
    report = response.json()
    assert report["strategy_id"] == strategy_id
    assert report["report_type"] == "trade"
    assert "trades" in report or report.get("metrics")

def test_risk_report_generation(db_session):
    """
    Integration test for risk report generation
    """
    # 创建用户
    user_data = {
        "username": "risk_manager",
        "email": "risk@example.com",
        "password": "secure_password",
        "role": "admin"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    user_id = user["id"]
    
    # 创建策略
    strategy_data = {
        "name": "Risk Strategy",
        "description": "A strategy to test risk reports",
        "user_id": user_id
    }
    response = client.post("/api/v1/strategies/", json=strategy_data)
    assert response.status_code == 200
    strategy = response.json()
    strategy_id = strategy["id"]
    
    # 生成风险报告
    report_data = {
        "strategy_id": strategy_id,
        "report_type": "risk",
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T23:59:59"
    }
    response = client.post("/api/v1/reports/", json=report_data)
    assert response.status_code == 200
    
    report = response.json()
    assert report["strategy_id"] == strategy_id
    assert report["report_type"] == "risk"
    assert "risk_metrics" in report or report.get("metrics")

def test_pnl_report_generation(db_session):
    """
    Integration test for PnL report generation
    """
    # 创建用户
    user_data = {
        "username": "pnl_analyst",
        "email": "pnl@example.com",
        "password": "secure_password",
        "role": "strategist"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
    user = response.json()
    user_id = user["id"]
    
    # 创建策略
    strategy_data = {
        "name": "PnL Strategy",
        "description": "A strategy to test PnL reports",
        "user_id": user_id
    }
    response = client.post("/api/v1/strategies/", json=strategy_data)
    assert response.status_code == 200
    strategy = response.json()
    strategy_id = strategy["id"]
    
    # 生成PnL报告
    report_data = {
        "strategy_id": strategy_id,
        "report_type": "pnl",
        "start_date": "2023-01-01T00:00:00",
        "end_date": "2023-12-31T23:59:59"
    }
    response = client.post("/api/v1/reports/", json=report_data)
    assert response.status_code == 200
    
    report = response.json()
    assert report["strategy_id"] == strategy_id
    assert report["report_type"] == "pnl"
    assert "pnl_data" in report or report.get("metrics")