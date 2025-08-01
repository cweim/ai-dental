from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Treatment(Base):
    __tablename__ = "treatments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    duration = Column(Integer)  # in minutes
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    patient_email = Column(String, index=True)
    patient_phone = Column(String)
    appointment_date = Column(String)  # Store as string for now, can be converted to Date later
    appointment_time = Column(String)
    treatment_type = Column(String)
    notes = Column(Text)
    admin_notes = Column(Text)  # Admin notes for internal use
    status = Column(String, default="confirmed")  # confirmed, completed, cancelled
    cancellation_reason = Column(Text)  # Patient's reason for cancellation
    cancelled_at = Column(DateTime(timezone=True))  # When the appointment was cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatbotQA(Base):
    __tablename__ = "chatbot_qa"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, index=True)
    answer = Column(Text)
    category = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class EmailLog(Base):
    """Email log table for tracking sent emails"""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    email_type = Column(String, nullable=False)  # 'reminder' or 'followup'
    subject = Column(String, nullable=False)
    to_email = Column(String, nullable=False)
    to_name = Column(String)
    status = Column(String, nullable=False)  # 'sent', 'failed', 'delivered', 'opened'
    error_message = Column(Text)
    message_id = Column(String)  # External service message ID
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    
class EmailTemplate(Base):
    """Email template table for storing reusable templates"""
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    template_type = Column(String, nullable=False)  # 'reminder' or 'followup'
    subject_template = Column(String, nullable=False)
    html_template = Column(Text, nullable=False)
    plain_text_template = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
class EmailPreference(Base):
    """Email preferences for patients"""
    __tablename__ = "email_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    reminder_emails = Column(Boolean, default=True)
    followup_emails = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=True)
    unsubscribe_token = Column(String, unique=True)
    unsubscribed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class KnowledgeBase(Base):
    """Knowledge base entries with embeddings for vector search"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False, index=True)
    answer = Column(Text, nullable=False)
    category = Column(String, index=True)
    source = Column(String)  # 'user_defined', 'dental_corpus', 'external'
    source_url = Column(String)  # Reference URL if applicable
    embedding_vector = Column(Text)  # JSON serialized embedding vector
    embedding_model = Column(String, default='basic-text-similarity')
    confidence_threshold = Column(Float, default=0.7)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatSession(Base):
    """Chat sessions for tracking conversations"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)  # Anonymous user tracking
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    message_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    """Individual chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('chat_sessions.session_id'), nullable=False)
    message_type = Column(String, nullable=False)  # 'user', 'bot'
    content = Column(Text, nullable=False)
    sources = Column(Text)  # JSON array of source references
    confidence_score = Column(Float)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class VectorSearchLog(Base):
    """Log vector search queries and results"""
    __tablename__ = "vector_search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('chat_sessions.session_id'))
    query = Column(Text, nullable=False)
    top_k = Column(Integer, default=5)
    similarity_scores = Column(Text)  # JSON array of similarity scores
    matched_kb_ids = Column(Text)  # JSON array of matched knowledge base IDs
    search_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ClinicSetting(Base):
    """Clinic settings for email generation and general practice info"""
    __tablename__ = "clinic_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String, nullable=False, default='text')  # text, email, phone, url, textarea
    display_name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False, default='general')  # general, contact, email, review
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())