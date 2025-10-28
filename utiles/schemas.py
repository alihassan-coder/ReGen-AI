from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_active: bool

class FormCreate(BaseModel):
    # user_id will be injected server-side from auth context
    location: str
    area_type: str
    soil_type: str
    water_source: str
    irrigation: str
    temperature: str
    rainfall: str
    sunlight: str
    land_size: str
    goal: str
    crop_duration: str
    specific_crop: Optional[str] = None
    fertilizers_preference: Optional[str] = None
    last_planted_at: Optional[str] = None

class FormUpdate(BaseModel):
    location: Optional[str] = None
    area_type: Optional[str] = None
    soil_type: Optional[str] = None
    water_source: Optional[str] = None
    irrigation: Optional[str] = None
    temperature: Optional[str] = None
    rainfall: Optional[str] = None
    sunlight: Optional[str] = None
    land_size: Optional[str] = None
    goal: Optional[str] = None
    crop_duration: Optional[str] = None
    specific_crop: Optional[str] = None
    fertilizers_preference: Optional[str] = None
    last_planted_at: Optional[str] = None

class FormResponseSchema(BaseModel):
    id: int
    user_id: int
    location: str
    area_type: str
    soil_type: str
    water_source: str
    irrigation: str
    temperature: str
    rainfall: str
    sunlight: str
    land_size: str
    goal: str
    crop_duration: str
    specific_crop: Optional[str] = None
    fertilizers_preference: Optional[str] = None
    last_planted_at: Optional[str] = None

    class Config:
        from_attributes = True

# Chat Schemas
class MessageCreate(BaseModel):
    conversation_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: str
    conversation_type: Optional[str] = None

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    conversation_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None
    unread_count: int = 0

    class Config:
        from_attributes = True

class ConversationWithMessages(BaseModel):
    id: int
    user_id: int
    title: str
    conversation_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True