from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import uuid

from database import get_db
from models import Appointment, EmailLog, EmailTemplate, EmailPreference
from email_services import get_email_service, EmailMessage
from email_scheduler import get_email_scheduler
from ai_content_generator import get_ai_content_generator, AppointmentContext
from treatment_data import TREATMENT_TYPES

router = APIRouter()

@router.get("/health")
async def email_system_health():
    """Check health of email system components"""
    try:
        email_service = get_email_service()
        email_scheduler = get_email_scheduler()
        ai_generator = get_ai_content_generator()
        
        health_status = {
            "email_service": email_service.health_check(),
            "scheduler": email_scheduler.health_check(),
            "ai_generator": {
                "configured": ai_generator.is_configured(),
                "service": "GROQ Llama3"
            }
        }
        
        return health_status
        
    except Exception as e:
        logging.error(f"Error checking email system health: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check email system health")

@router.get("/logs")
async def get_email_logs(
    appointment_id: Optional[int] = Query(None, description="Filter by appointment ID"),
    email_type: Optional[str] = Query(None, description="Filter by email type (reminder/followup)"),
    status: Optional[str] = Query(None, description="Filter by status (sent/failed/delivered/opened)"),
    limit: int = Query(50, description="Number of logs to return"),
    db: Session = Depends(get_db)
):
    """Get email logs with optional filters"""
    try:
        query = db.query(EmailLog)
        
        if appointment_id:
            query = query.filter(EmailLog.appointment_id == appointment_id)
        
        if email_type:
            query = query.filter(EmailLog.email_type == email_type)
        
        if status:
            query = query.filter(EmailLog.status == status)
        
        logs = query.order_by(EmailLog.sent_at.desc()).limit(limit).all()
        
        return [{
            "id": log.id, 
            "appointment_id": log.appointment_id, 
            "email_type": log.email_type, 
            "subject": log.subject, 
            "to_email": log.to_email, 
            "to_name": log.to_name, 
            "status": log.status, 
            "error_message": log.error_message, 
            "message_id": log.message_id, 
            "sent_at": log.sent_at.isoformat() if log.sent_at else None, 
            "delivered_at": log.delivered_at.isoformat() if log.delivered_at else None, 
            "opened_at": log.opened_at.isoformat() if log.opened_at else None
        } for log in logs]
        
    except Exception as e:
        logging.error(f"Error getting email logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve email logs")

@router.post("/send-test")
async def send_test_email(
    to_email: str,
    to_name: str,
    email_type: str = "reminder",  # reminder or followup
    appointment_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Send a test email"""
    try:
        email_service = get_email_service()
        ai_generator = get_ai_content_generator()
        
        # Create test appointment context
        if appointment_id:
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            if not appointment:
                raise HTTPException(status_code=404, detail="Appointment not found")
            
            treatment_info = TREATMENT_TYPES.get(appointment.treatment_type, {})
            context = AppointmentContext(
                patient_name=appointment.patient_name,
                patient_email=appointment.patient_email,
                patient_phone=appointment.patient_phone,
                treatment_type=appointment.treatment_type,
                appointment_date=appointment.appointment_date,
                appointment_time=appointment.appointment_time,
                duration=treatment_info.get('duration', 60),
                price=treatment_info.get('price', 0),
                notes=appointment.notes,
                admin_notes=getattr(appointment, 'admin_notes', None),
                status=appointment.status
            )
        else:
            # Create dummy context for testing
            context = AppointmentContext(
                patient_name=to_name,
                patient_email=to_email,
                patient_phone="(555) 123-4567",
                treatment_type="cleaning",
                appointment_date="2024-01-15",  
                appointment_time="10:00",
                duration=60,
                price=120.0,
                notes="Test appointment for email preview",
                admin_notes="Test admin notes - patient prefers morning appointments",
                status="confirmed"
            )
        
        # Generate email content
        if email_type == "reminder":
            email_content = ai_generator.generate_reminder_email(context)
        else:
            email_content = ai_generator.generate_followup_email(context)
        
        # Create email message
        email_message = EmailMessage(
            to_email=to_email,
            to_name=to_name,
            subject=f"[TEST] {email_content['subject']}",
            html_content=email_content['html_content'],
            plain_text_content=email_content['plain_text_content']
        )
        
        # Send email with database session for dynamic clinic settings
        result = email_service.send_email(email_message, db=db)
        
        return {
            "success": result['success'],
            "message_id": result.get('message_id'),
            "error": result.get('error'),
            "email_type": email_type,
            "subject": email_content['subject']
        }
        
    except Exception as e:
        logging.error(f"Error sending test email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send test email")

@router.get("/stats")
async def get_email_stats(
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get email statistics"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get email counts by type and status
        reminder_sent = db.query(EmailLog).filter(
            EmailLog.email_type == 'reminder',
            EmailLog.status == 'sent',
            EmailLog.sent_at >= cutoff_date
        ).count()
        
        reminder_failed = db.query(EmailLog).filter(
            EmailLog.email_type == 'reminder',
            EmailLog.status == 'failed',
            EmailLog.sent_at >= cutoff_date
        ).count()
        
        followup_sent = db.query(EmailLog).filter(
            EmailLog.email_type == 'followup',
            EmailLog.status == 'sent',
            EmailLog.sent_at >= cutoff_date
        ).count()
        
        followup_failed = db.query(EmailLog).filter(
            EmailLog.email_type == 'followup',
            EmailLog.status == 'failed',
            EmailLog.sent_at >= cutoff_date
        ).count()
        
        total_sent = reminder_sent + followup_sent
        total_failed = reminder_failed + followup_failed
        
        return {
            "period_days": days,
            "reminder_emails": {
                "sent": reminder_sent,
                "failed": reminder_failed,
                "success_rate": (reminder_sent / (reminder_sent + reminder_failed)) * 100 if (reminder_sent + reminder_failed) > 0 else 0
            },
            "followup_emails": {
                "sent": followup_sent,
                "failed": followup_failed,
                "success_rate": (followup_sent / (followup_sent + followup_failed)) * 100 if (followup_sent + followup_failed) > 0 else 0
            },
            "total": {
                "sent": total_sent,
                "failed": total_failed,
                "success_rate": (total_sent / (total_sent + total_failed)) * 100 if (total_sent + total_failed) > 0 else 0
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting email stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve email statistics")

@router.post("/preview")
async def preview_email(
    appointment_id: int,
    email_type: str = "reminder",  # reminder or followup
    db: Session = Depends(get_db)
):
    """Preview email content without sending"""
    try:
        ai_generator = get_ai_content_generator()
        
        # Get appointment data
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Create appointment context with all data
        treatment_info = TREATMENT_TYPES.get(appointment.treatment_type, {})
        context = AppointmentContext(
            patient_name=appointment.patient_name,
            patient_email=appointment.patient_email,
            patient_phone=appointment.patient_phone,
            treatment_type=appointment.treatment_type,
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            duration=treatment_info.get('duration', 60),
            price=treatment_info.get('price', 0),
            notes=appointment.notes,
            admin_notes=getattr(appointment, 'admin_notes', None),
            status=appointment.status
        )
        
        # Generate email content
        if email_type == "reminder":
            email_content = ai_generator.generate_reminder_email(context)
        else:
            email_content = ai_generator.generate_followup_email(context)
        
        return {
            "appointment_id": appointment_id,
            "email_type": email_type,
            "patient_name": appointment.patient_name,
            "patient_email": appointment.patient_email,
            "treatment": treatment_info.get('name', appointment.treatment_type),
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time,
            "subject": email_content['subject'],
            "html_content": email_content['html_content'],
            "plain_text_content": email_content['plain_text_content'],
            "context_used": {
                "patient_notes": appointment.notes,
                "admin_notes": getattr(appointment, 'admin_notes', None),
                "status": appointment.status
            }
        }
        
    except Exception as e:
        logging.error(f"Error previewing email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to preview email")

@router.post("/appointments/{appointment_id}/send-reminder")
async def send_manual_reminder(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Send manual reminder email for an appointment"""
    try:
        email_scheduler = get_email_scheduler()
        
        # Verify appointment exists
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Send reminder email immediately
        email_scheduler._send_reminder_email(appointment_id)
        
        return {
            "success": True,
            "message": f"Reminder email sent for appointment {appointment_id}",
            "appointment_id": appointment_id,
            "patient_email": appointment.patient_email
        }
        
    except Exception as e:
        logging.error(f"Error sending manual reminder: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send reminder email")

@router.post("/appointments/{appointment_id}/send-followup")
async def send_manual_followup(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Send manual follow-up email for an appointment"""
    try:
        email_scheduler = get_email_scheduler()
        
        # Verify appointment exists
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Send follow-up email immediately
        email_scheduler._send_followup_email(appointment_id)
        
        return {
            "success": True,
            "message": f"Follow-up email sent for appointment {appointment_id}",
            "appointment_id": appointment_id,
            "patient_email": appointment.patient_email
        }
        
    except Exception as e:
        logging.error(f"Error sending manual follow-up: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send follow-up email")

@router.get("/templates")
async def get_email_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    db: Session = Depends(get_db)
):
    """Get email templates"""
    try:
        query = db.query(EmailTemplate).filter(EmailTemplate.is_active == True)
        
        if template_type:
            query = query.filter(EmailTemplate.template_type == template_type)
        
        templates = query.order_by(EmailTemplate.created_at.desc()).all()
        
        return [{
            "id": template.id,
            "name": template.name,
            "template_type": template.template_type,
            "subject_template": template.subject_template,
            "html_template": template.html_template,
            "plain_text_template": template.plain_text_template,
            "created_at": template.created_at.isoformat() if template.created_at else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None
        } for template in templates]
        
    except Exception as e:
        logging.error(f"Error getting email templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve email templates")

@router.post("/templates")
async def create_email_template(
    name: str,
    template_type: str,
    subject_template: str,
    html_template: str,
    plain_text_template: str,
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    try:
        # Check if template name already exists
        existing = db.query(EmailTemplate).filter(EmailTemplate.name == name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Template name already exists")
        
        template = EmailTemplate(
            name=name,
            template_type=template_type,
            subject_template=subject_template,
            html_template=html_template,
            plain_text_template=plain_text_template
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "id": template.id,
            "name": template.name,
            "template_type": template.template_type,
            "message": "Template created successfully"
        }
        
    except Exception as e:
        logging.error(f"Error creating email template: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create email template")