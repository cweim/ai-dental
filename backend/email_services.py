import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent
from sqlalchemy.orm import Session

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class EmailMessage:
    """Email message data class"""
    to_email: str
    to_name: str
    subject: str
    html_content: str
    plain_text_content: str
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    cc_emails: Optional[List[str]] = None
    bcc_emails: Optional[List[str]] = None
    reply_to: Optional[str] = None

class EmailServiceBase(ABC):
    """Base class for email services"""
    
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the email service is properly configured"""
        pass
    
    @abstractmethod
    def send_email(self, message: EmailMessage, db: Session = None) -> Dict:
        """Send an email message"""
        pass
    
    def health_check(self) -> Dict:
        """Check the health of the email service"""
        return {
            "configured": self.is_configured(),
            "service_type": self.__class__.__name__
        }

class SendGridService(EmailServiceBase):
    """SendGrid email service implementation"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.fallback_from_email = os.getenv('SENDGRID_FROM_EMAIL')
        self.fallback_from_name = os.getenv('SENDGRID_FROM_NAME', 'AI Dentist')
        
        if not self.api_key:
            logger.warning("SendGrid API key not found in environment variables")
        
        if self.api_key:
            self.client = SendGridAPIClient(api_key=self.api_key)
        else:
            self.client = None
    
    def is_configured(self) -> bool:
        """Check if SendGrid is properly configured"""
        return self.api_key is not None and self.fallback_from_email is not None
    
    def send_email(self, message: EmailMessage, db: Session = None) -> Dict:
        """Send email using SendGrid"""
        if not self.is_configured():
            logger.error("SendGrid not configured")
            return {"success": False, "error": "SendGrid not configured"}
        
        try:
            # Get dynamic clinic email and name if database session provided
            from_email = message.from_email
            from_name = message.from_name
            
            if db and not from_email:
                from clinic_settings_endpoints import get_all_settings_dict
                clinic_settings = get_all_settings_dict(db)
                from_email = clinic_settings.get('clinic_email', self.fallback_from_email)
                from_name = clinic_settings.get('clinic_name', self.fallback_from_name)
            
            # Fallback to environment variables if still not set
            if not from_email:
                from_email = self.fallback_from_email
            if not from_name:
                from_name = self.fallback_from_name
            
            # Create mail object
            mail = Mail(
                from_email=From(from_email, from_name),
                to_emails=To(message.to_email, message.to_name),
                subject=Subject(message.subject),
                html_content=HtmlContent(message.html_content),
                plain_text_content=PlainTextContent(message.plain_text_content)
            )
            
            # Add CC emails if provided
            if message.cc_emails:
                for cc_email in message.cc_emails:
                    mail.add_cc(cc_email)
            
            # Add BCC emails if provided
            if message.bcc_emails:
                for bcc_email in message.bcc_emails:
                    mail.add_bcc(bcc_email)
            
            # Add reply-to if provided
            if message.reply_to:
                mail.reply_to = message.reply_to
            
            # Send email
            response = self.client.send(mail)
            
            success = response.status_code in [200, 201, 202]
            
            if success:
                logger.info(f"Email sent successfully to {message.to_email}")
                return {
                    "success": True,
                    "message_id": response.headers.get('X-Message-Id'),
                    "status_code": response.status_code
                }
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.body}")
                return {
                    "success": False,
                    "error": f"SendGrid error: {response.status_code}",
                    "details": response.body
                }
                
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_delivery_status(self, message_id: str) -> Dict:
        """Get delivery status for a message (requires SendGrid Event Webhook)"""
        # This would typically require webhook setup for real-time status
        # For now, we'll return a placeholder
        return {"status": "unknown", "message": "Status tracking requires webhook setup"}

class EmailServiceManager:
    """Manager class to handle email services"""
    
    def __init__(self):
        self.services = {
            "sendgrid": SendGridService()
        }
        
        # Determine primary service based on configuration
        self.primary_service = self._get_primary_service()
        
        logger.info(f"Email service manager initialized with primary service: {self.primary_service}")
    
    def _get_primary_service(self) -> str:
        """Determine which email service to use as primary"""
        preferred_service = os.getenv('EMAIL_SERVICE', 'sendgrid').lower()
        
        if preferred_service in self.services and self.services[preferred_service].is_configured():
            return preferred_service
        
        # Fallback to any configured service
        for service_name, service in self.services.items():
            if service.is_configured():
                logger.info(f"Using {service_name} as fallback email service")
                return service_name
        
        logger.warning("No email service is properly configured")
        return "sendgrid"  # Default fallback
    
    def send_email(self, message: EmailMessage, service_name: str = None, db: Session = None) -> Dict:
        """Send email using specified service or primary service"""
        service_name = service_name or self.primary_service
        
        if service_name not in self.services:
            return {"success": False, "error": f"Unknown email service: {service_name}"}
        
        service = self.services[service_name]
        
        if not service.is_configured():
            return {"success": False, "error": "No configured email service available"}
        
        # Pass database session to service if it supports dynamic settings
        if hasattr(service, 'send_email') and 'db' in service.send_email.__code__.co_varnames:
            return service.send_email(message, db)
        else:
            return service.send_email(message)
    
    def get_available_services(self) -> List[str]:
        """Get list of available and configured email services"""
        return [name for name, service in self.services.items() if service.is_configured()]
    
    def health_check(self) -> Dict:
        """Check health of all email services"""
        status = {}
        
        for service_name, service in self.services.items():
            status[service_name] = {
                "configured": service.is_configured(),
                "is_primary": service_name == self.primary_service
            }
        
        return {
            "services": status,
            "primary_service": self.primary_service,
            "available_services": self.get_available_services()
        }

# Global email service manager instance
email_manager = EmailServiceManager()

def get_email_service() -> EmailServiceManager:
    """Get the global email service manager instance"""
    return email_manager