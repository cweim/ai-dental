# AI Dentist - Comprehensive Dental Appointment & Chatbot System

A complete web-based dental appointment booking system with AI-powered chatbot, automated email notifications, and comprehensive admin dashboard.

## 🏗️ **System Architecture**

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL
- **AI/ML**: OpenAI GPT + Embeddings, FAISS Vector Search
- **Integrations**: Google Calendar, Google Sheets, SendGrid/Mailgun
- **Email**: Automated reminders and follow-ups with APScheduler

## 📋 **Features Overview**

### 🗓️ **Appointment Management**
- Online booking system with real-time availability
- Google Calendar integration for scheduling
- Automatic Google Sheets logging
- Treatment type selection with pricing
- SMS/Email confirmations

### 🤖 **AI Chatbot System**
- Vector-based semantic search with FAISS
- OpenAI GPT-powered responses
- Knowledge base management
- Source attribution and confidence scoring
- Real-time testing interface

### 📧 **Email Automation**
- GPT-generated personalized emails
- 24-hour appointment reminders
- Post-appointment follow-ups
- Treatment summaries and care instructions
- Google Review link integration

### 👨‍💼 **Admin Dashboard**
- Calendar view with booking management
- QA knowledge base editor
- Chatbot testing interface
- Email analytics and logs
- System statistics and monitoring

---

## 🚀 **Quick Start Guide**
cd backend & uvicorn main:app --reload --host 0.0.0.0 --port 8000
cd frontend & npm start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.9+ and pip
- **PostgreSQL** 12+
- **Git**

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI-dentist
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (see Environment Variables section)
cp .env.example .env
# Edit .env with your credentials

# Create database tables
python create_tables.py

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend & npm start


# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start development server
npm start
```
Run the backend: cd backend && uvicorn main:app --reload
Run the frontend: cd frontend && npm start

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

---

## ⚙️ **Environment Variables**

### Backend (.env)
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_dentist

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google API Configuration
GOOGLE_CREDENTIALS_FILE=../google-credentials.json
GOOGLE_CALENDAR_ID=primary
GOOGLE_SHEETS_ID=your_google_sheets_id_here
GOOGLE_REVIEW_URL=https://g.page/r/YOUR_GOOGLE_BUSINESS_ID/review

# Email Service Configuration (Choose one)
EMAIL_SERVICE=sendgrid  # or mailgun

# SendGrid Configuration
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=AI Dentist Clinic

# Mailgun Configuration
MAILGUN_API_KEY=your-mailgun-api-key-here
MAILGUN_DOMAIN=yourdomain.com
MAILGUN_FROM_EMAIL=noreply@yourdomain.com
MAILGUN_FROM_NAME=AI Dentist Clinic

# FastAPI Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Clinic Information
CLINIC_NAME=AI Dentist Clinic
CLINIC_PHONE=(555) 123-4567
CLINIC_ADDRESS=123 Main St, City, State 12345
DOCTOR_NAME=Dr. Smith
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

---

## 🔑 **API Credentials Setup**

### 1. OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new secret key
5. Add to `.env` as `OPENAI_API_KEY`

### 2. Google Calendar & Sheets API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable the following APIs:
   - Google Calendar API
   - Google Sheets API
4. Create credentials (Service Account):
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Download the JSON key file
   - Save as `google-credentials.json` in project root
5. Share your Google Calendar and Sheets with the service account email

### 3. SendGrid Setup (Option 1)
1. Create account at [SendGrid](https://sendgrid.com)
2. Navigate to Settings → API Keys
3. Create new API key with Mail Send permissions
4. Verify sender email address
5. Add API key to `.env` as `SENDGRID_API_KEY`

### 4. Mailgun Setup (Option 2)
1. Create account at [Mailgun](https://mailgun.com)
2. Add and verify your domain
3. Get API key from domain settings
4. Configure DNS records as instructed
5. Add API key to `.env` as `MAILGUN_API_KEY`

### 5. PostgreSQL Database
```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE ai_dentist;
CREATE USER your_username WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_dentist TO your_username;
```

---

## 📁 **Project Structure**

```
AI-dentist/
├── backend/                    # FastAPI Backend
│   ├── main.py                # Main application entry
│   ├── models.py              # SQLAlchemy database models
│   ├── schemas.py             # Pydantic schemas
│   ├── database.py            # Database configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment variables template
│   │
│   ├── chatbot_endpoints.py   # Chatbot API endpoints
│   ├── chatbot_service.py     # Chatbot business logic
│   ├── embeddings_service.py  # OpenAI embeddings integration
│   ├── vector_search.py       # FAISS vector search
│   ├── qa_management.py       # QA pair management
│   ├── dental_corpus.py       # Dental knowledge base
│   │
│   ├── email_endpoints.py     # Email API endpoints
│   ├── email_services.py      # Email service providers
│   ├── email_scheduler.py     # Automated email scheduling
│   ├── ai_content_generator.py # GPT email generation
│   │
│   ├── google_integrations.py # Google Calendar/Sheets
│   ├── treatment_data.py      # Treatment types and pricing
│   └── additional_endpoints.py # Admin utility endpoints
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   ├── AdminLayout.tsx
│   │   │   └── Layout.tsx
│   │   │
│   │   ├── pages/            # Page components
│   │   │   ├── Home.tsx      # Landing page
│   │   │   ├── Appointments.tsx # Booking interface
│   │   │   ├── Admin.tsx     # Admin dashboard
│   │   │   └── admin/        # Admin sub-pages
│   │   │       ├── Dashboard.tsx
│   │   │       ├── CalendarView.tsx
│   │   │       ├── SheetsView.tsx
│   │   │       ├── QAEditor.tsx    # QA Management
│   │   │       └── ChatbotTester.tsx # Chatbot Testing
│   │   │
│   │   ├── App.tsx           # Main app component
│   │   └── index.tsx         # Entry point
│   │
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── .env                  # Environment variables
│
├── google-credentials.json    # Google API credentials
├── README.md                 # This file
└── email-automation-guide.md # Email system documentation
```

---

## 🔗 **API Endpoints**

### Authentication & Core
- `GET /` - Health check
- `GET /health` - System status

### Appointments
- `POST /appointments` - Create appointment
- `GET /appointments` - List appointments
- `POST /appointments/book` - Book appointment with calendar integration
- `GET /appointments/available-slots` - Get available time slots

### Treatments
- `GET /treatments` - List available treatments
- `GET /treatments/types` - Get treatment types and pricing

### Chatbot System
- `POST /api/chatbot/chat` - Process chat query
- `POST /api/chatbot/chat/sessions` - Create chat session
- `GET /api/chatbot/chat/sessions/{id}` - Get session details
- `GET /api/chatbot/chat/sessions/{id}/history` - Get chat history

### QA Management
- `GET /api/chatbot/qa` - List QA pairs
- `POST /api/chatbot/qa` - Create QA pair
- `PUT /api/chatbot/qa/{id}` - Update QA pair
- `DELETE /api/chatbot/qa/{id}` - Delete QA pair
- `POST /api/chatbot/qa/search` - Vector search QA pairs
- `GET /api/chatbot/qa/categories` - Get categories
- `GET /api/chatbot/qa/sources` - Get sources

### Email System
- `GET /api/email/health` - Email system health
- `GET /api/email/logs` - Email delivery logs
- `POST /api/email/send-test` - Send test email
- `GET /api/email/stats` - Email statistics

### Admin
- `GET /api/admin/calendar` - Calendar events
- `GET /api/admin/sheets` - Google Sheets data
- `GET /api/admin/stats` - System statistics

---

## 🎨 **Frontend Components**

### Public Pages
- **Home** (`/`) - Landing page with service overview
- **Appointments** (`/appointments`) - Booking interface

### Admin Dashboard (`/admin`)
- **Dashboard** - System overview and statistics
- **Calendar View** - Appointment management interface
- **Booking Logs** - Google Sheets integration view
- **QA Manager** - Knowledge base management
- **Chatbot Test** - Interactive testing interface

### Key Features
- **Responsive Design** - Works on all devices
- **Real-time Updates** - Live data refresh
- **Error Handling** - Graceful error states
- **Loading States** - Visual feedback
- **Form Validation** - Client-side validation

---

## 🧪 **Testing the System**

### 1. Test Appointment Booking
```bash
# Start both frontend and backend
# Navigate to http://localhost:3000/appointments
# Test the booking flow
```

### 2. Test Chatbot
```bash
# Navigate to http://localhost:3000/admin/chatbot-test
# Try sample questions
# Check response sources and confidence scores
```

### 3. Test QA Management
```bash
# Navigate to http://localhost:3000/admin/qa-editor
# Add new QA pairs
# Use Quick Test to verify responses
```

### 4. Test Email System
```bash
# Book an appointment
# Check email logs in admin dashboard
# Verify automated emails are scheduled
```

---

## 🔧 **Development Commands**

### Backend Development
```bash
cd backend

# Run with auto-reload
uvicorn main:app --reload

# Run tests (if test files exist)
pytest

# Database migrations
alembic upgrade head

# Check code style
flake8 .

# Format code
black .
```

### Frontend Development
```bash
cd frontend

# Development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Type checking
npm run type-check

# Lint code
npm run lint
```

---

## 📚 **Additional Documentation**

### Email System
- See `email-automation-guide.md` for detailed email setup
- Includes templates, scheduling, and analytics

### Google Integration
- See `google-integration-guide.md` for Calendar/Sheets setup
- Includes authentication and permissions

### Admin Dashboard
- See `admin-dashboard-demo.md` for feature overview
- Includes screenshots and usage examples

---

## 🐛 **Troubleshooting**

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Check database exists
   psql -U postgres -l
   ```

2. **Google API Errors**
   ```bash
   # Verify credentials file path
   ls -la google-credentials.json
   
   # Check API permissions
   # Ensure Calendar/Sheets APIs are enabled
   ```

3. **OpenAI API Errors**
   ```bash
   # Check API key is valid
   # Verify you have sufficient quota
   ```

4. **Email Service Issues**
   ```bash
   # Check API keys are correct
   # Verify domain authentication (for production)
   ```

5. **Frontend Build Errors**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Debug Commands
```bash
# Check email system health
curl http://localhost:8000/api/email/health

# View recent email logs
curl http://localhost:8000/api/email/logs?limit=10

# Test chatbot
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are your office hours?"}'

# Check system stats
curl http://localhost:8000/api/admin/stats
```

---

## 🚀 **Production Deployment**

### Environment Setup
1. **Set up production database**
2. **Configure email service with domain authentication**
3. **Set up SSL certificates**
4. **Configure environment variables for production**

### Backend Deployment
```bash
# Use a production WSGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Docker
docker build -t ai-dentist-backend .
docker run -p 8000:8000 ai-dentist-backend
```

### Frontend Deployment
```bash
# Build production bundle
npm run build

# Serve with nginx or deploy to CDN
# Configure API_URL for production
```

---

## 👥 **Contributing**

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Use strict mode, proper typing
- **CSS**: Use Tailwind classes, avoid custom CSS
- **Git**: Use conventional commit messages

---

## 📄 **License**

This project is licensed under the MIT License. See LICENSE file for details.

---

## 📞 **Support**

For development questions or issues:
1. Check the troubleshooting section
2. Review the documentation files
3. Open an issue on GitHub
4. Contact the development team

---

## 🔄 **Version History**

- **v1.0.0** - Initial release with basic booking
- **v1.1.0** - Added email automation
- **v1.2.0** - Integrated AI chatbot system
- **v1.3.0** - Enhanced admin dashboard
- **v1.4.0** - Vector search and QA management

---

**Happy Coding! 🦷✨**