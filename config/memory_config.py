import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine
from agents.extensions.memory import SQLAlchemySession
from config.env_config import EnvironmentConfig

class MemoryManager:
    """Memory management system for ReGenAI using PostgreSQL and UUID-based user identification"""
    
    def __init__(self):
        self.engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the async database engine for memory management"""
        database_url = EnvironmentConfig.get_database_url()
        if not database_url:
            raise ValueError("Database URL not configured")
        
        self.engine = create_async_engine(database_url, echo=EnvironmentConfig.DEBUG)
    
    def create_session(self, user_id: Optional[str] = None) -> SQLAlchemySession:
        """
        Create a SQLAlchemySession for a user
        
        Args:
            user_id: Optional user ID. If not provided, generates a new UUID
            
        Returns:
            SQLAlchemySession configured for the user
        """
        if user_id is None:
            user_id = str(uuid.uuid4())
        
        return SQLAlchemySession(
            user_id=user_id,
            engine=self.engine,
            create_tables=True  # Automatically create tables if they don't exist
        )
    
    def generate_user_id(self) -> str:
        """Generate a new UUID for user identification"""
        return str(uuid.uuid4())
    
    async def cleanup(self):
        """Clean up database connections"""
        if self.engine:
            await self.engine.dispose()

# Global memory manager instance
memory_manager = MemoryManager()
