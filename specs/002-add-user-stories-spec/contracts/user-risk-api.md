# 用户和风控API

## 用户认证

### 用户登录

`POST /api/v1/auth/login`

### 描述
用户登录并获取访问令牌

### 请求体
```json
{
  "username": "string",
  "password": "string"
}
```

### 响应
- 200:
  ```json
  {
    "token": "string",
    "user": {
      "id": "string",
      "username": "string",
      "email": "string",
      "role": "管理员|策略师|交易员"
    }
  }
  ```
- 401: 认证失败

### 用户登出

`POST /api/v1/auth/logout`

### 描述
用户登出，使访问令牌失效

### 响应
- 204: 成功登出

## 用户管理

### 获取用户列表

`GET /api/v1/users`

### 描述
获取系统中的所有用户

### 参数
- role (query, optional): 用户角色过滤
- status (query, optional): 用户状态过滤
- page (query, optional): 页码
- size (query, optional): 每页大小

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "id": "string",
        "username": "string",
        "email": "string",
        "role": "管理员|策略师|交易员",
        "status": "激活|禁用",
        "createdAt": "string",
        "updatedAt": "string"
      }
    ],
    "total": "integer",
    "page": "integer",
    "size": "integer"
  }
  ```

### 创建用户

`POST /api/v1/users`

### 描述
创建一个新用户

### 请求体
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "管理员|策略师|交易员"
}
```

### 响应
- 201:
  ```json
  {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "管理员|策略师|交易员",
    "status": "激活",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```

### 获取用户详情

`GET /api/v1/users/{userId}`

### 描述
获取特定用户的详细信息

### 参数
- userId (path): 用户的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "管理员|策略师|交易员",
    "status": "激活|禁用",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```

### 更新用户

`PUT /api/v1/users/{userId}`

### 描述
更新用户信息

### 参数
- userId (path): 用户的唯一标识符

### 请求体
```json
{
  "email": "string",
  "role": "管理员|策略师|交易员",
  "status": "激活|禁用"
}
```

### 响应
- 200:
  ```json
  {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "管理员|策略师|交易员",
    "status": "激活|禁用",
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```

### 删除用户

`DELETE /api/v1/users/{userId}`

### 描述
删除特定用户

### 参数
- userId (path): 用户的唯一标识符

### 响应
- 204: 删除成功

## 风控管理

### 获取风控参数

`GET /api/v1/risk-params`

### 描述
获取所有风控参数配置

### 参数
- strategyId (query, optional): 策略ID过滤

### 响应
- 200:
  ```json
  {
    "data": [
      {
        "id": "string",
        "strategyId": "string",
        "strategyName": "string",
        "accountRisk": "object",
        "stockRisk": "object",
        "globalRisk": "object",
        "createdAt": "string",
        "updatedAt": "string"
      }
    ]
  }
  ```

### 获取策略风控参数

`GET /api/v1/strategies/{strategyId}/risk-params`

### 描述
获取特定策略的风控参数

### 参数
- strategyId (path): 策略的唯一标识符

### 响应
- 200:
  ```json
  {
    "id": "string",
    "strategyId": "string",
    "accountRisk": {
      "maxPositionValue": "number",
      "maxDailyLoss": "number",
      "maxPositionPercentage": "number"
    },
    "stockRisk": {
      "maxStockPosition": "number",
      "maxDailyStockTurnover": "number"
    },
    "globalRisk": {
      "maxOrderRate": "number",
      "maxPositionConcentration": "number"
    },
    "createdAt": "string",
    "updatedAt": "string"
  }
  ```

### 更新风控参数

`PUT /api/v1/strategies/{strategyId}/risk-params`

### 描述
更新特定策略的风控参数

### 参数
- strategyId (path): 策略的唯一标识符

### 请求体
```json
{
  "accountRisk": {
    "maxPositionValue": "number",
    "maxDailyLoss": "number",
    "maxPositionPercentage": "number"
  },
  "stockRisk": {
    "maxStockPosition": "number",
    "maxDailyStockTurnover": "number"
  },
  "globalRisk": {
    "maxOrderRate": "number",
    "maxPositionConcentration": "number"
  }
}
```

### 响应
- 200:
  ```json
  {
    "id": "string",
    "strategyId": "string",
    "accountRisk": {
      "maxPositionValue": "number",
      "maxDailyLoss": "number",
      "maxPositionPercentage": "number"
    },
    "stockRisk": {
      "maxStockPosition": "number",
      "maxDailyStockTurnover": "number"
    },
    "globalRisk": {
      "maxOrderRate": "number",
      "maxPositionConcentration": "number"
    },
    "updatedAt": "string"
  }
  ```