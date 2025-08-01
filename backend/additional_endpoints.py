from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
from datetime import datetime, timedelta

from database import get_db
from models import Appointment
from treatment_data import TREATMENT_TYPES

router = APIRouter()

@router.get("/calendar/events")
async def get_calendar_events(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db)
):
    """Get calendar events for admin dashboard from database only"""
    try:
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        
        if not end_date:
            # Get last day of current month
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get appointments from database
        db_appointments = db.query(Appointment).filter(
            Appointment.appointment_date >= start_date.strftime("%Y-%m-%d"),
            Appointment.appointment_date <= end_date.strftime("%Y-%m-%d")
        ).all()
        
        # Format events for calendar display
        events = []
        for appointment in db_appointments:
            # Create datetime for start and end
            appointment_datetime = datetime.strptime(f"{appointment.appointment_date} {appointment.appointment_time}", "%Y-%m-%d %H:%M")
            treatment_info = TREATMENT_TYPES.get(appointment.treatment_type, {'duration': 30})
            end_datetime = appointment_datetime + timedelta(minutes=treatment_info['duration'])
            
            event = {
                'id': str(appointment.id),
                'title': f"{appointment.patient_name} - {appointment.treatment_type}",
                'start': appointment_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'resource': {
                    'patientName': appointment.patient_name,
                    'patientEmail': appointment.patient_email,
                    'patientPhone': appointment.patient_phone,
                    'treatment': appointment.treatment_type,
                    'status': appointment.status,
                    'notes': appointment.notes or '',
                    'adminNotes': appointment.admin_notes or ''
                }
            }
            events.append(event)
        
        return {"events": events}
        
    except Exception as e:
        logging.error(f"Error getting calendar events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch calendar events")

@router.get("/sheets/bookings")
async def get_sheets_bookings(
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 50,
    search: str = "",
    status: str = "all",
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get bookings from database with filtering, pagination, and sorting"""
    try:
        # Start with base query
        query = db.query(Appointment)
        
        # Apply search filter
        if search.strip():
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (Appointment.patient_name.ilike(search_term)) |
                (Appointment.patient_email.ilike(search_term)) |
                (Appointment.treatment_type.ilike(search_term))
            )
        
        # Apply status filter
        if status != "all":
            query = query.filter(Appointment.status == status)
        
        # Apply sorting
        sort_column = Appointment.created_at  # default
        if sort_by == "date":
            sort_column = Appointment.appointment_date
        elif sort_by == "name":
            sort_column = Appointment.patient_name
        elif sort_by == "treatment":
            sort_column = Appointment.treatment_type
        elif sort_by == "status":
            sort_column = Appointment.status
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        appointments = query.offset(offset).limit(limit).all()
        
        # Transform to booking format
        bookings = []
        for appointment in appointments:
            treatment_info = TREATMENT_TYPES.get(appointment.treatment_type, {})
            booking = {
                'id': str(appointment.id),
                'patientName': appointment.patient_name,
                'email': appointment.patient_email,
                'phone': appointment.patient_phone,
                'date': appointment.appointment_date,
                'time': appointment.appointment_time,
                'treatment': treatment_info.get('name', appointment.treatment_type),
                'price': f"${treatment_info.get('price', 0):.0f}",
                'duration': f"{treatment_info.get('duration', 30)} min",
                'notes': appointment.notes or '',
                'adminNotes': appointment.admin_notes or '',
                'status': appointment.status,
                'createdAt': appointment.created_at.isoformat() if appointment.created_at else '',
                'updatedAt': appointment.updated_at.isoformat() if appointment.updated_at else ''
            }
            bookings.append(booking)
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "bookings": bookings,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters": {
                "search": search,
                "status": status,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
    except Exception as e:
        logging.error(f"Error getting bookings: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch bookings")

@router.put("/appointments/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update appointment status in database"""
    try:
        # Validate status
        valid_statuses = ['confirmed', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Update in database
        db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not db_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        db_appointment.status = status
        db.commit()
        
        return {
            "message": "Appointment status updated successfully",
            "appointment_id": appointment_id,
            "new_status": status
        }
        
    except Exception as e:
        logging.error(f"Error updating appointment status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment status")

@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Cancel an appointment (update status in database)"""
    try:
        # Get appointment from database
        db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not db_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Update status in database
        db_appointment.status = 'cancelled'
        db.commit()
        
        return {
            "message": "Appointment cancelled successfully",
            "appointment_id": appointment_id
        }
        
    except Exception as e:
        logging.error(f"Error cancelling appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")

@router.put("/appointments/{appointment_id}/notes")
async def update_appointment_notes(
    appointment_id: int,
    notes_data: dict,
    db: Session = Depends(get_db)
):
    """Update admin notes for an appointment"""
    try:
        # Get appointment from database
        db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not db_appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Update admin notes in database
        admin_notes = notes_data.get('admin_notes', '')
        db_appointment.admin_notes = admin_notes
        db.commit()
        db.refresh(db_appointment)
        
        return {
            "message": "Admin notes updated successfully",
            "appointment_id": appointment_id,
            "admin_notes": admin_notes
        }
        
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating admin notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to update admin notes")

@router.get("/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """Get statistics for admin dashboard"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get counts from database
        total_appointments = db.query(Appointment).count()
        today_appointments = db.query(Appointment).filter(Appointment.appointment_date == today).count()
        cancelled_appointments = db.query(Appointment).filter(Appointment.status == 'cancelled').count()
        completed_appointments = db.query(Appointment).filter(Appointment.status == 'completed').count()
        
        # Calculate revenue (basic calculation)
        appointments = db.query(Appointment).all()
        total_revenue = 0
        for appointment in appointments:
            if appointment.treatment_type in TREATMENT_TYPES:
                total_revenue += TREATMENT_TYPES[appointment.treatment_type]['price']
        
        return {
            "total_appointments": total_appointments,
            "today_appointments": today_appointments,
            "cancelled_appointments": cancelled_appointments,
            "completed_appointments": completed_appointments,
            "total_revenue": total_revenue,
            "average_appointment_value": total_revenue / total_appointments if total_appointments > 0 else 0
        }
        
    except Exception as e:
        logging.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin statistics")

