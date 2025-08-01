from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List
import logging

from database import get_db
from models import User, Treatment, Appointment, ChatbotQA
from schemas import (
    AppointmentCreate, AppointmentResponse,
    TreatmentCreate, TreatmentResponse,
    ChatbotQACreate, ChatbotQAResponse,
    AppointmentBooking, AppointmentCancellation
)
from treatment_data import TREATMENT_TYPES, AVAILABLE_TIME_SLOTS
from exceptions import (
    AIDentistException, handle_exception, ValidationException,
    AppointmentException, DatabaseException, ExceptionHandler
)

load_dotenv()

app = FastAPI(title="AI Dentist API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Global exception handler
@app.exception_handler(AIDentistException)
async def ai_dentist_exception_handler(request: Request, exc: AIDentistException):
    """Handle custom AI Dentist exceptions"""
    http_exc = handle_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions"""
    http_exc = handle_exception(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )

@app.on_event("startup")
async def startup_event():
    """Initialize services on app startup"""
    from email_scheduler import get_email_scheduler
    from vector_search import get_vector_search_engine
    from database import get_db
    
    # Initialize email scheduler
    scheduler = get_email_scheduler()
    if scheduler.scheduler:
        scheduler.start()
        logging.info("Email scheduler started successfully")
    
    # Initialize vector search index
    try:
        vector_search = get_vector_search_engine()
        db = next(get_db())
        success = vector_search.initialize_index(db)
        if success:
            logging.info("Vector search index initialized successfully on startup")
        else:
            logging.error("Failed to initialize vector search index on startup")
        db.close()
    except Exception as e:
        logging.error(f"Error initializing vector search on startup: {e}")

@app.get("/")
async def root():
    return {"message": "AI Dentist API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    with ExceptionHandler("create_appointment"):
        try:
            # Validate treatment type
            if appointment.treatment_type not in TREATMENT_TYPES:
                raise ValidationException(
                    f"Invalid treatment type: {appointment.treatment_type}",
                    details={"valid_types": list(TREATMENT_TYPES.keys())}
                )
            
            db_appointment = Appointment(
                patient_name=appointment.patient_name,
                patient_email=appointment.patient_email,
                patient_phone=appointment.patient_phone,
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                treatment_type=appointment.treatment_type,
                notes=appointment.notes
            )
            db.add(db_appointment)
            db.commit()
            db.refresh(db_appointment)
            return db_appointment
            
        except Exception as e:
            if not isinstance(e, AIDentistException):
                raise DatabaseException(f"Failed to create appointment: {str(e)}")
            raise

@app.get("/appointments")
async def get_appointments(db: Session = Depends(get_db)):
    with ExceptionHandler("get_appointments"):
        try:
            appointments = db.query(Appointment).all()
            return appointments
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve appointments: {str(e)}")

@app.post("/treatments", response_model=TreatmentResponse)
async def create_treatment(
    treatment: TreatmentCreate,
    db: Session = Depends(get_db)
):
    db_treatment = Treatment(
        name=treatment.name,
        description=treatment.description,
        duration=treatment.duration,
        price=treatment.price
    )
    db.add(db_treatment)
    db.commit()
    db.refresh(db_treatment)
    return db_treatment

@app.get("/treatments")
async def get_treatments(db: Session = Depends(get_db)):
    treatments = db.query(Treatment).all()
    return treatments


@app.get("/treatments/types")
async def get_treatment_types():
    return TREATMENT_TYPES

@app.get("/appointments/available-slots")
async def get_available_slots(date: str, treatment: str, db: Session = Depends(get_db)):
    """Get available time slots for a specific date and treatment type"""
    with ExceptionHandler("get_available_slots"):
        try:
            # Validate treatment type
            if treatment not in TREATMENT_TYPES:
                raise ValidationException(
                    f"Invalid treatment type: {treatment}",
                    details={"valid_types": list(TREATMENT_TYPES.keys())}
                )
            
            # Parse date to validate format
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValidationException("Invalid date format. Use YYYY-MM-DD")
            
            # Get treatment duration
            treatment_duration = TREATMENT_TYPES[treatment]['duration']
            
            # Get existing appointments for the date
            existing_appointments = db.query(Appointment).filter(
                Appointment.appointment_date == date,
                Appointment.status.in_(['confirmed', 'completed'])  # Don't block cancelled appointments
            ).all()
            
            # Create set of blocked time slots
            blocked_slots = set()
            
            for appointment in existing_appointments:
                try:
                    # Parse appointment time
                    appointment_time = datetime.strptime(appointment.appointment_time, "%H:%M")
                    
                    # Get appointment duration
                    appt_treatment_duration = TREATMENT_TYPES.get(appointment.treatment_type, {}).get('duration', 30)
                    
                    # Block all 30-minute slots that overlap with this appointment
                    current_time = appointment_time
                    end_time = appointment_time + timedelta(minutes=appt_treatment_duration)
                    
                    while current_time < end_time:
                        blocked_slots.add(current_time.strftime('%H:%M'))
                        current_time += timedelta(minutes=30)
                        
                except ValueError:
                    # Skip invalid time formats
                    continue
            
            # Filter available slots based on treatment duration and blocked slots
            available_slots = []
            
            for slot in AVAILABLE_TIME_SLOTS:
                try:
                    slot_time = datetime.strptime(slot, '%H:%M')
                    end_slot_time = slot_time + timedelta(minutes=treatment_duration)
                    
                    # Check if the entire appointment duration is available
                    is_available = True
                    check_time = slot_time
                    
                    while check_time < end_slot_time:
                        if check_time.strftime('%H:%M') in blocked_slots:
                            is_available = False
                            break
                        check_time += timedelta(minutes=30)
                    
                    # Also check if we have enough time slots available
                    # (e.g., don't book a 90-minute appointment at 17:00 if we close at 18:00)
                    last_slot_needed = (slot_time + timedelta(minutes=treatment_duration - 30)).strftime('%H:%M')
                    if last_slot_needed not in AVAILABLE_TIME_SLOTS:
                        is_available = False
                    
                    if is_available:
                        available_slots.append(slot)
                        
                except ValueError:
                    # Skip invalid slot formats
                    continue
            
            return {"available_slots": available_slots}
            
        except ValidationException:
            raise
        except Exception as e:
            logging.error(f"Error getting available slots: {e}")
            # Return default slots if service fails gracefully
            return {"available_slots": AVAILABLE_TIME_SLOTS}

@app.post("/appointments/book")
async def book_appointment(booking: AppointmentBooking, db: Session = Depends(get_db)):
    try:
        # Validate treatment type
        if booking.treatment not in TREATMENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid treatment type")
        
        treatment_info = TREATMENT_TYPES[booking.treatment]
        
        # Parse date and time
        appointment_date = datetime.strptime(booking.date, "%Y-%m-%d")
        appointment_time = datetime.strptime(booking.time, "%H:%M")
        
        # Combine date and time
        start_datetime = appointment_date.replace(
            hour=appointment_time.hour,
            minute=appointment_time.minute,
            second=0,
            microsecond=0
        )
        end_datetime = start_datetime + timedelta(minutes=treatment_info["duration"])
        
        # Save to database
        db_appointment = Appointment(
            patient_name=booking.name,
            patient_email=booking.email,
            patient_phone=booking.phone,
            appointment_date=booking.date,
            appointment_time=booking.time,
            treatment_type=booking.treatment,
            notes=booking.notes,
            status="confirmed"
        )
        
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        
        # Schedule automated emails
        from email_scheduler import get_email_scheduler
        email_scheduler = get_email_scheduler()
        email_results = email_scheduler.schedule_appointment_emails(db_appointment.id)
        
        return {
            "message": "Appointment booked successfully!",
            "appointment_id": db_appointment.id,
            "treatment": treatment_info['name'],
            "date": booking.date,
            "time": booking.time,
            "price": treatment_info['price'],
            "duration": treatment_info['duration'],
            "emails_scheduled": email_results
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
    except Exception as e:
        logging.error(f"Error booking appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to book appointment")

@app.post("/chat")
async def chat_with_ai(message: dict):
    # TODO: Implement OpenAI integration
    return {"response": "AI response coming soon!"}

@app.get("/appointments/find")
async def find_appointments_by_email(
    email: str,
    name: str = None,
    db: Session = Depends(get_db)
):
    """Find upcoming appointments by email and optionally name"""
    with ExceptionHandler("find_appointments"):
        try:
            from datetime import datetime, date
            today = date.today().strftime("%Y-%m-%d")
            
            query = db.query(Appointment).filter(
                Appointment.patient_email == email,
                Appointment.appointment_date >= today,
                Appointment.status.in_(['confirmed', 'completed'])  # Not cancelled
            )
            
            if name:
                query = query.filter(Appointment.patient_name.ilike(f"%{name}%"))
            
            appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).all()
            
            return [{
                "id": apt.id,
                "patient_name": apt.patient_name,
                "patient_email": apt.patient_email,
                "patient_phone": apt.patient_phone,
                "appointment_date": apt.appointment_date,
                "appointment_time": apt.appointment_time,
                "treatment_type": apt.treatment_type,
                "notes": apt.notes,
                "status": apt.status,
                "created_at": apt.created_at.isoformat() if apt.created_at else None
            } for apt in appointments]
            
        except Exception as e:
            raise DatabaseException(f"Failed to find appointments: {str(e)}")

@app.post("/appointments/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    cancellation_data: AppointmentCancellation,
    db: Session = Depends(get_db)
):
    """Cancel an appointment with reason"""
    with ExceptionHandler("cancel_appointment"):
        try:
            from datetime import datetime
            from email_scheduler import get_email_scheduler
            
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                raise ValidationException("Appointment not found")
            
            if appointment.status == "cancelled":
                raise ValidationException("Appointment is already cancelled")
            
            # Update appointment status
            appointment.status = "cancelled"
            appointment.cancellation_reason = cancellation_data.cancellation_reason
            appointment.cancelled_at = datetime.utcnow()
            appointment.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(appointment)
            
            # Cancel scheduled emails
            email_scheduler = get_email_scheduler()
            email_cancelled = email_scheduler.cancel_appointment_emails(appointment_id)
            
            return {
                "message": "Appointment cancelled successfully",
                "appointment_id": appointment_id,
                "status": "cancelled",
                "cancellation_reason": cancellation_data.cancellation_reason,
                "cancelled_at": appointment.cancelled_at.isoformat(),
                "emails_cancelled": email_cancelled
            }
            
        except ValidationException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to cancel appointment: {str(e)}")

# Include additional admin endpoints
from additional_endpoints import router as admin_router
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])

# Include email management endpoints
from email_endpoints import router as email_router
from clinic_settings_endpoints import router as clinic_settings_router
app.include_router(email_router, prefix="/api/email", tags=["email"])
app.include_router(clinic_settings_router, prefix="/api/admin/clinic", tags=["clinic-settings"])

# Include chatbot endpoints
from chatbot_endpoints import router as chatbot_router
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["chatbot"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)