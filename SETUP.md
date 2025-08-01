# AI Dentist Setup Guide

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Python** (v3.8 or higher)
3. **PostgreSQL** (v12 or higher)
4. **Google Cloud Console Account** (for Calendar and Sheets API)

## Initial Setup

### 1. Clone and Install Dependencies

```bash
# Install root dependencies
npm install

# Install all dependencies (frontend + backend)
npm run install:all
```

### 2. Database Setup

1. **Install PostgreSQL** and create a database:
```sql
CREATE DATABASE ai_dentist;
CREATE USER ai_dentist_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_dentist TO ai_dentist_user;
```

2. **Create tables**:
```bash
npm run setup:db
```

### 3. Environment Configuration

1. **Copy environment files**:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

2. **Edit `.env` files** with your actual values:
   - Database credentials
   - Google API credentials path
   - OpenAI API key
   - Secret keys

### 4. Google API Setup

1. **Go to Google Cloud Console**
2. **Create a new project** or select existing
3. **Enable APIs**:
   - Google Calendar API
   - Google Sheets API
4. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Create new service account
   - Download JSON credentials
   - Rename to `google-credentials.json` and place in project root

### 5. Google Calendar Setup

1. **Share calendar** with service account email
2. **Grant appropriate permissions** (read/write)

## Running the Application

### Development Mode

```bash
# Start both frontend and backend
npm run dev

# Or start individually
npm run dev:frontend  # Frontend on http://localhost:3000
npm run dev:backend   # Backend on http://localhost:8000
```

### Production Mode

```bash
# Build and start
npm run build
npm start
```

## API Endpoints

### Appointments
- `GET /appointments` - Get all appointments
- `POST /appointments` - Create new appointment

### Treatments
- `GET /treatments` - Get all treatments
- `POST /treatments` - Create new treatment

### Chatbot
- `GET /chatbot/qa` - Get Q&A entries
- `POST /chatbot/qa` - Add Q&A entry
- `POST /chat` - Chat with AI

## Database Schema

### Users
- Admin users for backend access

### Treatments
- Available dental treatments with pricing

### Appointments
- Patient appointments with Google Calendar integration

### Chatbot QA
- Knowledge base for AI chatbot responses

## Security Notes

1. **Never commit** `.env` files or `google-credentials.json`
2. **Use strong passwords** for database and secret keys
3. **Restrict Google API access** to necessary scopes only
4. **Enable CORS** only for trusted domains in production

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Check PostgreSQL is running
   - Verify database credentials in `.env`

2. **Google API errors**:
   - Ensure service account has proper permissions
   - Check credentials file path

3. **Frontend build errors**:
   - Delete `node_modules` and reinstall
   - Check Node.js version compatibility

## Additional Features to Implement

1. **Email notifications** for appointments
2. **SMS reminders** via Twilio
3. **Advanced AI chatbot** with OpenAI integration
4. **Payment processing** with Stripe
5. **Admin dashboard** improvements
6. **Mobile app** with React Native