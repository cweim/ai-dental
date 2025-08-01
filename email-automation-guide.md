# Email Automation System Guide

## Overview
This guide covers the comprehensive email automation system for the AI Dentist booking platform, featuring GPT-powered content generation, scheduled email delivery, and multi-provider support.

## Features

### ✅ **Automated Email Flow**
1. **Reminder Emails** - Sent 24 hours before appointment
2. **Follow-up Emails** - Sent 2 hours after appointment completion
3. **GPT-Generated Content** - Personalized emails using OpenAI
4. **Multi-Provider Support** - SendGrid and Mailgun integration
5. **Scheduled Delivery** - APScheduler for automated sending

### ✅ **Email Content Generation**
- **OpenAI Integration** - Dynamic content based on appointment details
- **Fallback Templates** - HTML/Plain text templates when AI unavailable
- **Personalization** - Patient name, treatment type, clinic info
- **Smart Content** - Treatment-specific care instructions

### ✅ **Email Service Providers**
- **SendGrid Support** - Full integration with delivery tracking
- **Mailgun Support** - Alternative provider with status tracking
- **Automatic Fallback** - Switches providers if primary fails
- **Health Monitoring** - Service availability checking

## Setup Instructions

### 1. Install Dependencies
```bash
pip install sendgrid mailgun-py apscheduler openai jinja2
```

### 2. Environment Configuration
Add to your `.env` file:
```env
# Email Service (choose one)
EMAIL_SERVICE=sendgrid  # or mailgun

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=AI Dentist Clinic

# Mailgun Configuration
MAILGUN_API_KEY=your_mailgun_api_key_here
MAILGUN_DOMAIN=yourdomain.com
MAILGUN_FROM_EMAIL=noreply@yourdomain.com
MAILGUN_FROM_NAME=AI Dentist Clinic

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Clinic Information
CLINIC_NAME=AI Dentist Clinic
CLINIC_PHONE=(555) 123-4567
CLINIC_ADDRESS=123 Main St, City, State 12345
DOCTOR_NAME=Dr. Smith
GOOGLE_REVIEW_URL=https://g.page/r/YOUR_GOOGLE_BUSINESS_ID/review
```

### 3. Database Setup
The system automatically creates these tables:
- `email_logs` - Track all sent emails
- `email_templates` - Store reusable templates
- `email_preferences` - Patient email preferences

### 4. SendGrid Setup
1. Create account at [SendGrid](https://sendgrid.com/)
2. Generate API key with mail send permissions
3. Verify sender email address
4. Set up domain authentication (optional)

### 5. Mailgun Setup
1. Create account at [Mailgun](https://mailgun.com/)
2. Add and verify your domain
3. Get API key from domain settings
4. Configure DNS records

## System Architecture

### 📧 **Email Services** (`email_services.py`)
```python
# Multi-provider email management
email_manager = EmailServiceManager()

# Send email with automatic fallback
result = email_manager.send_email(EmailMessage(
    to_email="patient@example.com",
    to_name="John Doe",
    subject="Appointment Reminder",
    html_content="<h1>Your appointment is tomorrow</h1>",
    plain_text_content="Your appointment is tomorrow"
))
```

### 🤖 **AI Content Generation** (`ai_content_generator.py`)
```python
# Generate personalized email content
ai_generator = get_ai_content_generator()

context = AppointmentContext(
    patient_name="John Doe",
    treatment_type="cleaning",
    appointment_date="2024-01-15",
    appointment_time="10:00",
    duration=60,
    price=120.0
)

# Generate reminder email
reminder_content = ai_generator.generate_reminder_email(context)
# Returns: {"subject": "...", "html_content": "...", "plain_text_content": "..."}

# Generate follow-up email
followup_content = ai_generator.generate_followup_email(context)
```

### ⏰ **Email Scheduler** (`email_scheduler.py`)
```python
# Schedule emails for an appointment
email_scheduler = get_email_scheduler()

# Automatically schedules both reminder and follow-up
results = email_scheduler.schedule_appointment_emails(appointment_id=123)
# Returns: {"reminder": True, "followup": True}

# Cancel scheduled emails
cancelled = email_scheduler.cancel_appointment_emails(appointment_id=123)

# Reschedule emails (useful when appointment changes)
results = email_scheduler.reschedule_appointment_emails(appointment_id=123)
```

## Email Flow Examples

### 📅 **Reminder Email Flow**
**Triggered**: 24 hours before appointment
**Content**: AI-generated personalized reminder with:
- Appointment details
- What to bring
- Preparation instructions
- Contact information
- Rescheduling options

### 📋 **Follow-up Email Flow**
**Triggered**: 2 hours after appointment
**Content**: AI-generated follow-up with:
- Thank you message
- Treatment summary
- Post-care instructions
- Medication reminders
- Google Review link
- Next appointment scheduling

## API Endpoints

### 📊 **Email Management**
```http
# Check email system health
GET /api/email/health

# Get email logs
GET /api/email/logs?appointment_id=123&email_type=reminder

# Send test email
POST /api/email/send-test
{
  "to_email": "test@example.com",
  "to_name": "Test User",
  "email_type": "reminder"
}

# Get email statistics
GET /api/email/stats?days=30
```

### 🔧 **Appointment Email Control**
```http
# Send manual reminder
POST /api/email/appointments/123/send-reminder

# Send manual follow-up
POST /api/email/appointments/123/send-followup

# Cancel scheduled emails
DELETE /api/email/appointments/123/cancel-emails

# Reschedule emails
POST /api/email/appointments/123/reschedule-emails
```

### ⚙️ **Email Preferences**
```http
# Update patient preferences
POST /api/email/preferences
{
  "email": "patient@example.com",
  "reminder_emails": true,
  "followup_emails": true,
  "marketing_emails": false
}

# Get patient preferences
GET /api/email/preferences/patient@example.com

# Unsubscribe using token
POST /api/email/unsubscribe/unique-token-here
```

## Sample Generated Content

### 🔔 **Reminder Email Sample**
```html
Subject: Reminder: Your Dental Cleaning appointment tomorrow

Dear John,

This is a friendly reminder about your upcoming dental appointment:

Appointment Details:
• Treatment: Dental Cleaning
• Date: January 15, 2024
• Time: 10:00 AM
• Duration: 60 minutes
• Doctor: Dr. Smith

Please bring:
• Photo ID
• Insurance card
• List of current medications
• Payment method

If you need to reschedule, please call (555) 123-4567.

We look forward to seeing you tomorrow!

Best regards,
AI Dentist Clinic
```

### 📝 **Follow-up Email Sample**
```html
Subject: Thank you for your visit - Post-treatment care

Dear John,

Thank you for choosing AI Dentist Clinic for your dental cleaning today.

Treatment Summary:
• Procedure: Professional Dental Cleaning
• Date: January 15, 2024
• Duration: 60 minutes
• Doctor: Dr. Smith

Post-Treatment Care:
• Maintain regular brushing and flossing
• Use fluoride toothpaste
• Schedule next cleaning in 6 months
• Contact us if you experience any issues

Share Your Experience:
[Leave a Google Review] (https://g.page/r/YOUR_BUSINESS_ID/review)

Questions? Call us at (555) 123-4567

Best regards,
AI Dentist Clinic
```

## Monitoring and Analytics

### 📈 **Email Statistics**
- **Delivery rates** by email type
- **Open rates** (with tracking setup)
- **Click rates** for review links
- **Failure analysis** and error tracking

### 🔍 **Email Logs**
- **Comprehensive logging** of all email attempts
- **Error tracking** with detailed messages
- **Delivery status** tracking
- **Patient interaction** tracking

### ⚡ **System Health**
- **Service availability** monitoring
- **Queue status** and job tracking
- **AI service** health checks
- **Automatic failover** between providers

## Advanced Features

### 🎯 **Smart Scheduling**
- **Time zone support** for multi-location clinics
- **Business hours** respect for email sending
- **Appointment status** checking before sending
- **Automatic rescheduling** when appointments change

### 🚫 **Unsubscribe Management**
- **One-click unsubscribe** links
- **Granular preferences** (reminder vs follow-up)
- **Compliance** with email regulations
- **Preference center** for patients

### 📊 **Template Management**
- **Custom templates** for different treatments
- **A/B testing** support for content optimization
- **Seasonal templates** for holidays
- **Multi-language** support ready

## Production Considerations

### 🔒 **Security**
- **API key encryption** and secure storage
- **Email content** sanitization
- **GDPR compliance** for EU patients
- **Rate limiting** to prevent abuse

### 📈 **Scalability**
- **Queue management** for high-volume clinics
- **Batch processing** for bulk operations
- **Database indexing** for performance
- **Caching** for frequently accessed data

### 🛡️ **Reliability**
- **Retry logic** for failed deliveries
- **Dead letter queues** for persistent failures
- **Health checks** and monitoring
- **Graceful degradation** when services are down

## Troubleshooting

### Common Issues
1. **"Email not sent"** - Check API keys and service configuration
2. **"Scheduler not working"** - Verify database connection and APScheduler setup
3. **"AI content generation failed"** - Check OpenAI API key and quotas
4. **"Emails going to spam"** - Verify domain authentication and sender reputation

### Debug Commands
```bash
# Check email service health
curl http://localhost:8000/api/email/health

# View recent email logs
curl http://localhost:8000/api/email/logs?limit=10

# Test email sending
curl -X POST http://localhost:8000/api/email/send-test \
  -H "Content-Type: application/json" \
  -d '{"to_email": "test@example.com", "to_name": "Test User"}'
```

The email automation system is now fully operational and ready to enhance your dental practice's patient communication!