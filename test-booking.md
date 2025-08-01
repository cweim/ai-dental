# Testing the Booking System

## Quick Start

1. **Start the development servers**:
```bash
# From project root
npm run dev
```

2. **Set up environment variables**:
```bash
# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend/.env with your database credentials
DATABASE_URL=postgresql://username:password@localhost:5432/ai_dentist
```

3. **Create database tables**:
```bash
npm run setup:db
```

## Testing the Booking Flow

### Frontend (http://localhost:3000/appointments)

1. **Select Treatment**: Choose from 10 different treatments with prices and durations
2. **Pick Date**: Select any date from today to 3 months ahead
3. **View Available Slots**: Real-time check against Google Calendar
4. **Enter Contact Details**: Name, email, phone
5. **Submit**: Creates calendar event and Google Sheets entry

### Backend API Endpoints

- `GET /treatments/types` - Get all treatment types with pricing
- `GET /appointments/available-slots?date=2024-01-15&treatment=cleaning` - Check availability
- `POST /appointments/book` - Book appointment (creates calendar event + sheets entry)

## Features Implemented

### ✅ Treatment Selection
- 10 different treatments with realistic pricing:
  - Cleaning: $120 (60 min)
  - Wisdom Tooth Removal: $300 (60 min)
  - Root Canal: $600 (90 min)
  - Crown: $800 (120 min)
  - And more...

### ✅ Real-time Availability Check
- Queries Google Calendar API for existing appointments
- Calculates available slots based on treatment duration
- Updates automatically when date/treatment changes

### ✅ Smart Time Slot Management
- Business hours: 9 AM - 5:30 PM
- Lunch break: 12 PM - 2 PM
- 30-minute time slots
- Prevents double-booking

### ✅ Google Calendar Integration
- Creates calendar events with proper duration
- Includes patient details and treatment info
- Sends invitation to patient email

### ✅ Google Sheets Integration
- Automatically logs all bookings
- Includes: ID, patient info, treatment, pricing, timestamp
- Headers set up automatically

### ✅ User Experience
- Loading states while checking availability
- Success/error messages
- Form validation
- Responsive design

## Sample Data

The system includes these treatment types:
- Dental Cleaning ($120, 60 min)
- General Checkup ($80, 30 min)
- Dental Filling ($150, 90 min)
- Dental Crown ($800, 120 min)
- Tooth Extraction ($200, 45 min)
- Wisdom Tooth Removal ($300, 60 min)
- Root Canal Treatment ($600, 90 min)
- Teeth Whitening ($250, 60 min)
- Braces Consultation ($100, 45 min)
- Emergency Treatment ($180, 60 min)

## Next Steps

1. **Database Setup**: Create PostgreSQL database
2. **Google Setup**: Configure service account and calendar sharing
3. **Environment**: Set up all environment variables
4. **Testing**: Book a test appointment to verify full flow

The system is ready for immediate testing with dummy data and real Google API integration!