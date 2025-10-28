"""
Database migration script to create chat tables
Run this script to add Conversation and Message tables to the database
"""

from sqlalchemy import create_engine
from models.tables_models import Base, Conversation, Message
from config.database_config import DATABASE_URL

def create_chat_tables():
    """Create chat-related tables in the database"""
    print("Creating chat tables...")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Create only the new tables (Conversation and Message)
        # This won't affect existing tables
        Conversation.__table__.create(engine, checkfirst=True)
        Message.__table__.create(engine, checkfirst=True)
        
        print("✅ Chat tables created successfully!")
        print("   - conversations")
        print("   - messages")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_chat_tables()

