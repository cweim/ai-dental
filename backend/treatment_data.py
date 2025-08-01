TREATMENT_TYPES = {
    "cleaning": {
        "name": "Dental Cleaning",
        "duration": 60,  # minutes
        "description": "Professional teeth cleaning and polishing",
        "price": 120.00
    },
    "checkup": {
        "name": "General Checkup",
        "duration": 30,
        "description": "Routine dental examination and consultation",
        "price": 80.00
    },
    "filling": {
        "name": "Dental Filling",
        "duration": 90,
        "description": "Tooth restoration with composite or amalgam filling",
        "price": 150.00
    },
    "crown": {
        "name": "Dental Crown",
        "duration": 120,
        "description": "Custom crown placement for damaged teeth",
        "price": 800.00
    },
    "extraction": {
        "name": "Tooth Extraction",
        "duration": 45,
        "description": "Simple tooth removal procedure",
        "price": 200.00
    },
    "wisdom_tooth": {
        "name": "Wisdom Tooth Removal",
        "duration": 60,
        "description": "Surgical removal of wisdom teeth",
        "price": 300.00
    },
    "root_canal": {
        "name": "Root Canal Treatment",
        "duration": 90,
        "description": "Endodontic treatment for infected tooth",
        "price": 600.00
    },
    "whitening": {
        "name": "Teeth Whitening",
        "duration": 60,
        "description": "Professional teeth whitening treatment",
        "price": 250.00
    },
    "braces_consultation": {
        "name": "Braces Consultation",
        "duration": 45,
        "description": "Orthodontic evaluation and treatment planning",
        "price": 100.00
    },
    "emergency": {
        "name": "Emergency Treatment",
        "duration": 60,
        "description": "Urgent dental care for pain or injury",
        "price": 180.00
    }
}

# Available time slots (24-hour format)
AVAILABLE_TIME_SLOTS = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"
]

# Business hours
BUSINESS_HOURS = {
    "start": "09:00",
    "end": "17:30",
    "lunch_start": "12:00",
    "lunch_end": "14:00"
}