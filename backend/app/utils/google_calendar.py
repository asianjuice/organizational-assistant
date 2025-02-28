# backend/app/utils/google_calendar.py

from datetime import datetime, timedelta
from googleapiclient.discovery import build
from backend.app.utils.google_auth import authenticate_google_calendar

# Function to fetch events from Google Calendar
def fetch_google_calendar_events(start_time: datetime, end_time: datetime):
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