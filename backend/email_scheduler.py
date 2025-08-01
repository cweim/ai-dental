import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from models import Appointment, EmailLog
from email_services import get_email_service, EmailMessage
from ai_content_generator import get_ai_content_generator, AppointmentContext
from treatment_data import TREATMENT_TYPES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailScheduler:
    """Email scheduler for automated appointment reminders and follow-ups"""
    
    def __init__(self):
        self.email_service = get_email_service()
        self.ai_generator = get_ai_content_generator()
        self.scheduler = None
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """Set up APScheduler with memory jobstore"""
        try:
            # Use memory jobstore to avoid serialization issues
            executors = {
                'default': ThreadPoolExecutor(20)
            }
            
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            self.scheduler = BackgroundScheduler(
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            # Add periodic cleanup job
            self.scheduler.add_job(
                func=self._cleanup_old_jobs,
                trigger=CronTrigger(hour=2, minute=0),  # Run at 2 AM daily
                id='cleanup_jobs',
                replace_existing=True
            )
            
            logger.info("Email scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize email scheduler: {str(e)}")
            self.scheduler = None
    
    def start(self):
        """Start the email scheduler"""
        if self.scheduler and not self.scheduler.running:
            self.scheduler.start()
            logger.info("Email scheduler started")
    
    def stop(self):
        """Stop the email scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Email scheduler stopped")
    
    def schedule_appointment_emails(self, appointment_id: int) -> Dict[str, bool]:
        """Schedule both reminder and follow-up emails for an appointment"""
        try:
            db = SessionLocal()
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found")
                return {"reminder": False, "followup": False}
            
            # Parse appointment date and time
            appointment_datetime = datetime.strptime(
                f"{appointment.appointment_date} {appointment.appointment_time}",
                "%Y-%m-%d %H:%M"
            )
            
            # Schedule reminder email (24 hours before)
            reminder_scheduled = self._schedule_reminder_email(
                appointment_id, 
                appointment_datetime - timedelta(hours=24)
            )
            
            # Schedule follow-up email (2 hours after appointment)
            followup_scheduled = self._schedule_followup_email(
                appointment_id,
                appointment_datetime + timedelta(hours=2)
            )
            
            db.close()
            
            return {
                "reminder": reminder_scheduled,
                "followup": followup_scheduled
            }
            
        except Exception as e:
            logger.error(f"Error scheduling emails for appointment {appointment_id}: {str(e)}")
            return {"reminder": False, "followup": False}
    
    def _schedule_reminder_email(self, appointment_id: int, send_time: datetime) -> bool:
        """Schedule a reminder email"""
        try:
            # Only schedule if send_time is in the future
            if send_time <= datetime.now():
                logger.warning(f"Reminder email send time {send_time} is in the past")
                return False
            
            job_id = f"reminder_{appointment_id}"
            
            self.scheduler.add_job(
                func=self._send_reminder_email,
                trigger=DateTrigger(run_date=send_time),
                args=[appointment_id],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Reminder email scheduled for appointment {appointment_id} at {send_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling reminder email: {str(e)}")
            return False
    
    def _schedule_followup_email(self, appointment_id: int, send_time: datetime) -> bool:
        """Schedule a follow-up email"""
        try:
            job_id = f"followup_{appointment_id}"
            
            self.scheduler.add_job(
                func=self._send_followup_email,
                trigger=DateTrigger(run_date=send_time),
                args=[appointment_id],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Follow-up email scheduled for appointment {appointment_id} at {send_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling follow-up email: {str(e)}")
            return False
    
    def _send_reminder_email(self, appointment_id: int):
        """Send a reminder email for an appointment"""
        try:
            db = SessionLocal()
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found for reminder email")
                return
            
            # Check if appointment is still active
            if appointment.status in ['cancelled', 'completed']:
                logger.info(f"Skipping reminder email for {appointment.status} appointment {appointment_id}")
                return
            
            # Create appointment context
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
            email_content = self.ai_generator.generate_reminder_email(context)
            
            # Create email message
            email_message = EmailMessage(
                to_email=appointment.patient_email,
                to_name=appointment.patient_name,
                subject=email_content['subject'],
                html_content=email_content['html_content'],
                plain_text_content=email_content['plain_text_content']
            )
            
            # Send email with database session for dynamic clinic settings
            result = self.email_service.send_email(email_message, db=db)
            
            # Log email
            self._log_email(
                db, appointment_id, 'reminder', 
                email_message.subject, email_message.to_email, email_message.to_name, result
            )
            
            db.close()
            
            if result['success']:
                logger.info(f"Reminder email sent successfully for appointment {appointment_id}")
            else:
                logger.error(f"Failed to send reminder email for appointment {appointment_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending reminder email for appointment {appointment_id}: {str(e)}")
    
    def _send_followup_email(self, appointment_id: int):
        """Send a follow-up email after an appointment"""
        try:
            db = SessionLocal()
            appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
            
            if not appointment:
                logger.error(f"Appointment {appointment_id} not found for follow-up email")
                return
            
            # Only send follow-up if appointment was completed
            if appointment.status != 'completed':
                # Auto-update status to completed if appointment time has passed
                appointment_datetime = datetime.strptime(
                    f"{appointment.appointment_date} {appointment.appointment_time}",
                    "%Y-%m-%d %H:%M"
                )
                
                if datetime.now() > appointment_datetime + timedelta(hours=2):
                    appointment.status = 'completed'
                    db.commit()
                    logger.info(f"Auto-updated appointment {appointment_id} status to completed")
                else:
                    logger.info(f"Skipping follow-up email for non-completed appointment {appointment_id}")
                    return
            
            # Create appointment context
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
            email_content = self.ai_generator.generate_followup_email(context)
            
            # Create email message
            email_message = EmailMessage(
                to_email=appointment.patient_email,
                to_name=appointment.patient_name,
                subject=email_content['subject'],
                html_content=email_content['html_content'],
                plain_text_content=email_content['plain_text_content']
            )
            
            # Send email with database session for dynamic clinic settings
            result = self.email_service.send_email(email_message, db=db)
            
            # Log email
            self._log_email(
                db, appointment_id, 'followup', 
                email_message.subject, email_message.to_email, email_message.to_name, result
            )
            
            db.close()
            
            if result['success']:
                logger.info(f"Follow-up email sent successfully for appointment {appointment_id}")
            else:
                logger.error(f"Failed to send follow-up email for appointment {appointment_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Error sending follow-up email for appointment {appointment_id}: {str(e)}")
    
    def _log_email(self, db: Session, appointment_id: int, email_type: str, subject: str, to_email: str, to_name: str, result: Dict):
        """Log email sending attempt"""
        try:
            email_log = EmailLog(
                appointment_id=appointment_id,
                email_type=email_type,
                subject=subject,
                to_email=to_email,
                to_name=to_name,
                status='sent' if result['success'] else 'failed',
                error_message=result.get('error'),
                message_id=result.get('message_id'),
                sent_at=datetime.now()
            )
            
            db.add(email_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging email: {str(e)}")
    
    def _cleanup_old_jobs(self):
        """Clean up old completed jobs"""
        try:
            # Remove jobs older than 7 days
            cutoff_date = datetime.now() - timedelta(days=7)
            
            jobs = self.scheduler.get_jobs()
            removed_count = 0
            
            for job in jobs:
                if job.next_run_time and job.next_run_time < cutoff_date:
                    self.scheduler.remove_job(job.id)
                    removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old scheduled jobs")
            
        except Exception as e:
            logger.error(f"Error cleaning up old jobs: {str(e)}")
    
    def cancel_appointment_emails(self, appointment_id: int) -> bool:
        """Cancel scheduled emails for an appointment"""
        try:
            reminder_job_id = f"reminder_{appointment_id}"
            followup_job_id = f"followup_{appointment_id}"
            
            cancelled_count = 0
            
            # Cancel reminder email
            try:
                self.scheduler.remove_job(reminder_job_id)
                cancelled_count += 1
                logger.info(f"Cancelled reminder email for appointment {appointment_id}")
            except:
                pass  # Job might not exist or already completed
            
            # Cancel follow-up email
            try:
                self.scheduler.remove_job(followup_job_id)
                cancelled_count += 1
                logger.info(f"Cancelled follow-up email for appointment {appointment_id}")
            except:
                pass  # Job might not exist or already completed
            
            return cancelled_count > 0
            
        except Exception as e:
            logger.error(f"Error cancelling emails for appointment {appointment_id}: {str(e)}")
            return False
    
    def get_scheduled_jobs(self) -> List[Dict]:
        """Get list of all scheduled jobs"""
        try:
            jobs = self.scheduler.get_jobs()
            job_list = []
            
            for job in jobs:
                job_list.append({
                    'id': job.id,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'func_name': job.func.__name__,
                    'args': job.args
                })
            
            return job_list
            
        except Exception as e:
            logger.error(f"Error getting scheduled jobs: {str(e)}")
            return []
    
    def health_check(self) -> Dict:
        """Check scheduler health"""
        return {
            'scheduler_running': self.scheduler.running if self.scheduler else False,
            'job_count': len(self.scheduler.get_jobs()) if self.scheduler else 0,
            'email_service_available': len(self.email_service.get_available_services()) > 0,
            'ai_generator_available': self.ai_generator.is_configured()
        }

# Global email scheduler instance
email_scheduler = EmailScheduler()

def get_email_scheduler() -> EmailScheduler:
    """Get the global email scheduler instance"""
    return email_scheduler

# Note: Scheduler will be started by the FastAPI app startup event
# to avoid serialization issues during module import