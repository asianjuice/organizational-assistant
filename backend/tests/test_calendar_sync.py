# backend/tests/test_calendar_sync.py

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine
import os

# Fixture to provide a TestClient instance
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

# Fixture to set up and tear down the database
@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Fixture to provide a database session
@pytest.fixture(scope="function")
def db_session(setup_database):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test: Upload and sync a CSV class schedule
def test_upload_csv_schedule(client, db_session):
    # Create a dummy CSV file
    csv_content = """title,description,start_time,end_time,location
Class 1,Math,2025-02-01T10:00:00,2025-02-01T11:00:00,Room 101
Class 2,Science,2025-02-01T12:00:00,2025-02-01T13:00:00,Room 102
"""
    with open("test_schedule.csv", "w") as f:
        f.write(csv_content)

    # Upload the CSV file
    with open("test_schedule.csv", "rb") as f:
        response = client.post(
            "/api/calendar/upload-schedule",
            files={"file": ("test_schedule.csv", f, "text/csv")},
        )

    # Assert the response
    assert response.status_code == 200
    assert response.json()["message"] == "Class schedule synced successfully"
    assert response.json()["num_events"] == 2

    # Clean up the dummy CSV file
    os.remove("test_schedule.csv")

# Test: Upload and sync an ICS class schedule
def test_upload_ics_schedule(client, db_session):
    # Create a dummy ICS file
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Your Organization//Your Product//EN
BEGIN:VEVENT
SUMMARY:Class 1
DESCRIPTION:Math
DTSTART:20250201T100000
DTEND:20250201T110000
LOCATION:Room 101
END:VEVENT
BEGIN:VEVENT
SUMMARY:Class 2
DESCRIPTION:Science
DTSTART:20250201T120000
DTEND:20250201T130000
LOCATION:Room 102
END:VEVENT
END:VCALENDAR
"""
    with open("test_schedule.ics", "w") as f:
        f.write(ics_content)

    # Upload the ICS file
    with open("test_schedule.ics", "rb") as f:
        response = client.post(
            "/api/calendar/upload-schedule",
            files={"file": ("test_schedule.ics", f, "text/calendar")},
        )

    # Assert the response
    assert response.status_code == 200
    assert response.json()["message"] == "Class schedule synced successfully"
    assert response.json()["num_events"] == 2

    # Clean up the dummy ICS file
    os.remove("test_schedule.ics")