from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

# Enums
class OrderStatus(PyEnum):
    PENDING_SUBMISSION = "pending_submission"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class OrderSide(PyEnum):
    BUY = "buy"
    SELL = "sell"

class OrderType(PyEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

class StrategyStatus(PyEnum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class AccountStatus(PyEnum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    RISK_CONTROL = "risk_control"
    FROZEN = "frozen"

class RiskLevel(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class PositionDirection(PyEnum):
    LONG = "long"
    SHORT = "short"

class AccountType(PyEnum):
    SIMULATED = "simulated"
    LIVE = "live"

class DirectionType(PyEnum):
    BUY = "buy"
    SELL = "sell"

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)  # 'admin', 'strategist', 'trader'
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Strategy model
class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(StrategyStatus), default=StrategyStatus.INACTIVE)
    config = Column(Text)  # JSON configuration for the strategy
    code = Column(Text)  # Strategy code or path
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="strategies")

User.strategies = relationship("Strategy", order_by=Strategy.id, back_populates="user")

# Account model
class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    account_type = Column(Enum(AccountType), default=AccountType.SIMULATED)
    status = Column(Enum(AccountStatus), default=AccountStatus.NORMAL)
    balance = Column(Numeric(20, 6), default=0)
    available_balance = Column(Numeric(20, 6), default=0)
    market_value = Column(Numeric(20, 6), default=0)
    total_pnl = Column(Numeric(20, 6), default=0)
    daily_pnl = Column(Numeric(20, 6), default=0)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="accounts")

User.accounts = relationship("Account", order_by=Account.id, back_populates="user")

# Position model
class Position(Base):
    __tablename__ = "positions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("accounts.id"))
    strategy_id = Column(String, ForeignKey("strategies.id"))
    symbol = Column(String, nullable=False)
    direction = Column(Enum(PositionDirection), nullable=False)
    volume = Column(Numeric(20, 6), default=0)
    available_volume = Column(Numeric(20, 6), default=0)
    avg_price = Column(Numeric(20, 6), default=0)
    unrealized_pnl = Column(Numeric(20, 6), default=0)
    realized_pnl = Column(Numeric(20, 6), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("Account", back_populates="positions")
    strategy = relationship("Strategy", back_populates="positions")

Account.positions = relationship("Position", order_by=Position.id, back_populates="account")
Strategy.positions = relationship("Position", order_by=Position.id, back_populates="strategy")

# Order model
class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, ForeignKey("strategies.id"))
    account_id = Column(String, ForeignKey("accounts.id"))
    symbol = Column(String, nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Numeric(20, 6), nullable=False)
    price = Column(Numeric(20, 6), default=0)  # 0 for market orders
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING_SUBMISSION)
    exchange_order_id = Column(String)  # ID from the exchange
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    executed_at = Column(DateTime)  # When the order was executed/filled
    
    strategy = relationship("Strategy", back_populates="orders")
    account = relationship("Account", back_populates="orders")

Strategy.orders = relationship("Order", order_by=Order.id, back_populates="strategy")
Account.orders = relationship("Order", order_by=Order.id, back_populates="account")

# Trade model
class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"))
    symbol = Column(String, nullable=False)
    side = Column(Enum(DirectionType), nullable=False)
    quantity = Column(Numeric(20, 6), nullable=False)
    price = Column(Numeric(20, 6), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)
    commission = Column(Numeric(20, 6), default=0)
    
    order = relationship("Order", back_populates="trades")

Order.trades = relationship("Trade", order_by=Trade.id, back_populates="order")

# Risk Parameters model
class RiskParams(Base):
    __tablename__ = "risk_params"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, ForeignKey("strategies.id"), nullable=True)  # Null for global rules
    max_position_size = Column(Numeric(20, 6))
    max_order_size = Column(Numeric(20, 6))
    max_daily_loss = Column(Numeric(20, 6))
    max_drawdown = Column(Numeric(20, 6))
    position_limit_per_symbol = Column(Numeric(20, 6))
    daily_order_limit = Column(Integer)
    order_frequency_limit = Column(Integer)  # Limit per seconds
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)
    is_active = Column(Boolean, default=True)
    
    strategy = relationship("Strategy", back_populates="risk_params")

Strategy.risk_params = relationship("RiskParams", order_by=RiskParams.id, back_populates="strategy")

# Backtest Report model
class BacktestReport(Base):
    __tablename__ = "backtest_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_id = Column(String, ForeignKey("strategies.id"))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Numeric(20, 6), nullable=False)
    final_capital = Column(Numeric(20, 6), nullable=False)
    total_return = Column(Numeric(20, 6))
    annual_return = Column(Numeric(20, 6))
    sharpe_ratio = Column(Numeric(20, 6))
    sortino_ratio = Column(Numeric(20, 6))
    calmar_ratio = Column(Numeric(20, 6))
    max_drawdown = Column(Numeric(20, 6))
    win_rate = Column(Numeric(20, 6))
    profit_factor = Column(Numeric(20, 6))
    alpha = Column(Numeric(20, 6))
    beta = Column(Numeric(20, 6))
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    data = Column(Text)  # JSON data for detailed results
    created_at = Column(DateTime, default=datetime.utcnow)
    
    strategy = relationship("Strategy", back_populates="backtest_reports")

Strategy.backtest_reports = relationship("BacktestReport", order_by=BacktestReport.id, back_populates="strategy")

# Market Data model
class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # 'tick', 'bar', 'quote'
    timestamp = Column(DateTime, nullable=False)
    open = Column(Numeric(20, 6))  # For bar data
    high = Column(Numeric(20, 6))  # For bar data
    low = Column(Numeric(20, 6))   # For bar data
    close = Column(Numeric(20, 6)) # For bar data
    volume = Column(Numeric(20, 6))
    turnover = Column(Numeric(20, 6))
    bid_price = Column(Numeric(20, 6))  # For tick data
    ask_price = Column(Numeric(20, 6))  # For tick data
    bid_volume = Column(Numeric(20, 6))  # For tick data
    ask_volume = Column(Numeric(20, 6))  # For tick data

# Indicator Library model
class IndicatorLibrary(Base):
    __tablename__ = "indicator_libraries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String)
    path = Column(String)  # Path to the library
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)