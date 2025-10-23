from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # App settings
    APP_NAME: str = "QoraTrader Quantitative Trading System"
    APP_DESCRIPTION: str = "A quantitative trading system supporting strategy backtesting, live trading, and risk management"
    APP_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    OPENAPI_URL: Optional[str] = "/openapi.json"
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    
    # Server settings
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG_MODE: bool = True
    
    # Database settings
    DATABASE_URL: str = "postgresql://qoratrader:qoratrader@localhost:5432/qoratrader"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # InfluxDB settings (for time-series data)
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = "your-influxdb-token"
    INFLUXDB_ORG: str = "your-org"
    INFLUXDB_BUCKET: str = "trading_data"
    
    # Trading settings
    MIN_ORDER_SIZE: float = 100.0
    MAX_ORDER_SIZE: float = 1000000.0
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Exchange settings
    EXCHANGE_API_KEY: str = os.getenv("EXCHANGE_API_KEY", "")
    EXCHANGE_API_SECRET: str = os.getenv("EXCHANGE_API_SECRET", "")
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    model_config = {"env_file": ".env", "case_sensitive": True}

# Create settings instance
settings = Settings()