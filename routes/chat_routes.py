from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from models.tables_models import User, Conversation, Message
from utiles.schemas import (
    ConversationCreate, 
    ConversationResponse, 
    ConversationWithMessages,
    MessageCreate, 
    MessageResponse,
    ConversationTitleUpdate
)
from routes.auth_routes import get_current_user
from config.database_config import get_db
from datetime import datetime
from agent.main_agent import get_agent
from agent.tools import get_user_latest_form
from uuid import uuid4
import json
import time
import traceback

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

# Stream a message (user message + streamed AI response)
@router.post("/messages/stream")
def send_message_stream(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and stream the AI response as text/event-stream.
    Frontend can read with fetch() and incrementally render 'delta' events.
    """
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

    # Create user message immediately
    user_message = Message(
        conversation_id=message_data.conversation_id,
        sender='user',
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    def sse_pack(event: str, data: dict) -> str:
        return f"data: {json.dumps({'event': event, 'data': data})}\n\n"

    def generator():
        # Notify start
        yield sse_pack('start', {
            'user_message_id': user_message.id,
            'conversation_id': user_message.conversation_id
        })

        # Invoke agent and get full reply; stream in chunks to client
        try:
            agent = get_agent()
            thread_id = f"conv_{message_data.conversation_id}"
            form = get_user_latest_form(db, current_user.id)
            
            print(f"[AGENT] Calling agent for user {current_user.id}, thread {thread_id}")
            print(f"[AGENT] Form data: {form}")
            print(f"[AGENT] Message: {message_data.content}")
            
            state = {
                "user_id": current_user.id,
                "form": form,
                "message": message_data.content,
            }
            result = agent.invoke(state, {"configurable": {"thread_id": thread_id}})
            ai_response_text = result.get("reply", "I'm here to help, but I couldn't generate a response.")
            
            print(f"[AGENT] Success! Response length: {len(ai_response_text)} chars")
        except Exception as e:
            print(f"[AGENT ERROR] {type(e).__name__}: {e}")
            print(f"[AGENT ERROR] Traceback: {traceback.format_exc()}")
            ai_response_text = f"I apologize, but I'm having trouble processing your request. Error: {str(e)[:100]}"

        # Stream chunks with small delay for smoother animation
        chunk_size = 80
        for i in range(0, len(ai_response_text), chunk_size):
            chunk = ai_response_text[i:i+chunk_size]
            yield sse_pack('delta', { 'text': chunk })
            time.sleep(0.05)  # 50ms delay for smooth typing effect

        # Persist AI message once finished
        ai_message = Message(
            conversation_id=message_data.conversation_id,
            sender='agent',
            content=ai_response_text
        )
        db.add(ai_message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ai_message)

        # Notify end with final ids
        yield sse_pack('end', {
            'ai_message_id': ai_message.id,
            'conversation_id': ai_message.conversation_id
        })

    return StreamingResponse(generator(), media_type="text/event-stream")

# Update conversation title
@router.put("/conversations/{conversation_id}/title", response_model=ConversationResponse)
def update_conversation_title(
    conversation_id: int,
    payload: ConversationTitleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    conversation.title = payload.title
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)

    # Compute last message preview
    last_message = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.desc()).first()

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        conversation_type=conversation.conversation_type,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message=last_message.content if last_message else None,
        unread_count=0
    )

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

