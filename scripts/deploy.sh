#!/bin/bash

# QoraTrader 部署脚本
# 用途：一键部署QoraTrader量化交易系统

set -e  # 遌溉遇到错误时退出

echo "开始部署 QoraTrader 系统..."

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
  echo "警告: $ENV_FILE 不存在，创建示例环境文件"
  cat > "$ENV_FILE" << EOF
# QoraTrader 环境配置
DATABASE_URL=postgresql://user:password@db:5432/qora_trader
TIMESCALEDB_URL=postgresql://user:password@timescale:5432/qora_trader
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MINI_QMT_PATH=/path/to/mini/qmt
LOG_LEVEL=INFO
MAX_STRATEGIES=20
MAX_ORDER_RATE=100
EOF
  echo "已创建 $ENV_FILE，请根据实际环境修改配置"
fi

# 构建并启动服务
echo "构建并启动 QoraTrader 服务..."
cd "${SCRIPT_DIR}/../docker"
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose ps

# 运行数据库迁移（如果有的话）
echo "执行数据库初始化..."
# docker-compose exec backend python manage.py migrate  # 根据实际使用的迁移工具调整

echo "QoraTrader 系统部署完成！"
echo "API 服务将在 http://localhost:8000 可用"
echo "前端应用将在 http://localhost:3000 可用"
echo "数据库将在 localhost:5432 可用"
echo "TimescaleDB 将在 localhost:5433 可用"