# Quickstart Guide: 量化交易系统

## 环境要求

- Docker 20.10+
- Docker Compose v2+
- Python 3.11+
- Node.js 16+ (可选，用于前端开发)

## 快速部署

### 1. 克隆仓库
```bash
git clone <repository-url>
cd QoraTrader
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件以配置数据库连接、交易所API密钥等
```

### 3. 启动服务
```bash
# 使用Docker Compose一键启动所有服务
docker-compose up -d

# 或使用便捷脚本（如果提供）
./scripts/deploy.sh
```

### 4. 验证部署
```bash
# 检查所有服务状态
docker-compose ps

# 访问Web界面
open http://localhost:8080

# 检查API健康状态
curl http://localhost:8000/health
```

## 本地开发环境设置

### 1. 安装依赖
```bash
# 后端
pip install -r requirements.txt

# 前端（如果适用）
cd frontend && npm install
```

### 2. 启动开发环境
```bash
# 启动后端服务
python -m backend.main

# 在另一个终端中启动前端（如果适用）
cd frontend && npm run dev
```

### 3. 运行测试
```bash
# 运行后端测试
pytest

# 运行前端测试（如果适用）
cd frontend && npm run test
```

## 核心功能演示

### 1. 创建并运行策略

1. 登录Web界面
2. 导航到"策略管理"页面
3. 点击"新建策略"，上传您的策略文件
4. 配置策略参数
5. 点击"激活"启动策略

### 2. 执行回测

1. 在"策略管理"页面选择一个策略
2. 点击"回测"按钮
3. 设置回测参数（时间范围、初始资金等）
4. 启动回测并查看结果报告

### 3. 监控实时交易

1. 访问"实时监控"页面
2. 查看活跃策略的状态和表现
3. 监控订单执行和持仓变化

## API访问示例

### 获取所有策略
```bash
curl -H "Authorization: Bearer <your-token>" \
     http://localhost:8000/api/v1/strategies
```

### 创建新订单
```bash
curl -X POST \
     -H "Authorization: Bearer <your-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "strategyId": "your-strategy-id",
       "accountId": "your-account-id",
       "symbol": "000001",
       "direction": "买入",
       "orderType": "限价单",
       "price": 10.5,
       "quantity": 1000
     }' \
     http://localhost:8000/api/v1/orders
```

## 故障排除

### 服务未启动
- 检查日志：`docker-compose logs`
- 确认端口未被占用
- 验证环境变量配置

### 策略无法激活
- 确认策略文件格式正确
- 检查策略代码语法
- 验证依赖项是否安装

### API访问失败
- 确认认证令牌有效
- 检查网络连接
- 验证API端点URL

## 进一步定制

- 配置额外的交易所连接
- 添加自定义指标库
- 调整风控参数
- 集成其他数据源