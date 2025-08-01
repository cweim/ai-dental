from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentCreate(BaseModel):
    patient_name: str
    patient_email: str
    patient_phone: str
    appointment_date: str
    appointment_time: str
    treatment_type: str
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    patient_email: str
    patient_phone: str
    appointment_date: str
    appointment_time: str
    treatment_type: str
    notes: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TreatmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int
    price: float

class TreatmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    duration: int
    price: float
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatbotQACreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None

class ChatbotQAResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AppointmentBooking(BaseModel):
    name: str
    email: str
    phone: str
    date: str
    time: str
    treatment: str
    notes: Optional[str] = None

class AppointmentCancellation(BaseModel):
    cancellation_reason: str