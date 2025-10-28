from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.tables_models import User, Conversation, Message
from utiles.schemas import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationWithMessages,
    MessageCreate, 
    MessageResponse
)
from routes.auth_routes import get_current_user
from config.database_config import get_db
from datetime import datetime
from agent.main_agent import get_agent
from agent.tools import get_user_latest_form
from uuid import uuid4

router = APIRouter()

# Create a new conversation
@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation for the current user"""
    db_conversation = Conversation(
        user_id=current_user.id,
        title=conversation.title,
        conversation_type=conversation.conversation_type
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    
    return ConversationResponse(
        id=db_conversation.id,
        user_id=db_conversation.user_id,
        title=db_conversation.title,
        conversation_type=db_conversation.conversation_type,
        created_at=db_conversation.created_at,
        updated_at=db_conversation.updated_at,
        last_message=None,
        unread_count=0
    )

# Get all conversations for current user
@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    result = []
    for conv in conversations:
        # Get last message
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).first()
        
        result.append(ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            conversation_type=conv.conversation_type,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            last_message=last_message.content if last_message else None,
            unread_count=0  # Can implement read/unread logic later
        ))
    
    return result

# Get a specific conversation with all messages
@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all its messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return ConversationWithMessages(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        conversation_type=conversation.conversation_type,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender=msg.sender,
            content=msg.content,
            created_at=msg.created_at
        ) for msg in messages]
    )

# Send a message (user message + AI response)
@router.post("/messages", response_model=List[MessageResponse])
def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == message_data.conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create user message
    user_message = Message(
        conversation_id=message_data.conversation_id,
        sender='user',
        content=message_data.content
    )
    db.add(user_message)
    
    # Generate AI response using real agent
    try:
        agent = get_agent()
        thread_id = f"conv_{message_data.conversation_id}"
        form = get_user_latest_form(db, current_user.id)
        
        state = {
            "user_id": current_user.id,
            "form": form,
            "message": message_data.content,
        }
        
        result = agent.invoke(state, {"configurable": {"thread_id": thread_id}})
        ai_response_text = result.get("reply", "I'm here to help, but I couldn't generate a response.")
    except Exception as e:
        print(f"Error calling agent: {e}")
        ai_response_text = "I apologize, but I'm having trouble processing your request. Please try again."
    
    # Create AI message
    ai_message = Message(
        conversation_id=message_data.conversation_id,
        sender='agent',
        content=ai_response_text
    )
    db.add(ai_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user_message)
    db.refresh(ai_message)
    
    return [
        MessageResponse(
            id=user_message.id,
            conversation_id=user_message.conversation_id,
            sender=user_message.sender,
            content=user_message.content,
            created_at=user_message.created_at
        ),
        MessageResponse(
            id=ai_message.id,
            conversation_id=ai_message.conversation_id,
            sender=ai_message.sender,
            content=ai_message.content,
            created_at=ai_message.created_at
        )
    ]

# Delete a conversation
@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}

# Note: AI responses are now generated using the real LangGraph agent
# The agent uses Gemini AI with user's farm data and context enrichment

