from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create the database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections are alive before using them
    pool_recycle=300,    # Recycle connections after 5 minutes
    echo=False           # Set to True for SQL query logging
)

# Create a configured "Session" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create a base class for declarative models
Base = declarative_base()

def get_db():
    """
    Dependency function for FastAPI to get database sessions
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")