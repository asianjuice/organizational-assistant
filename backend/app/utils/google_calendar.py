# backend/app/utils/google_calendar.py

from datetime import datetime
from googleapiclient.discovery import build
from backend.app.utils.google_auth import authenticate_google_calendar

def fetch_google_calendar_events(start_time: datetime, end_time: datetime):
    """
    Fetch events from Google Calendar within a specified time range.
    """
    creds = authenticate_google_calendar()
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

def find_free_time_slots(events, start_time: datetime, end_time: datetime):
    """
    Find free time slots between events in the user's calendar.
    """
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

def suggest_time_slots(free_slots, task_duration_minutes: int):
    """
    Suggest optimal time slots for tasks based on free time in the user's calendar.
    """
    suggested_slots = []
    for slot in free_slots:
        slot_duration = (slot["end"] - slot["start"]).total_seconds() / 60
        if slot_duration >= task_duration_minutes:
            suggested_slots.append(slot)
    return suggested_slots

#create event in google calendar
def create_google_calendar_event(summary: str, start_time: datetime, end_time: datetime, description: str = None):
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
    }

    # Insert the event into the primary calendar
    event = service.events().insert(calendarId="primary", body=event).execute()
    return event.get("id")

def create_google_calendar_event(summary: str, start_time: datetime, end_time: datetime, description: str = None, location: str = None):
    """
    Create an event in Google Calendar.
    """
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
    }

    if location:
        event["location"] = location

    # Insert the event into the primary calendar
    event = service.events().insert(calendarId="primary", body=event).execute()
    return event.get("id")