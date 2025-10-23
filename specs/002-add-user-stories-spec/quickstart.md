# Quickstart Guide: 量化交易系统

## 项目概述
本项目是一个支持策略回测、实盘交易和风险管理的量化交易平台。系统采用微服务架构，使用Python/FastAPI构建后端服务，React构建前端界面。

## 环境要求
- Docker 20.10+
- Docker Compose v2+
- Python 3.11+
- Node.js 18+ (用于前端构建)

## 本地开发环境搭建

### 1. 克隆项目
```bash
git clone <repository-url>
cd QoraTrader
```

### 2. 启动开发环境
```bash
# 启动所有服务
docker-compose -f docker/docker-compose.yml up -d

# 或者只启动后端服务进行开发
docker-compose -f docker/docker-compose.yml up backend
```

### 3. 初始化数据库
```bash
# 等待数据库服务启动后运行迁移
docker exec -it qoratrader-backend-1 python -m db.migrate
```

## 项目结构说明
```
QoraTrader/
├── backend/                 # 后端服务 (Python/FastAPI)
│   ├── src/
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑服务
│   │   ├── api/            # API端点
│   │   ├── strategies/     # 策略引擎
│   │   └── risk/           # 风控模块
│   └── tests/
├── frontend/                # 前端应用 (React/TypeScript)
│   ├── src/
│   │   ├── components/     # UI组件
│   │   ├── pages/          # 页面组件
│   │   └── services/       # API服务
│   └── tests/
├── db/                      # 数据库相关
│   ├── migrations/         # 数据库迁移脚本
│   └── schemas/            # 数据库模式
├── docker/                  # Docker配置
└── contracts/               # API契约定义
```

## 核心功能开发指南

### 1. 创建新策略
1. 在 `backend/src/strategies/` 目录下创建新策略文件
2. 继承基类 `BaseStrategy` 并实现必要方法
3. 定义策略参数和逻辑

```python
from src.strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.param1 = kwargs.get('param1', 10)
        
    def on_bar(self, symbol: str, bar_data):
        # 实现策略逻辑
        pass
```

### 2. 添加新API端点
1. 在 `backend/src/api/` 目录下创建新路由文件
2. 使用FastAPI定义端点

```python
from fastapi import APIRouter, Depends
from src.dependencies import get_strategy_service

router = APIRouter()

@router.get("/strategies/{strategy_id}")
async def get_strategy(strategy_id: str, service = Depends(get_strategy_service)):
    return await service.get_strategy(strategy_id)
```

### 3. 数据模型变更
1. 在 `backend/src/models/` 修改模型定义
2. 使用Alembic生成迁移文件
3. 更新 `db/schemas/` 中的数据库模式定义

## 测试指南

### 后端测试
```bash
# 运行所有测试
cd backend
python -m pytest tests/

# 运行单元测试
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 运行契约测试
python -m pytest tests/contract/
```

### 前端测试
```bash
# 运行前端测试
cd frontend
npm test
```

## 部署说明

### 本地部署
```bash
# 构建并启动所有服务
docker-compose -f docker/docker-compose.yml up --build -d

# 检查服务状态
docker-compose -f docker/docker-compose.yml ps
```

### 生产部署
1. 配置环境变量文件 `.env.production`
2. 更新 `docker-compose.prod.yml` 中的配置
3. 部署到服务器

```bash
# 生产环境部署
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 调试技巧

### 后端调试
- 查看服务日志: `docker logs qoratrader-backend-1`
- 进入容器: `docker exec -it qoratrader-backend-1 bash`
- 使用日志级别: 设置 `LOG_LEVEL=DEBUG`

### 前端调试
- 开发模式: `npm start` (启用热重载)
- 生产构建: `npm run build`
- 检查网络请求: 浏览器开发者工具的网络面板

## 重要配置

### 环境变量
在 `.env` 文件中配置:
```
# 数据库配置
DB_HOST=postgres
DB_PORT=5432
DB_NAME=qoratrader
DB_USER=qoratrader_user
DB_PASSWORD=qoratrader_pass

# 交易所API配置
EXCHANGE_API_KEY=your_api_key
EXCHANGE_API_SECRET=your_api_secret

# 风控配置
RISK_MAX_POSITION_SIZE=100000
RISK_MAX_DAILY_LOSS=5000
```

### 性能调优
- 核心交易路径延迟: <1ms P99
- 订单处理吞吐量: >1000 订单/秒
- UI响应时间: <2秒加载时间