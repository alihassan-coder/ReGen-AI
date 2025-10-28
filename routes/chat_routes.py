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
    
    # Generate AI response
    ai_response_text = generate_ai_response(message_data.content, conversation.conversation_type)
    
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

# Helper function to generate AI responses
def generate_ai_response(user_message: str, conversation_type: str = None) -> str:
    """Generate contextual AI responses based on conversation type"""
    
    # Simple keyword-based responses for now
    # In production, this would call your AI agent
    
    user_message_lower = user_message.lower()
    
    # Climate insights responses
    if conversation_type == 'climate-insights' or any(word in user_message_lower for word in ['climate', 'air', 'quality', 'pollution']):
        responses = [
            "Based on the latest climate data, I can help you understand your area's environmental conditions. Your local air quality index has been moderate recently. I recommend focusing on tree planting and reducing emissions during peak hours.",
            "Great question about climate action! The data shows that implementing sustainable practices in your area could reduce CO₂ emissions by up to 15%. Would you like specific recommendations?",
            "Climate monitoring in your region indicates stable conditions. The best actions you can take now include supporting green infrastructure and participating in community environmental initiatives."
        ]
    
    # Farm optimization responses
    elif conversation_type == 'farm-optimization' or any(word in user_message_lower for word in ['farm', 'crop', 'soil', 'plant']):
        responses = [
            "Your soil analysis shows good potential for sustainable farming. Based on your location and climate data, I recommend considering crop rotation and organic fertilizers to improve yield.",
            "For optimal farm productivity, the weather patterns suggest this is a great time for planting. I can provide specific crop recommendations based on your soil type and water availability.",
            "Farm optimization tip: Your land characteristics indicate you could benefit from water conservation techniques. Drip irrigation and mulching could improve your crop yield by 20-30%."
        ]
    
    # Community actions responses
    elif conversation_type == 'community-actions' or any(word in user_message_lower for word in ['community', 'event', 'tree', 'planting']):
        responses = [
            "I've identified several community action opportunities in your area! Tree planting events and clean-up drives are scheduled for this month. These initiatives have shown great impact on local air quality.",
            "Community engagement is key to climate action! Based on participation data, coordinated efforts in your area have already offset 2.5 tons of CO₂. Would you like to join upcoming events?",
            "Your community has been very active! I recommend the upcoming tree planting drive on Saturday. Weather conditions will be ideal, and we expect good turnout."
        ]
    
    # Pollution alerts responses
    elif conversation_type == 'pollution-alerts' or any(word in user_message_lower for word in ['alert', 'pollution', 'warning']):
        responses = [
            "Air quality monitoring shows improvement in your region. Recent community actions have reduced pollution levels by 8%. Keep up the great work!",
            "Pollution alert: Air quality is expected to be moderate today. I recommend limiting outdoor activities during peak traffic hours (8-10 AM and 5-7 PM).",
            "Good news! Pollution levels have decreased compared to last week. Your community's eco-friendly initiatives are making a real difference."
        ]
    
    # General responses
    else:
        responses = [
            "That's a great question! Based on environmental data and your goals, I can provide tailored recommendations. What specific aspect of climate action would you like to focus on?",
            "I'm here to help with climate action, sustainable farming, and community environmental initiatives. How can I assist you today?",
            "Thanks for reaching out! I analyze real-time environmental data to provide actionable insights. What would you like to know more about?",
            "Excellent! I can help you understand climate patterns, optimize farming practices, or find community action opportunities. What interests you most?"
        ]
    
    # Return a random response from the appropriate category
    import random
    return random.choice(responses)

