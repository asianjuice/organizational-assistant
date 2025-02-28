# backend/app/routes/calendar.py

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from backend.app.utils.calendar import fetch_calendar_events, find_free_time_slots, suggest_time_slots
from pydantic import BaseModel

router = APIRouter()

# Pydantic model for request body validation
class SuggestTimeSlotsRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    task_duration_minutes: int

# Fetch free time slots
@router.get("/calendar/free-time")
def get_free_time_slots(start_time: datetime, end_time: datetime):
    try:
        events = fetch_calendar_events(start_time, end_time)
        free_slots = find_free_time_slots(events, start_time, end_time)
        return {"free_slots": free_slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Suggest optimal time slots for a task
@router.post("/calendar/suggest-time")
def suggest_time_for_task(request: SuggestTimeSlotsRequest):
    try:
        events = fetch_calendar_events(request.start_time, request.end_time)
        free_slots = find_free_time_slots(events, request.start_time, request.end_time)
        suggested_slots = suggest_time_slots(free_slots, request.task_duration_minutes)
        return {"suggested_slots": suggested_slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))