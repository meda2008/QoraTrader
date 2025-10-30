# API Contracts for Quantitative Trading System

## 1. 策略管理 API

### 1.1 创建策略
- **Endpoint**: `POST /api/v1/strategies`
- **Request**:
  ```json
  {
    "name": "strategy_name",
    "description": "strategy_description",
    "code": "strategy_code",
    "config": {
      "param1": "value1",
      "param2": "value2"
    }
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": "uuid",
    "name": "strategy_name",
    "description": "strategy_description",
    "status": "未激活",
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

### 1.2 激活策略
- **Endpoint**: `POST /api/v1/strategies/{strategy_id}/activate`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "status": "已激活"
  }
  ```

### 1.3 暂停策略
- **Endpoint**: `POST /api/v1/strategies/{strategy_id}/pause`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "status": "暂停"
  }
  ```

### 1.4 停止策略
- **Endpoint**: `POST /api/v1/strategies/{strategy_id}/stop`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "status": "已停止"
  }
  ```

### 1.5 获取策略列表
- **Endpoint**: `GET /api/v1/strategies`
- **Response**: 200 OK
  ```json
  [
    {
      "id": "uuid",
      "name": "strategy_name",
      "description": "strategy_description",
      "status": "已激活",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
  ```

### 1.6 获取策略详情
- **Endpoint**: `GET /api/v1/strategies/{strategy_id}`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "name": "strategy_name",
    "description": "strategy_description",
    "status": "已激活",
    "config": {
      "param1": "value1",
      "param2": "value2"
    },
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
  ```

## 2. 订单管理 API

### 2.1 下单
- **Endpoint**: `POST /api/v1/orders`
- **Request**:
  ```json
  {
    "strategy_id": "uuid",
    "symbol": "600036.SH",
    "order_type": "限价单",
    "side": "买入",
    "quantity": 100,
    "price": 10.5
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": "uuid",
    "strategy_id": "uuid",
    "symbol": "600036.SH",
    "order_type": "限价单",
    "side": "买入",
    "quantity": 100,
    "price": 10.5,
    "status": "已提交",
    "exchange_order_id": "exchange_order_id",
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

### 2.2 获取订单详情
- **Endpoint**: `GET /api/v1/orders/{order_id}`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "strategy_id": "uuid",
    "symbol": "600036.SH",
    "order_type": "限价单",
    "side": "买入",
    "quantity": 100,
    "price": 10.5,
    "status": "已成交",
    "exchange_order_id": "exchange_order_id",
    "executed_at": "2023-01-01T00:00:00Z",
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

### 2.3 获取策略订单列表
- **Endpoint**: `GET /api/v1/strategies/{strategy_id}/orders`
- **Response**: 200 OK
  ```json
  [
    {
      "id": "uuid",
      "symbol": "600036.SH",
      "order_type": "限价单",
      "side": "买入",
      "quantity": 100,
      "price": 10.5,
      "status": "已成交",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
  ```

## 3. 风控管理 API

### 3.1 配置风控规则
- **Endpoint**: `POST /api/v1/risk-rules`
- **Request**:
  ```json
  {
    "strategy_id": "uuid", // 可选，null为全局规则
    "max_position_size": 1000000,
    "max_order_size": 100000,
    "max_daily_loss": 50000,
    "max_drawdown": 0.1,
    "is_active": true
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": "uuid",
    "strategy_id": "uuid",
    "max_position_size": 1000000,
    "max_order_size": 100000,
    "max_daily_loss": 50000,
    "max_drawdown": 0.1,
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

### 3.2 更新风控规则
- **Endpoint**: `PUT /api/v1/risk-rules/{rule_id}`
- **Response**: 200 OK

## 4. 回测引擎 API

### 4.1 创建回测任务
- **Endpoint**: `POST /api/v1/backtest`
- **Request**:
  ```json
  {
    "strategy_id": "uuid",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000,
    "data_symbols": ["600036.SH", "000001.SZ"]
  }
  ```
- **Response**: 202 Created
  ```json
  {
    "id": "uuid",
    "strategy_id": "uuid",
    "status": "处理中",
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

### 4.2 获取回测报告
- **Endpoint**: `GET /api/v1/backtest/{report_id}`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "strategy_id": "uuid",
    "status": "已完成",
    "report": {
      "total_return": 0.15,
      "annual_return": 0.18,
      "sharpe_ratio": 1.5,
      "max_drawdown": 0.05,
      "win_rate": 0.6,
      "profit_factor": 1.8,
      "total_trades": 150
    }
  }
  ```

## 5. 账户与持仓 API

### 5.1 获取账户信息
- **Endpoint**: `GET /api/v1/accounts/{account_id}`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "account_type": "实盘",
    "status": "正常",
    "balance": 100000,
    "available_balance": 80000,
    "market_value": 20000,
    "total_pnl": 5000,
    "risk_level": "中"
  }
  ```

### 5.2 获取持仓列表
- **Endpoint**: `GET /api/v1/accounts/{account_id}/positions`
- **Response**: 200 OK
  ```json
  [
    {
      "id": "uuid",
      "symbol": "600036.SH",
      "direction": "多头",
      "volume": 1000,
      "available_volume": 1000,
      "avg_price": 10.5,
      "unrealized_pnl": 500,
      "realized_pnl": 0
    }
  ]
  ```

## 6. 指标库管理 API

### 6.1 注册指标库
- **Endpoint**: `POST /api/v1/indicator-libraries`
- **Request**:
  ```json
  {
    "name": "TA-Lib",
    "description": "Technical Analysis Library",
    "version": "0.4.24",
    "path": "/path/to/talib"
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": "uuid",
    "name": "TA-Lib",
    "description": "Technical Analysis Library",
    "version": "0.4.24",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

## 7. 实时数据 API

### 7.1 订阅行情
- **Endpoint**: `GET /ws/market-data/{symbol}`
- **WebSocket endpoint** for real-time market data streaming

### 7.2 获取历史行情
- **Endpoint**: `GET /api/v1/market-data/{symbol}`
- **Query Parameters**:
  - `start_date`: "2023-01-01"
  - `end_date`: "2023-01-31"
  - `freq`: "1min" or "1day"

## 8. 系统监控 API

### 8.1 获取系统状态
- **Endpoint**: `GET /api/v1/health`
- **Response**: 200 OK
  ```json
  {
    "status": "healthy",
    "timestamp": "2023-01-01T00:00:00Z",
    "components": {
      "trading_engine": "healthy",
      "market_data": "healthy",
      "risk_management": "healthy"
    }
  }
  ```

### 8.2 获取系统指标
- **Endpoint**: `GET /api/v1/metrics`
- **Response**: 200 OK
  ```json
  {
    "p99_latency_ms": 0.8,
    "active_strategies": 5,
    "orders_per_second": 120,
    "memory_usage_mb": 512
  }
  ```

## 9. 参数优化 API

### 9.1 创建参数优化任务
- **Endpoint**: `POST /api/v1/parameter-optimization`
- **Request**:
  ```json
  {
    "strategy_id": "uuid",
    "optimization_type": "grid_search", // or "bayesian", "genetic", "reinforcement_learning"
    "parameters": {
      "param1": {"min": 10, "max": 50, "step": 5},
      "param2": {"min": 0.1, "max": 0.9, "step": 0.1}
    },
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000
  }
  ```
- **Response**: 201 Created
  ```json
  {
    "id": "uuid",
    "strategy_id": "uuid",
    "status": "processing",
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

### 9.2 获取参数优化结果
- **Endpoint**: `GET /api/v1/parameter-optimization/{optimization_id}`
- **Response**: 200 OK
  ```json
  {
    "id": "uuid",
    "strategy_id": "uuid",
    "status": "completed",
    "best_params": {
      "param1": 25,
      "param2": 0.6
    },
    "best_result": {
      "total_return": 0.15,
      "sharpe_ratio": 1.5,
      "max_drawdown": 0.05
    },
    "all_results": [
      {
        "params": {"param1": 10, "param2": 0.3},
        "metrics": {"total_return": 0.12, "sharpe_ratio": 1.2}
      }
    ]
  }
  ```