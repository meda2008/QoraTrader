# Data Model: 量化交易系统

## 核心实体

### 策略 (Strategy)
- **属性**:
  - id: UUID (主键)
  - name: string (策略名称)
  - description: string (策略描述)
  - status: enum (未激活, 已激活, 暂停, 已停止, 异常)
  - config: JSON (策略配置参数)
  - code: text (策略代码或引用路径)
  - created_at: datetime
  - updated_at: datetime
  - user_id: UUID (外键，关联用户)

- **验证规则**:
  - name 必须唯一
  - status 转换遵循预定义规则
  - config 必须符合策略接口规范

- **关系**:
  - 一对多: Strategy → Order (一个策略生成多个订单)
  - 一对多: Strategy → BacktestReport (一个策略可多次回测)

### 订单 (Order)
- **属性**:
  - id: UUID (主键)
  - strategy_id: UUID (外键，关联策略)
  - symbol: string (交易标的)
  - order_type: enum (市价单, 限价单, 止损单等)
  - side: enum (买入, 卖出)
  - quantity: decimal (数量)
  - price: decimal (价格，市价单为0)
  - status: enum (未提交, 已提交, 部分成交, 完全成交, 已取消, 已成交)
  - exchange_order_id: string (交易所订单ID)
  - created_at: datetime
  - updated_at: datetime
  - executed_at: datetime (可选，成交时间)

- **验证规则**:
  - quantity > 0
  - price >= 0
  - 状态转换符合业务规则

- **关系**:
  - 多对一: Order → Strategy (多个订单属于一个策略)
  - 一对多: Order → Trade (一个订单可产生多个成交记录)

### 成交 (Trade)
- **属性**:
  - id: UUID (主键)
  - order_id: UUID (外键，关联订单)
  - symbol: string (交易标的)
  - side: enum (买入, 卖出)
  - quantity: decimal (成交量)
  - price: decimal (成交价格)
  - executed_at: datetime (成交时间)
  - commission: decimal (手续费)

- **验证规则**:
  - quantity > 0
  - price > 0
  - quantity 不得超过对应订单的未成交量

- **关系**:
  - 多对一: Trade → Order (多个成交记录对应一个订单)

### 行情数据 (MarketData)
- **属性**:
  - id: UUID (主键)
  - symbol: string (交易标的)
  - data_type: enum (tick, bar, quote)
  - timestamp: datetime (时间戳)
  - open: decimal (开盘价，K线数据)
  - high: decimal (最高价，K线数据)
  - low: decimal (最低价，K线数据)
  - close: decimal (收盘价，K线数据)
  - volume: decimal (成交量)
  - turnover: decimal (成交额)
  - bid_price: decimal (买价，tick数据)
  - ask_price: decimal (卖价，tick数据)
  - bid_volume: decimal (买量，tick数据)
  - ask_volume: decimal (卖量，tick数据)

- **验证规则**:
  - 所有价格字段 >= 0
  - 时间戳按时间序列排序
  - K线数据中的 high >= low, high >= open/close, low <= open/close

- **关系**:
  - 一对多: MarketData → BacktestReport (行情数据用于回测)

### 持仓 (Position)
- **属性**:
  - id: UUID (主键)
  - account_id: UUID (外键，关联账户)
  - strategy_id: UUID (外键，关联策略)
  - symbol: string (交易标的)
  - direction: enum (多头, 空头)
  - volume: decimal (持仓量)
  - available_volume: decimal (可用持仓量)
  - avg_price: decimal (平均成本价)
  - unrealized_pnl: decimal (未实现盈亏)
  - realized_pnl: decimal (已实现盈亏)
  - created_at: datetime
  - updated_at: datetime

- **验证规则**:
  - volume >= 0
  - available_volume >= 0
  - available_volume <= volume

- **关系**:
  - 多对一: Position → Account (多个持仓属于一个账户)
  - 多对一: Position → Strategy (多个持仓属于一个策略)

### 账户 (Account)
- **属性**:
  - id: UUID (主键)
  - user_id: UUID (外键，关联用户)
  - account_type: enum (模拟, 实盘)
  - status: enum (正常, 限制, 风控, 冻结)
  - balance: decimal (账户余额)
  - available_balance: decimal (可用余额)
  - market_value: decimal (市值)
  - total_pnl: decimal (总盈亏)
  - daily_pnl: decimal (当日盈亏)
  - risk_level: enum (低, 中, 高, 极高)
  - created_at: datetime
  - updated_at: datetime

- **验证规则**:
  - balance >= 0
  - available_balance >= 0
  - available_balance <= balance

- **关系**:
  - 一对多: Account → Position (一个账户有多个持仓)
  - 一对多: Account → Order (一个账户发出多个订单)

### 回测报告 (BacktestReport)
- **属性**:
  - id: UUID (主键)
  - strategy_id: UUID (外键，关联策略)
  - start_date: date (回测开始日期)
  - end_date: date (回测结束日期)
  - initial_capital: decimal (初始资金)
  - final_capital: decimal (最终资金)
  - total_return: decimal (总收益率)
  - annual_return: decimal (年化收益率)
  - sharpe_ratio: decimal (夏普比率)
  - sortino_ratio: decimal (索提诺比率)
  - calmar_ratio: decimal (卡玛比率)
  - max_drawdown: decimal (最大回撤)
  - win_rate: decimal (胜率)
  - profit_factor: decimal (盈亏比)
  - alpha: decimal (阿尔法)
  - beta: decimal (贝塔)
  - total_trades: integer (总交易次数)
  - winning_trades: integer (盈利交易次数)
  - losing_trades: integer (亏损交易次数)
  - data: JSON (详细回测数据和图表数据)
  - created_at: datetime

- **验证规则**:
  - 所有比率字段应为有效数值
  - 日期范围有效

- **关系**:
  - 多对一: BacktestReport → Strategy (多个回测报告属于一个策略)

### 风控参数 (RiskParams)
- **属性**:
  - id: UUID (主键)
  - strategy_id: UUID (外键，关联策略，可为空代表全局)
  - max_position_size: decimal (最大持仓规模)
  - max_order_size: decimal (最大订单规模)
  - max_daily_loss: decimal (最大日亏损)
  - max_drawdown: decimal (最大回撤限制)
  - position_limit_per_symbol: decimal (单标的持仓限制)
  - daily_order_limit: integer (日订单数量限制)
  - order_frequency_limit: integer (订单频率限制，单位秒)
  - risk_level: enum (低, 中, 高)
  - is_active: boolean (是否激活)

- **验证规则**:
  - 所有限制参数 >= 0
  - risk_level 符合预定义枚举

- **关系**:
  - 多对一: RiskParams → Strategy (风控参数属于策略)

### 指标库 (IndicatorLibrary)
- **属性**:
  - id: UUID (主键)
  - name: string (指标库名称)
  - description: string (指标库描述)
  - version: string (版本号)
  - path: string (库文件路径)
  - is_active: boolean (是否激活)
  - created_at: datetime
  - updated_at: datetime

- **验证规则**:
  - name 在系统中唯一
  - path 有效且可达

- **关系**:
  - 一对多: IndicatorLibrary → Strategy (一个指标库可被多个策略使用)

### 用户 (User)
- **属性**:
  - id: UUID (主键)
  - username: string (用户名)
  - email: string (邮箱)
  - role: enum (管理员, 策略师, 交易员)
  - password_hash: string (密码哈希)
  - is_active: boolean (是否激活)
  - created_at: datetime
  - updated_at: datetime

- **验证规则**:
  - username 唯一
  - email 格式有效
  - role 符合预定义枚举

- **关系**:
  - 一对多: User → Strategy (一个用户可创建多个策略)
  - 一对多: User → Account (一个用户可管理多个账户)

### 参数优化任务 (ParameterOptimization)
- **属性**:
  - id: UUID (主键)
  - strategy_id: UUID (外键，关联策略)
  - optimization_type: enum (网格搜索, 贝叶斯优化, 遗传算法, 强化学习)
  - parameters_space: JSON (参数搜索空间定义)
  - status: enum (待处理, 处理中, 已完成, 已取消, 失败)
  - best_params: JSON (最佳参数组合)
  - best_result: JSON (最佳结果指标)
  - all_results: JSON (所有尝试结果)
  - created_at: datetime
  - updated_at: datetime

- **验证规则**:
  - parameters_space 必须符合规范格式
  - status 转换遵循预定义规则

- **关系**:
  - 多对一: ParameterOptimization → Strategy (参数优化任务属于特定策略)

## 状态转换规则

### 订单状态转换
```
未提交 → 已提交 → 部分成交 → 完全成交
     ↓         ↓         ↓         ↓
   已取消 ← 已提交 ← 部分成交 ← 完全成交
```

### 策略状态转换
```
未激活 → 已激活 → 暂停 → 已停止
   ↑        ↓              ↑
   └---- 已停止 ←------------┘
   ↓
异常 (错误状态，需人工干预)
```

### 账户状态转换
```
正常 → 限制 → 风控 → 冻结
  ↑     ↑     ↑     ↑
  └-----┴-----┴-----┘
```

### 回测报告状态
- 生成中 → 已完成/失败

### 参数优化任务状态
- 待处理 → 处理中 → 已完成/已取消/失败