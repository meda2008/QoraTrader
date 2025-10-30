# 策略管理API

## 获取所有策略列表

`GET /api/v1/strategies`

### 描述
获取系统中所有策略的基本信息列表

### 参数
- page (query, optional): 页码，默认为1
- size (query, optional): 每页大小，默认为10

### 响应
- 200: 
  - Content-Type: application/json
  - Schema:
    ```json
    {
      "data": [
        {
          "id": "string",
          "name": "string",
          "description": "string",
          "version": "string",
          "status": "未激活|已激活|暂停|已停止|异常",
          "createdAt": "string",
          "updatedAt": "string"
        }
      ],
      "total": "integer",
      "page": "integer",
      "size": "integer"
    }
    ```

## 获取单个策略详情

`GET /api/v1/strategies/{strategyId}`

### 描述
获取指定策略的详细信息

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "version": "string",
    "status": "未激活|已激活|暂停|已停止|异常",
    "config": "object",
    "codePath": "string",
    "performanceMetrics": "object",
    "backtestResultId": "string",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```
- 404: 策略不存在

## 创建新策略

`POST /api/v1/strategies`

### 描述
创建一个新的交易策略

### 请求体
```json
{
  "name": "string",
  "description": "string",
  "version": "string",
  "config": "object",
  "codePath": "string"
}
```

### 响应
- 201:
  ```json
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "version": "string",
    "status": "未激活",
    "config": "object",
    "codePath": "string",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```

## 更新策略

`PUT /api/v1/strategies/{strategyId}`

### 描述
更新指定策略的信息

### 参数
- strategyId (path): 策略的唯一标识符

### 请求体
```json
{
  "name": "string",
  "description": "string",
  "config": "object"
}
```

### 响应
- 200:
  ```json
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "version": "string",
    "status": "未激活|已激活|暂停|已停止|异常",
    "config": "object",
    "codePath": "string",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```
- 404: 策略不存在

## 删除策略

`DELETE /api/v1/strategies/{strategyId}`

### 描述
删除指定的策略

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 204: 删除成功
- 404: 策略不存在

## 激活策略

`POST /api/v1/strategies/{strategyId}/activate`

### 描述
激活指定策略，使其开始运行

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "status": "已激活",
    "updatedAt": "string"
  }
  ```
- 400: 策略不能被激活（如已在运行状态）
- 404: 策略不存在

## 暂停策略

`POST /api/v1/strategies/{strategyId}/pause`

### 描述
暂停指定策略的运行

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "status": "暂停",
    "updatedAt": "string"
  }
  ```
- 400: 策略不能被暂停（如已停止或异常）
- 404: 策略不存在

## 停止策略

`POST /api/v1/strategies/{strategyId}/stop`

### 描述
停止指定策略的运行

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "status": "已停止",
    "updatedAt": "string"
  }
  ```
- 400: 策略不能被停止
- 404: 策略不存在

## 获取策略历史表现

`GET /api/v1/strategies/{strategyId}/performance`

### 描述
获取指定策略的历史表现数据

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 200:
  ```json
  {
    "strategyId": "string",
    "performanceData": [
      {
        "date": "string",
        "netValue": "number",
        "cumulativeReturn": "number",
        "dailyReturn": "number"
      }
    ],
    "riskMetrics": {
      "sharpeRatio": "number",
      "maxDrawdown": "number",
      "volatility": "number",
      "winRate": "number"
    }
  }
  ```