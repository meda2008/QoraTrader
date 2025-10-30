# 回测API

## 启动回测任务

`POST /api/v1/backtest`

### 描述
启动一个新的回测任务

### 请求体
```json
{
  "strategyId": "string",
  "backtestName": "string",
  "startTime": "string",
  "endTime": "string",
  "initialFunds": "number",
  "parameters": "object"
}
```

### 响应
- 201:
  ```json
  {
    "taskId": "string",
    "strategyId": "string",
    "backtestName": "string",
    "status": "排队中|运行中|已完成|已失败",
    "startTime": "string",
    "endTime": "string",
    "createdAt": "string"
  }
  ```

## 获取回测任务列表

`GET /api/v1/backtest`

### 描述
获取回测任务列表

### 参数
- strategyId (query, optional): 策略ID
- status (query, optional): 任务状态
- page (query, optional): 页码
- size (query, optional): 每页大小

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "taskId": "string",
        "strategyId": "string",
        "strategyName": "string",
        "backtestName": "string",
        "status": "排队中|运行中|已完成|已失败",
        "startTime": "string",
        "endTime": "string",
        "initialFunds": "number",
        "finalFunds": "number",
        "totalReturn": "number",
        "sharpeRatio": "number",
        "maxDrawdown": "number",
        "winRate": "number",
        "createdAt": "string",
        "updatedAt": "string"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
  ```

## 获取回测任务详情

`GET /api/v1/backtest/{taskId}`

### 描述
获取特定回测任务的详细信息

### 参数
- taskId (path): 回测任务的唯一标识符

### 响应
- 200:
  ```json
  {
    "taskId": "string",
    "strategyId": "string",
    "strategyName": "string",
    "backtestName": "string",
    "status": "排队中|运行中|已完成|已失败",
    "startTime": "string",
    "endTime": "string",
    "initialFunds": "number",
    "finalFunds": "number",
    "totalReturn": "number",
    "annualizedReturn": "number",
    "sharpeRatio": "number",
    "maxDrawdown": "number",
    "winRate": "number",
    "profitLossRatio": "number",
    "tradeCount": "integer",
    "parameters": "object",
    "detailedTrades": [
      {
        "orderType": "买入|卖出",
        "symbol": "string",
        "price": "number",
        "quantity": "integer",
        "fee": "number",
        "tradeTime": "string"
      }
    ],
    "performanceChart": [
      {
        "date": "string",
        "netValue": "number",
        "cumulativeReturn": "number"
      }
    ],
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```
- 404: 回测任务不存在

## 删除回测报告

`DELETE /api/v1/backtest/{taskId}`

### 描述
删除特定的回测报告

### 参数
- taskId (path): 回测任务的唯一标识符

### 响应
- 204: 删除成功
- 404: 回测任务不存在

## 获取策略回测历史

`GET /api/v1/strategies/{strategyId}/backtests`

### 描述
获取特定策略的所有回测历史

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "taskId": "string",
        "backtestName": "string",
        "status": "已完成",
        "startTime": "string",
        "endTime": "string",
        "initialFunds": "number",
        "finalFunds": "number",
        "totalReturn": "number",
        "sharpeRatio": "number",
        "maxDrawdown": "number",
        "createdAt": "string"
      }
    ]
  }
  ```