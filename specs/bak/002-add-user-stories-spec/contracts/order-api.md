# 订单管理API

## 获取订单列表

`GET /api/v1/orders`

### 描述
获取系统中的订单列表，支持按策略、账户等条件筛选

### 参数
- strategyId (query, optional): 策略ID
- accountId (query, optional): 账户ID
- status (query, optional): 订单状态（未提交|已提交|部分成交|完全成交|已取消|已拒绝）
- page (query, optional): 页码，默认为1
- size (query, optional): 每页大小，默认为10

### 响应
- 200: 
  ```json
  {
    "data": [
      {
        "id": "string",
        "strategyId": "string",
        "exchangeOrderId": "string",
        "accountId": "string",
        "symbol": "string",
        "direction": "买入|卖出",
        "orderType": "市价单|限价单|止损单",
        "status": "未提交|已提交|部分成交|完全成交|已取消|已拒绝",
        "price": "number",
        "quantity": "integer",
        "filledQuantity": "integer",
        "averageFillPrice": "number",
        "submitTime": "string",
        "updateTime": "string",
        "cancelTime": "string"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
  ```

## 获取特定订单

`GET /api/v1/orders/{orderId}`

### 描述
获取特定订单的详细信息

### 参数
- orderId (path): 订单的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "strategyId": "string",
    "exchangeOrderId": "string",
    "accountId": "string",
    "symbol": "string",
    "direction": "买入|卖出",
    "orderType": "市价单|限价单|止损单",
    "status": "未提交|已提交|部分成交|完全成交|已取消|已拒绝",
    "price": "number",
    "quantity": "integer",
    "filledQuantity": "integer",
    "averageFillPrice": "number",
    "submitTime": "string",
    "updateTime": "string",
    "cancelTime": "string"
  }
  ```
- 404: 订单不存在

## 创建新订单

`POST /api/v1/orders`

### 描述
创建一个新的交易订单，提交到交易所

### 请求体
```json
{
  "strategyId": "string",
  "accountId": "string",
  "symbol": "string",
  "direction": "买入|卖出",
  "orderType": "市价单|限价单|止损单",
  "price": "number",
  "quantity": "integer"
}
```

### 响应
- 201:
  ```json
  {
    "id": "string",
    "strategyId": "string",
    "exchangeOrderId": "string",
    "accountId": "string",
    "symbol": "string",
    "direction": "买入|卖出",
    "orderType": "市价单|限价单|止损单",
    "status": "未提交",
    "price": "number",
    "quantity": "integer",
    "submitTime": "string",
    "updateTime": "string"
  }
  ```

## 取消订单

`DELETE /api/v1/orders/{orderId}`

### 描述
取消一个已提交但未完全成交的订单

### 参数
- orderId (path): 订单的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "status": "已取消",
    "updateTime": "string"
  }
  ```
- 400: 订单不能被取消（如已成交或已取消）
- 404: 订单不存在

## 获取账户订单列表

`GET /api/v1/accounts/{accountId}/orders`

### 描述
获取特定账户下的所有订单

### 参数
- accountId (path): 账户ID
- status (query, optional): 订单状态
- page (query, optional): 页码
- size (query, optional): 每页大小

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "id": "string",
        "strategyId": "string",
        "exchangeOrderId": "string",
        "symbol": "string",
        "direction": "买入|卖出",
        "orderType": "市价单|限价单|止损单",
        "status": "未提交|已提交|部分成交|完全成交|已取消|已拒绝",
        "price": "number",
        "quantity": "integer",
        "filledQuantity": "integer",
        "averageFillPrice": "number",
        "submitTime": "string",
        "updateTime": "string"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
  ```

## 获取策略订单列表

`GET /api/v1/strategies/{strategyId}/orders`

### 描述
获取特定策略下的所有订单

### 参数
- strategyId (path): 策略ID
- status (query, optional): 订单状态
- page (query, optional): 页码
- size (query, optional): 每页大小

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "id": "string",
        "exchangeOrderId": "string",
        "accountId": "string",
        "symbol": "string",
        "direction": "买入|卖出",
        "orderType": "市价单|限价单|止损单",
        "status": "未提交|已提交|部分成交|完全成交|已取消|已拒绝",
        "price": "number",
        "quantity": "integer",
        "filledQuantity": "integer",
        "averageFillPrice": "number",
        "submitTime": "string",
        "updateTime": "string"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
  ```