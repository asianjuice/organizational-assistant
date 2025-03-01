# backend/app/utils/schedule_parser.py

import csv
from datetime import datetime
from typing import List, Dict

def parse_csv_schedule(file_path: str) -> List[Dict[str, str]]:
    """
    Parse a CSV file containing class schedules.
    CSV format: title,description,start_time,end_time,location
    """
    events = []
    with open(file_path, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            events.append({
                "title": row["title"],
                "description": row["description"],
                "start_time": datetime.fromisoformat(row["start_time"]),
                "end_time": datetime.fromisoformat(row["end_time"]),
                "location": row["location"],
            })
    return events

from icalendar import Calendar

def parse_ics_schedule(file_path: str) -> List[Dict[str, str]]:
    """
    Parse an ICS file containing class schedules.
    """
    events = []
    with open(file_path, mode="r") as file:
        calendar = Calendar.from_ical(file.read())
        for component in calendar.walk():
            if component.name == "VEVENT":
                events.append({
                    "title": str(component.get("summary")),
                    "description": str(component.get("description")),
                    "start_time": component.get("dtstart").dt,
                    "end_time": component.get("dtend").dt,
                    "location": str(component.get("location")),
                })
    return events