import json
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Get absolute path to the storage directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "modules", "stored")
SCHEDULE_FILE = os.path.join(STORAGE_DIR, "schedule.json")

# Pydantic models for validation
class ReminderCreate(BaseModel):
    time: str
    message: str

class ReminderUpdate(BaseModel):
    time: Optional[str] = None
    message: Optional[str] = None

def load_schedule():
    """Load schedule from JSON file with error handling"""
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_schedule(schedule_list):
    """Save schedule to JSON file with error handling"""
    try:
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(schedule_list, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving schedule: {e}")
        return False

@router.post("/schedule", response_model=dict)
def add_reminder(reminder: ReminderCreate):
    """Add a new reminder to the schedule"""
    schedule = load_schedule()
    
    new_reminder = {
        "id": str(uuid.uuid4()),  # Use UUID for unique IDs
        "time": reminder.time,
        "message": reminder.message,
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }
    
    schedule.append(new_reminder)
    
    if save_schedule(schedule):
        return {
            "message": "Reminder added successfully",
            "reminder": new_reminder,
            "success": True
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to save reminder")

@router.get("/schedule", response_model=dict)
def get_schedule():
    """Get all reminders from the schedule"""
    schedule = load_schedule()
    return {
        "schedule": schedule,
        "count": len(schedule),
        "success": True
    }

@router.put("/schedule/{reminder_id}", response_model=dict)
def update_reminder(reminder_id: str, updates: ReminderUpdate):
    """Update an existing reminder"""
    schedule = load_schedule()
    
    for reminder in schedule:
        if reminder["id"] == reminder_id:
            if updates.time is not None:
                reminder["time"] = updates.time
            if updates.message is not None:
                reminder["message"] = updates.message
            reminder["updated_at"] = datetime.now().isoformat()
            
            if save_schedule(schedule):
                return {
                    "message": "Reminder updated successfully",
                    "reminder": reminder,
                    "success": True
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to update reminder")
    
    raise HTTPException(status_code=404, detail="Reminder not found")

@router.delete("/schedule/{reminder_id}", response_model=dict)
def delete_reminder(reminder_id: str):
    """Delete a reminder from the schedule"""
    schedule = load_schedule()
    initial_count = len(schedule)
    
    schedule = [r for r in schedule if r["id"] != reminder_id]
    
    if len(schedule) == initial_count:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    if save_schedule(schedule):
        return {
            "message": "Reminder deleted successfully",
            "id": reminder_id,
            "success": True
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to delete reminder")

@router.delete("/schedule", response_model=dict)
def clear_schedule():
    """Clear all reminders from the schedule"""
    if save_schedule([]):
        return {
            "message": "All reminders cleared successfully",
            "success": True
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to clear schedule")