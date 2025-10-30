import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/qora_trader")
    TIMESCALEDB_URL = os.getenv("TIMESCALEDB_URL", "postgresql://user:password@localhost:5433/qora_trader")
    
    # Redis settings
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API settings
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "QoraTrader"
    
    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Exchange settings
    MINI_QMT_PATH = os.getenv("MINI_QMT_PATH", "")
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    
    # Performance settings
    MAX_STRATEGIES = int(os.getenv("MAX_STRATEGIES", "20"))
    MAX_ORDER_RATE = int(os.getenv("MAX_ORDER_RATE", "100"))  # per second
    
    # Backtesting settings
    BACKTEST_MAX_YEARS = int(os.getenv("BACKTEST_MAX_YEARS", "5"))
    BACKTEST_MAX_DATAPOINTS = int(os.getenv("BACKTEST_MAX_DATAPOINTS", "1000000"))

config = Config()