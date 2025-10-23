# 部署指南

## 一键部署应用

本指南介绍如何使用一键部署脚本部署QoraTrader量化交易系统。

### 前置条件

在部署之前，请确保系统满足以下要求：

- Docker Engine 20.10或更高版本
- Docker Compose v2或更高版本
- 至少4GB可用内存
- 至少10GB可用磁盘空间

### 环境配置

1. 复制环境配置文件模板：

```bash
cp .env.example .env
```

2. 编辑`.env`文件，根据您的环境配置以下参数：

```bash
# 数据库配置
DATABASE_URL=postgresql://qoratrader:qoratrader@localhost:5432/qoratrader

# InfluxDB配置
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=your-org
INFLUXDB_BUCKET=trading_data

# API密钥
EXCHANGE_API_KEY=your-exchange-api-key
EXCHANGE_API_SECRET=your-exchange-api-secret

# 应用配置
SECRET_KEY=your-secret-key
DEBUG_MODE=false  # 生产环境设为false
```

### 部署命令

运行以下命令进行部署：

```bash
# 部署到生产环境（默认）
bash scripts/deploy.sh deploy production

# 部署到开发环境
bash scripts/deploy.sh deploy development

# 部署到预发布环境
bash scripts/deploy.sh deploy staging
```

### 验证部署

部署完成后，您可以通过以下方式验证系统是否正常运行：

1. 检查服务状态：
```bash
docker-compose -f docker/docker-compose.yml ps
```

2. 访问API健康检查端点：
```bash
curl http://localhost:8000/health
```

3. 访问Web界面：
打开浏览器并访问 `http://localhost:3000`

### 滚动回滚

如果部署出现问题，可以执行回滚操作：

```bash
bash scripts/deploy.sh rollback production
```

### 常见问题

1. **端口冲突**：如果部署失败提示端口被占用，请检查以下端口是否被其他服务占用：
   - 8000 (Backend API)
   - 3000 (Frontend UI)
   - 5432 (PostgreSQL)
   - 8086 (InfluxDB)
   - 6379 (Redis)

2. **内存不足**：如果部署过程中出现内存不足错误，请确保系统至少有4GB可用内存。

3. **网络连接失败**：确保系统可以访问外部网络以下载Docker镜像。

### 监控与维护

系统部署后，可以通过以下方式进行监控：

- 查看服务日志：`docker-compose logs -f`
- 监控资源使用：`docker stats`
- 访问InfluxDB管理界面：`http://localhost:8086`

---

如需进一步支持，请联系开发团队。