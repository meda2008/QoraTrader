# 本地开发环境搭建指南

## 快速开始

本指南介绍如何快速搭建QoraTrader的本地开发环境。

### 前置条件

在开始之前，请确保安装了以下软件：

- Docker Engine 20.10或更高版本
- Docker Compose v2或更高版本
- Git
- Python 3.11或更高版本
- Node.js 18或更高版本

### 自动设置

运行以下命令自动设置开发环境：

```bash
# 设置开发环境
bash scripts/dev-setup.sh setup

# 启动开发环境
bash scripts/dev-setup.sh

# 重启服务
bash scripts/dev-setup.sh restart

# 停止开发环境
bash scripts/dev-setup.sh stop
```

### 手动设置

如果您想手动设置开发环境，请按照以下步骤：

1. 克隆代码库：
```bash
git clone <repository-url>
cd QoraTrader
```

2. 创建开发环境配置：
```bash
cp .env.development.example .env.development
```

3. 编辑 `.env.development` 文件，配置开发环境参数

4. 构建并启动服务：
```bash
docker-compose -f docker/docker-compose.dev.yml up -d --build
```

### 开发工作流

#### 后端开发

1. 代码位于 `backend/src/` 目录
2. 使用热重载模式，修改代码后自动重启
3. 服务运行在 `http://localhost:8000`

#### 前端开发

1. 代码位于 `frontend/src/` 目录
2. 使用React开发服务器，支持热重载
3. 服务运行在 `http://localhost:3000`

#### 策略开发

1. 策略代码位于 `backend/src/strategies/` 目录
2. 支持策略热重载，无需重启整个系统
3. 在开发环境中，策略文件修改会自动加载

### 数据库开发

开发环境使用PostgreSQL数据库：

- 主机: localhost
- 端口: 5432
- 数据库名: qoratrader
- 用户名: qoratrader
- 密码: qoratrader

要访问数据库：
```bash
psql -h localhost -p 5432 -U qoratrader -d qoratrader
```

### 服务监控

开发环境中可用的服务：

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000
- Database: http://localhost:5432
- InfluxDB: http://localhost:8086
- Redis: http://localhost:6379

查看服务日志：
```bash
docker-compose -f docker/docker-compose.dev.yml logs -f
```

### 运行测试

运行后端测试：
```bash
docker-compose -f docker/docker-compose.dev.yml exec backend python -m pytest
```

运行前端测试：
```bash
cd frontend
npm test
```

### 调试

开发环境已配置调试支持：

- VS Code调试配置：`.vscode/launch.json`
- 后端调试端口：5678
- 前端调试端口：9229

### 常见问题

1. **依赖安装失败**：确保网络连接正常，或尝试使用国内镜像源
2. **端口冲突**：检查是否有其他服务占用了所需端口
3. **权限错误**：在Linux系统上，确保当前用户在docker组中

---

如需更多帮助，请查阅相关文档或联系开发团队。