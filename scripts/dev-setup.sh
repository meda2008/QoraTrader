#!/bin/bash

# QoraTrader 开发环境启动脚本
# 用途：一键启动开发环境，包含热重载功能

set -e  # 遌溉遇到错误时退出

echo "启动 QoraTrader 开发环境..."

# 检查 Docker 是否安装
if ! [ -x "$(command -v docker)" ]; then
  echo "错误: Docker 未安装，请先安装 Docker" >&2
  exit 1
fi

# 检查 Docker Compose 是否安装
if ! [ -x "$(command -v docker-compose)" ]; then
  echo "错误: Docker Compose 未安装，请先安装 Docker Compose" >&2
  exit 1
fi

# 获取当前脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 设置环境变量文件
ENV_FILE="${SCRIPT_DIR}/../.env"

if [ ! -f "$ENV_FILE" ]; then
  echo "警告: $ENV_FILE 不存在，创建开发环境示例文件"
  cat > "$ENV_FILE" << EOF
# QoraTrader 开发环境配置
DATABASE_URL=postgresql://user:password@db:5432/qora_trader
TIMESCALEDB_URL=postgresql://user:password@timescale:5432/qora_trader
REDIS_URL=redis://redis:6379
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MINI_QMT_PATH=/path/to/mini/qmt
LOG_LEVEL=DEBUG
MAX_STRATEGIES=20
MAX_ORDER_RATE=100
EOF
  echo "已创建 $ENV_FILE，请根据实际环境修改配置"
fi

# 使用开发环境的 Docker Compose 文件
DEV_COMPOSE_FILE="${SCRIPT_DIR}/../docker/docker-compose.dev.yml"

if [ ! -f "$DEV_COMPOSE_FILE" ]; then
  echo "创建开发环境 Docker Compose 文件..."
  cat > "$DEV_COMPOSE_FILE" << EOF
version: '3.8'

services:
  backend:
    build:
      context: ../backend
      dockerfile: ../docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/qora_trader
      - TIMESCALEDB_URL=postgresql://user:password@timescale:5432/qora_trader
      - LOG_LEVEL=DEBUG
    depends_on:
      - db
      - timescale
    volumes:
      - ../backend:/app  # 挂载源代码以支持热重载
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload  # 开启热重载
    networks:
      - qora_network

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/frontend.Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ../frontend:/app  # 挂载源代码以支持热重载
    command: npm run dev  # 使用开发模式
    networks:
      - qora_network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=qora_trader
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql  # 数据库初始化脚本
    networks:
      - qora_network

  timescale:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=qora_trader
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    ports:
      - "5433:5432"
    volumes:
      - timescale_data_dev:/var/lib/postgresql/data
    networks:
      - qora_network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    networks:
      - qora_network

volumes:
  postgres_data_dev:
  timescale_data_dev:
  redis_data:

networks:
  qora_network:
    driver: bridge
EOF
  echo "已创建 $DEV_COMPOSE_FILE"
fi

# 启动开发环境
echo "启动 QoraTrader 开发环境..."
cd "${SCRIPT_DIR}/../docker"
docker-compose -f docker-compose.dev.yml up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 15

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose.dev.yml ps

echo "QoraTrader 开发环境启动完成！"
echo "API 服务将在 http://localhost:8000 可用（已启用热重载）"
echo "前端应用将在 http://localhost:3000 可用（已启用热重载）"
echo "代码更改将自动重新加载服务"