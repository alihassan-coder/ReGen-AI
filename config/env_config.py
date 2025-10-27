import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class EnvironmentConfig:
    """Configuration class for environment variables"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY_ALI", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    NEON_DATABASE_URL: str = os.getenv("NEON_DATABASE_URL", "")
    
    # API Keys for Climate Data
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    AIRVISUAL_API_KEY: str = os.getenv("AIRVISUAL_API_KEY", "")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "ReGenAI")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get the primary database URL, preferring Neon if available"""
        return cls.NEON_DATABASE_URL if cls.NEON_DATABASE_URL else cls.DATABASE_URL
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        required_vars = [
            cls.OPENAI_API_KEY or cls.GEMINI_API_KEY,
            cls.get_database_url()
        ]
        return all(required_vars)
