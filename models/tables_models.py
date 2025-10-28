from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Todo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

class FormResponse(Base):
    __tablename__ = 'form_responses'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    location = Column(String, nullable=False)  # District / City / Village
    area_type = Column(String, nullable=False)  # Plain / Hilly / River-side / Dry
    soil_type = Column(String, nullable=False)  # Loamy / Sandy / Clay / Don’t know
    water_source = Column(String, nullable=False)  # Rain-fed / Tube well / Canal / River
    irrigation = Column(String, nullable=False)  # Yes / No / Sometimes
    temperature = Column(String, nullable=False)  # Cold / Moderate / Hot
    rainfall = Column(String, nullable=False)  # Low / Medium / High
    sunlight = Column(String, nullable=False)  # Few / Moderate / Long hours
    land_size = Column(String, nullable=False)  # in acres or hectares (free text)
    goal = Column(String, nullable=False)  # Profit / Climate-safe / Organic / Experiment
    crop_duration = Column(String, nullable=False)  # 2–3 months / 6–12 months
    specific_crop = Column(String, nullable=True)  # optional
    fertilizers_preference = Column(String, nullable=True)  # Use fertilizers or prefer organic methods
    last_planted_at = Column(String, nullable=True)  # free text/date string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)