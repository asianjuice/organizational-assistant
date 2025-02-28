# backend/app/utils/calendar.py

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from backend.app.utils.google_calendar import fetch_google_calendar_events
from pydantic import BaseModel


# Load credentials from the token file
def load_credentials():
    token_path = "token.json"
    if os.path.exists(token_path):
        return Credentials.from_authorized_user_file(token_path)
    return None

# Fetch events from Google Calendar
def fetch_calendar_events(start_time: datetime, end_time: datetime):
    creds = load_credentials()
    if not creds:
        raise Exception("User not authenticated")

    service = build("calendar", "v3", credentials=creds)

    # Fetch events within the specified time range
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_time.isoformat() + "Z",
            timeMax=end_time.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events_result.get("items", [])

# backend/app/utils/calendar.py

def find_free_time_slots(events, start_time: datetime, end_time: datetime):
    free_slots = []
    current_time = start_time

    for event in events:
        event_start = datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date")))
        event_end = datetime.fromisoformat(event["end"].get("dateTime", event["end"].get("date")))

        if current_time < event_start:
            free_slots.append({"start": current_time, "end": event_start})
        current_time = max(current_time, event_end)

    if current_time < end_time:
        free_slots.append({"start": current_time, "end": end_time})

    return free_slots

# backend/app/utils/calendar.py

def suggest_time_slots(free_slots, task_duration_minutes: int):
    suggested_slots = []
    for slot in free_slots:
        slot_duration = (slot["end"] - slot["start"]).total_seconds() / 60
        if slot_duration >= task_duration_minutes:
            suggested_slots.append(slot)
    return suggested_slots

# backend/app/routes/calendar.py

router = APIRouter()

# Pydantic model for request body validation
class FetchEventsRequest(BaseModel):
    start_time: datetime
    end_time: datetime

# Fetch events from Google Calendar
@router.post("/calendar/events")
def fetch_events(request: FetchEventsRequest):
    try:
        events = fetch_google_calendar_events(request.start_time, request.end_time)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))