from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging
from datetime import datetime

from database import get_db
from models import ClinicSetting

router = APIRouter()

# Default clinic settings that will be created on first run
DEFAULT_SETTINGS = [
    {
        "setting_key": "clinic_name",
        "setting_value": "AI Dentist Clinic",
        "setting_type": "text",
        "display_name": "Clinic Name",
        "description": "The name of your dental practice",
        "category": "general"
    },
    {
        "setting_key": "doctor_name",
        "setting_value": "Dr. Smith",
        "setting_type": "text",
        "display_name": "Primary Doctor Name",
        "description": "Name of the primary dentist",
        "category": "general"
    },
    {
        "setting_key": "clinic_phone",
        "setting_value": "(555) 123-4567",
        "setting_type": "phone",
        "display_name": "Clinic Phone",
        "description": "Main phone number for appointments and inquiries",
        "category": "contact"
    },
    {
        "setting_key": "clinic_email",
        "setting_value": "info@aidentiist.com",
        "setting_type": "email",
        "display_name": "Clinic Email",
        "description": "Main email address for the clinic",
        "category": "contact"
    },
    {
        "setting_key": "clinic_address",
        "setting_value": "123 Main St, City, State 12345",
        "setting_type": "textarea",
        "display_name": "Clinic Address",
        "description": "Physical address of the clinic",
        "category": "contact"
    },
    {
        "setting_key": "business_hours",
        "setting_value": "Monday-Friday: 9:00 AM - 5:30 PM",
        "setting_type": "textarea",
        "display_name": "Business Hours",
        "description": "Operating hours for the clinic",
        "category": "general"
    },
    {
        "setting_key": "google_review_url",
        "setting_value": "https://g.page/r/YOUR_GOOGLE_BUSINESS_ID/review",
        "setting_type": "url",
        "display_name": "Google Review Link",
        "description": "Direct link to your Google Business review page",
        "category": "review"
    },
    {
        "setting_key": "emergency_contact",
        "setting_value": "(555) 123-4567",
        "setting_type": "phone",
        "display_name": "Emergency Contact",
        "description": "After-hours emergency contact number",
        "category": "contact"
    },
    {
        "setting_key": "website_url",
        "setting_value": "https://www.aidentiist.com",
        "setting_type": "url",
        "display_name": "Website URL",
        "description": "Main website for the clinic",
        "category": "general"
    },
    {
        "setting_key": "appointment_reminder_hours",
        "setting_value": "24",
        "setting_type": "text",
        "display_name": "Reminder Hours Before",
        "description": "How many hours before appointment to send reminder (default: 24)",
        "category": "email"
    },
    {
        "setting_key": "followup_hours_after",
        "setting_value": "2",
        "setting_type": "text",
        "display_name": "Follow-up Hours After",
        "description": "How many hours after appointment to send follow-up (default: 2)",
        "category": "email"
    }
]

@router.get("/settings")
async def get_clinic_settings(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all clinic settings, optionally filtered by category"""
    try:
        # Initialize default settings if none exist
        await initialize_default_settings(db)
        
        query = db.query(ClinicSetting).filter(ClinicSetting.is_active == True)
        
        if category:
            query = query.filter(ClinicSetting.category == category)
        
        settings = query.order_by(ClinicSetting.category, ClinicSetting.display_name).all()
        
        return [{
            "id": setting.id,
            "setting_key": setting.setting_key,
            "setting_value": setting.setting_value,
            "setting_type": setting.setting_type,
            "display_name": setting.display_name,
            "description": setting.description,
            "category": setting.category,
            "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
        } for setting in settings]
        
    except Exception as e:
        logging.error(f"Error getting clinic settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve clinic settings")

@router.get("/settings/{setting_key}")
async def get_clinic_setting(
    setting_key: str,
    db: Session = Depends(get_db)
):
    """Get a specific clinic setting by key"""
    try:
        setting = db.query(ClinicSetting).filter(
            ClinicSetting.setting_key == setting_key,
            ClinicSetting.is_active == True
        ).first()
        
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        return {
            "id": setting.id,
            "setting_key": setting.setting_key,
            "setting_value": setting.setting_value,
            "setting_type": setting.setting_type,
            "display_name": setting.display_name,
            "description": setting.description,
            "category": setting.category,
            "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting clinic setting {setting_key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve clinic setting")

@router.put("/settings/{setting_key}")
async def update_clinic_setting(
    setting_key: str,
    setting_value: str,
    db: Session = Depends(get_db)
):
    """Update a specific clinic setting"""
    try:
        setting = db.query(ClinicSetting).filter(
            ClinicSetting.setting_key == setting_key,
            ClinicSetting.is_active == True
        ).first()
        
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        setting.setting_value = setting_value
        setting.updated_at = datetime.now()
        db.commit()
        db.refresh(setting)
        
        return {
            "message": f"Setting {setting_key} updated successfully",
            "setting_key": setting_key,
            "new_value": setting_value,
            "updated_at": setting.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating clinic setting {setting_key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update clinic setting")

@router.post("/settings")
async def create_clinic_setting(
    setting_key: str,
    setting_value: str,
    setting_type: str,
    display_name: str,
    description: str = "",
    category: str = "general",
    db: Session = Depends(get_db)
):
    """Create a new clinic setting"""
    try:
        # Check if setting already exists
        existing = db.query(ClinicSetting).filter(ClinicSetting.setting_key == setting_key).first()
        if existing:
            raise HTTPException(status_code=400, detail="Setting key already exists")
        
        new_setting = ClinicSetting(
            setting_key=setting_key,
            setting_value=setting_value,
            setting_type=setting_type,
            display_name=display_name,
            description=description,
            category=category
        )
        
        db.add(new_setting)
        db.commit()
        db.refresh(new_setting)
        
        return {
            "message": "Setting created successfully",
            "id": new_setting.id,
            "setting_key": new_setting.setting_key,
            "display_name": new_setting.display_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating clinic setting: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create clinic setting")

@router.delete("/settings/{setting_key}")
async def delete_clinic_setting(
    setting_key: str,
    db: Session = Depends(get_db)
):
    """Soft delete a clinic setting (mark as inactive)"""
    try:
        setting = db.query(ClinicSetting).filter(ClinicSetting.setting_key == setting_key).first()
        
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        setting.is_active = False
        db.commit()
        
        return {
            "message": f"Setting {setting_key} deleted successfully",
            "setting_key": setting_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting clinic setting {setting_key}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete clinic setting")

@router.get("/categories")
async def get_setting_categories(db: Session = Depends(get_db)):
    """Get all setting categories"""
    try:
        categories = db.query(ClinicSetting.category).filter(
            ClinicSetting.is_active == True
        ).distinct().all()
        
        return [{"category": cat[0]} for cat in categories]
        
    except Exception as e:
        logging.error(f"Error getting setting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve setting categories")

async def initialize_default_settings(db: Session):
    """Initialize default clinic settings if none exist"""
    try:
        # Check if any settings exist
        existing_count = db.query(ClinicSetting).count()
        
        if existing_count == 0:
            # Create default settings
            for default_setting in DEFAULT_SETTINGS:
                setting = ClinicSetting(**default_setting)
                db.add(setting)
            
            db.commit()
            logging.info(f"Initialized {len(DEFAULT_SETTINGS)} default clinic settings")
            
    except Exception as e:
        db.rollback()
        logging.error(f"Error initializing default settings: {str(e)}")

def get_setting_value(db: Session, setting_key: str, default_value: str = "") -> str:
    """Helper function to get a setting value"""
    try:
        setting = db.query(ClinicSetting).filter(
            ClinicSetting.setting_key == setting_key,
            ClinicSetting.is_active == True
        ).first()
        
        return setting.setting_value if setting else default_value
        
    except Exception as e:
        logging.error(f"Error getting setting {setting_key}: {str(e)}")
        return default_value

def get_all_settings_dict(db: Session) -> Dict[str, str]:
    """Helper function to get all settings as a dictionary"""
    try:
        settings = db.query(ClinicSetting).filter(ClinicSetting.is_active == True).all()
        return {setting.setting_key: setting.setting_value for setting in settings}
    except Exception as e:
        logging.error(f"Error getting all settings: {str(e)}")
        return {}