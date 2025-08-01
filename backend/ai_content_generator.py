import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from groq import Groq
from treatment_data import TREATMENT_TYPES
from clinic_settings_endpoints import get_all_settings_dict
from database import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AppointmentContext:
    """Context data for generating personalized emails"""
    patient_name: str
    patient_email: str
    patient_phone: str
    treatment_type: str
    appointment_date: str
    appointment_time: str
    duration: int
    price: float
    notes: Optional[str] = None
    admin_notes: Optional[str] = None
    status: Optional[str] = "confirmed"
    doctor_name: Optional[str] = "Dr. Smith"
    clinic_name: Optional[str] = "AI Dentist Clinic"
    clinic_phone: Optional[str] = "(555) 123-4567"
    clinic_address: Optional[str] = "123 Main St, City, State 12345"

class AIContentGenerator:
    """AI-powered content generator for personalized emails"""
    
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.client = None
        
        if self.groq_api_key:
            self.client = Groq(api_key=self.groq_api_key)
            logger.info("GROQ client initialized successfully")
        else:
            logger.warning("GROQ API key not found in environment variables")
    
    def is_configured(self) -> bool:
        """Check if GROQ is properly configured"""
        return self.groq_api_key is not None and self.client is not None
    
    def generate_reminder_email(self, context: AppointmentContext) -> Dict[str, str]:
        """Generate a reminder email for appointment tomorrow"""
        if not self.is_configured():
            return self._get_fallback_reminder_email(context)
        
        try:
            # Get dynamic clinic settings
            db = SessionLocal()
            clinic_settings = get_all_settings_dict(db)
            db.close()
            
            # Get treatment details
            treatment_info = TREATMENT_TYPES.get(context.treatment_type, {})
            treatment_name = treatment_info.get('name', context.treatment_type)
            
            # Use dynamic clinic info or fallback to context defaults
            clinic_name = clinic_settings.get('clinic_name', context.clinic_name)
            doctor_name = clinic_settings.get('doctor_name', context.doctor_name)
            clinic_phone = clinic_settings.get('clinic_phone', context.clinic_phone)
            clinic_address = clinic_settings.get('clinic_address', context.clinic_address)
            business_hours = clinic_settings.get('business_hours', 'Monday-Friday: 9:00 AM - 5:30 PM')
            
            # Create prompt for GROQ
            patient_notes_section = f"\n- Patient Notes: {context.notes}" if context.notes else ""
            admin_notes_section = f"\n- Admin Notes: {context.admin_notes}" if context.admin_notes else ""
            
            prompt = f"""
Write a friendly and professional dental appointment reminder email.

Appointment Details:
- Patient: {context.patient_name}
- Email: {context.patient_email}
- Phone: {context.patient_phone}
- Treatment: {treatment_name}
- Date: {context.appointment_date}
- Time: {context.appointment_time}
- Duration: {context.duration} minutes
- Price: ${context.price:.2f}
- Doctor: {doctor_name}
- Clinic: {clinic_name}
- Phone: {clinic_phone}
- Address: {clinic_address}
- Business Hours: {business_hours}{patient_notes_section}{admin_notes_section}

The email should:
1. Be warm and professional
2. Remind them about tomorrow's appointment
3. Include preparation instructions if relevant to the treatment type
4. Mention what to bring (insurance card, ID, etc.)
5. Include contact information for changes
6. Be encouraging and reduce anxiety
7. If admin notes are present, incorporate relevant information professionally
8. If patient notes indicate specific concerns, address them reassuringly

Generate both a subject line and email body in HTML format.
Return in this format:
SUBJECT: [subject line]
BODY: [HTML email body]
"""
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a professional dental office assistant writing appointment reminder emails. Be friendly, professional, and reassuring."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            logger.info(f"GROQ reminder response: {content[:500]}...")
            return self._parse_ai_response(content)
            
        except Exception as e:
            logger.error(f"Error generating reminder email with AI: {str(e)}")
            return self._get_fallback_reminder_email(context)
    
    def generate_followup_email(self, context: AppointmentContext) -> Dict[str, str]:
        """Generate a follow-up email after appointment"""
        if not self.is_configured():
            return self._get_fallback_followup_email(context)
        
        try:
            # Get dynamic clinic settings
            db = SessionLocal()
            clinic_settings = get_all_settings_dict(db)
            db.close()
            
            # Get treatment details
            treatment_info = TREATMENT_TYPES.get(context.treatment_type, {})
            treatment_name = treatment_info.get('name', context.treatment_type)
            
            # Use dynamic clinic info or fallback to context defaults
            clinic_name = clinic_settings.get('clinic_name', context.clinic_name)
            doctor_name = clinic_settings.get('doctor_name', context.doctor_name)
            clinic_phone = clinic_settings.get('clinic_phone', context.clinic_phone)
            google_review_url = clinic_settings.get('google_review_url', 'https://g.page/r/YOUR_GOOGLE_BUSINESS_ID/review')
            
            # Create prompt for GROQ
            patient_notes_section = f"\n- Patient Notes: {context.notes}" if context.notes else ""
            admin_notes_section = f"\n- Admin Notes: {context.admin_notes}" if context.admin_notes else ""
            
            prompt = f"""
Write a professional dental follow-up email after a completed appointment.

Appointment Details:
- Patient: {context.patient_name}
- Email: {context.patient_email}
- Phone: {context.patient_phone}
- Treatment: {treatment_name}
- Date: {context.appointment_date}
- Price: ${context.price:.2f}
- Duration: {context.duration} minutes
- Doctor: {doctor_name}
- Clinic: {clinic_name}
- Phone: {clinic_phone}
- Google Review Link: {google_review_url}{patient_notes_section}{admin_notes_section}

The email should:
1. Thank them for visiting
2. Provide a brief treatment summary including the specific treatment performed
3. Include post-treatment care instructions specific to the treatment type
4. Mention medication reminders if applicable
5. Include a professional closing and clinic contact information
6. Suggest scheduling next appointment if needed (like cleanings every 6 months)
7. Contact information for questions
8. If admin notes contain follow-up instructions, include them professionally
9. Address any concerns mentioned in patient notes with care instructions
10. IMPORTANT: Include a prominent call-to-action asking them to leave a Google review using the provided Google Review Link
11. Make the Google review request warm and personal, explaining how reviews help other patients find quality dental care

Generate both a subject line and email body in HTML format.
Return in this format:
SUBJECT: [subject line]
BODY: [HTML email body]
"""
            
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a professional dental office assistant writing follow-up emails. Be caring, informative, and helpful with post-treatment care."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            logger.info(f"GROQ followup response: {content[:500]}...")
            return self._parse_ai_response(content)
            
        except Exception as e:
            logger.error(f"Error generating follow-up email with AI: {str(e)}")
            return self._get_fallback_followup_email(context)
    
    def _parse_ai_response(self, content: str) -> Dict[str, str]:
        """Parse AI response to extract subject and body"""
        try:
            lines = content.strip().split('\n')
            subject = ""
            body = ""
            
            body_started = False
            for line in lines:
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                elif line.startswith("BODY:"):
                    body_started = True
                    body = line.replace("BODY:", "").strip()
                elif body_started:
                    body += "\n" + line
            
            return {
                "subject": subject or "Appointment Reminder",
                "html_content": body or "<p>Thank you for choosing our dental service.</p>",
                "plain_text_content": self._html_to_text(body)
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return {
                "subject": "Appointment Reminder",
                "html_content": "<p>Thank you for choosing our dental service.</p>",
                "plain_text_content": "Thank you for choosing our dental service."
            }
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        import re
        # Remove HTML tags
        clean = re.compile('<.*?>')
        plain_text = re.sub(clean, '', html_content)
        # Clean up extra whitespace
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        return plain_text
    
    def _get_fallback_reminder_email(self, context: AppointmentContext) -> Dict[str, str]:
        """Fallback reminder email when AI is not available"""
        treatment_info = TREATMENT_TYPES.get(context.treatment_type, {})
        treatment_name = treatment_info.get('name', context.treatment_type)
        
        subject = f"Reminder: Your {treatment_name} appointment tomorrow"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Appointment Reminder</h2>
                
                <p>Dear {context.patient_name},</p>
                
                <p>This is a friendly reminder about your upcoming dental appointment:</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>Appointment Details:</strong><br>
                    <strong>Treatment:</strong> {treatment_name}<br>
                    <strong>Date:</strong> {context.appointment_date}<br>
                    <strong>Time:</strong> {context.appointment_time}<br>
                    <strong>Duration:</strong> {context.duration} minutes<br>
                    <strong>Doctor:</strong> {context.doctor_name}
                </div>
                
                <p><strong>Please bring:</strong></p>
                <ul>
                    <li>Photo ID</li>
                    <li>Insurance card</li>
                    <li>List of current medications</li>
                    <li>Payment method</li>
                </ul>
                
                <p>If you need to reschedule or cancel, please call us at {context.clinic_phone} at least 24 hours in advance.</p>
                
                <p>We look forward to seeing you tomorrow!</p>
                
                <p>Best regards,<br>
                <strong>{context.clinic_name}</strong><br>
                {context.clinic_address}<br>
                {context.clinic_phone}</p>
            </div>
        </body>
        </html>
        """
        
        plain_text = f"""
Appointment Reminder

Dear {context.patient_name},

This is a friendly reminder about your upcoming dental appointment:

Appointment Details:
Treatment: {treatment_name}
Date: {context.appointment_date}
Time: {context.appointment_time}
Duration: {context.duration} minutes
Doctor: {context.doctor_name}

Please bring:
- Photo ID
- Insurance card
- List of current medications
- Payment method

If you need to reschedule or cancel, please call us at {context.clinic_phone} at least 24 hours in advance.

We look forward to seeing you tomorrow!

Best regards,
{context.clinic_name}
{context.clinic_address}
{context.clinic_phone}
        """
        
        return {
            "subject": subject,
            "html_content": html_content,
            "plain_text_content": plain_text
        }
    
    def _get_fallback_followup_email(self, context: AppointmentContext) -> Dict[str, str]:
        """Fallback follow-up email when AI is not available"""
        treatment_info = TREATMENT_TYPES.get(context.treatment_type, {})
        treatment_name = treatment_info.get('name', context.treatment_type)
        
        subject = f"Thank you for your visit - {treatment_name} follow-up"
        
        # Clinic contact information
        clinic_phone = os.getenv('CLINIC_PHONE', '(555) 123-4567')
        clinic_address = os.getenv('CLINIC_ADDRESS', '123 Main St, City, State 12345')
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Thank You for Your Visit!</h2>
                
                <p>Dear {context.patient_name},</p>
                
                <p>Thank you for choosing {context.clinic_name} for your dental care. We hope you had a positive experience with us today.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <strong>Treatment Summary:</strong><br>
                    <strong>Treatment:</strong> {treatment_name}<br>
                    <strong>Date:</strong> {context.appointment_date}<br>
                    <strong>Doctor:</strong> {context.doctor_name}
                </div>
                
                <h3 style="color: #2c5aa0;">Post-Treatment Care Instructions:</h3>
                <ul>
                    <li>Avoid hard or sticky foods for 24 hours</li>
                    <li>Take prescribed medications as directed</li>
                    <li>Maintain good oral hygiene</li>
                    <li>Apply ice if you experience swelling</li>
                    <li>Contact us if you experience unusual pain or complications</li>
                </ul>
                
                <h3 style="color: #2c5aa0;">Medication Reminders:</h3>
                <p>If you were prescribed medications, please take them as directed. Contact us if you experience any adverse reactions.</p>
                
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                    <h3 style="color: #2c5aa0;">Share Your Experience!</h3>
                    <p>If you have any questions or concerns, please don't hesitate to contact us at {clinic_phone}.</p>
                    <p style="margin-top: 10px; font-size: 14px; color: #666;">{clinic_name}<br>{clinic_address}<br>{clinic_phone}</p>
                </div>
                
                <p>If you have any questions or concerns, please don't hesitate to contact us at {context.clinic_phone}.</p>
                
                <p>We look forward to seeing you at your next appointment!</p>
                
                <p>Best regards,<br>
                <strong>{context.clinic_name}</strong><br>
                {context.clinic_address}<br>
                {context.clinic_phone}</p>
            </div>
        </body>
        </html>
        """
        
        plain_text = f"""
Thank You for Your Visit!

Dear {context.patient_name},

Thank you for choosing {context.clinic_name} for your dental care. We hope you had a positive experience with us today.

Treatment Summary:
Treatment: {treatment_name}
Date: {context.appointment_date}
Doctor: {context.doctor_name}

Post-Treatment Care Instructions:
- Avoid hard or sticky foods for 24 hours
- Take prescribed medications as directed
- Maintain good oral hygiene
- Apply ice if you experience swelling
- Contact us if you experience unusual pain or complications

Medication Reminders:
If you were prescribed medications, please take them as directed. Contact us if you experience any adverse reactions.

Share Your Experience!
If you have any questions or concerns, please don't hesitate to contact us at {clinic_phone}.\n\n{clinic_name}\n{clinic_address}\n{clinic_phone}

If you have any questions or concerns, please don't hesitate to contact us at {context.clinic_phone}.

We look forward to seeing you at your next appointment!

Best regards,
{context.clinic_name}
{context.clinic_address}
{context.clinic_phone}
        """
        
        return {
            "subject": subject,
            "html_content": html_content,
            "plain_text_content": plain_text
        }

# Global AI content generator instance
ai_generator = AIContentGenerator()

def get_ai_content_generator() -> AIContentGenerator:
    """Get the global AI content generator instance"""
    return ai_generator