import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from config.env_config import EnvironmentConfig

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables
DATABASE_URL = EnvironmentConfig.get_database_url()

# Check if the URL is loaded properly
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables")

# Ensure async URL has +asyncpg suffix
async_url = DATABASE_URL
if not async_url.startswith("postgresql+asyncpg://"):
    async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async database engine for OpenAI Agents SDK
async_engine = create_async_engine(
    async_url,
    echo=EnvironmentConfig.DEBUG,
    pool_pre_ping=True,
)

# Create sync database engine for regular operations - ensure it uses psycopg2
sync_url = DATABASE_URL
if sync_url.startswith("postgresql+asyncpg://"):
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://")
sync_engine = create_engine(
    sync_url,
    echo=EnvironmentConfig.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create session factories
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=async_engine
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()