# 账户和持仓API

## 获取账户列表

`GET /api/v1/accounts`

### 描述
获取系统中所有账户的信息

### 参数
- page (query, optional): 页码，默认为1
- size (query, optional): 每页大小，默认为10

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "id": "string",
        "name": "string",
        "accountNumber": "string",
        "status": "正常|限制|风控|冻结",
        "totalFunds": "number",
        "availableFunds": "number",
        "frozenFunds": "number",
        "cumulativeProfit": "number",
        "createdAt": "string",
        "updatedAt": "string"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
  ```

## 获取特定账户信息

`GET /api/v1/accounts/{accountId}`

### 描述
获取特定账户的详细信息

### 参数
- accountId (path): 账户的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "name": "string",
    "accountNumber": "string",
    "status": "正常|限制|风控|冻结",
    "totalFunds": "number",
    "availableFunds": "number",
    "frozenFunds": "number",
    "cumulativeProfit": "number",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```
- 404: 账户不存在

## 获取账户持仓

`GET /api/v1/accounts/{accountId}/positions`

### 描述
获取特定账户的所有持仓信息

### 参数
- accountId (path): 账户的唯一标识符

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "id": "string",
        "strategyId": "string",
        "symbol": "string",
        "direction": "多头|空头",
        "positionQuantity": "integer",
        "availableQuantity": "integer",
        "positionCost": "number",
        "currentPrice": "number",
        "floatingPnL": "number",
        "pnlRatio": "number",
        "createdAt": "string",
        "updatedAt": "string"
      }
    ]
  }
  ```
- 404: 账户不存在

## 获取特定持仓

`GET /api/v1/positions/{positionId}`

### 描述
获取特定持仓的详细信息

### 参数
- positionId (path): 持仓的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "accountId": "string",
    "strategyId": "string",
    "symbol": "string",
    "direction": "多头|空头",
    "positionQuantity": "integer",
    "availableQuantity": "integer",
    "positionCost": "number",
    "currentPrice": "number",
    "floatingPnL": "number",
    "pnlRatio": "number",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```
- 404: 持仓不存在

## 获取账户成交记录

`GET /api/v1/accounts/{accountId}/trades`

### 描述
获取特定账户的成交记录

### 参数
- accountId (path): 账户的唯一标识符
- page (query, optional): 页码
- size (query, optional): 每页大小
- startTime (query, optional): 开始时间
- endTime (query, optional): 结束时间

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "id": "string",
        "orderId": "string",
        "strategyId": "string",
        "symbol": "string",
        "direction": "买入|卖出",
        "tradePrice": "number",
        "tradeQuantity": "integer",
        "tradeTime": "string",
        "fee": "number"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
  ```
- 404: 账户不存在