# backend/tests/test_calendar.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine

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

# Test: Fetch Google Calendar Events
def test_fetch_google_calendar_events(client, db_session):
    start_time = datetime.now()
    end_time = start_time + timedelta(days=7)

    response = client.post(
        "/api/calendar/events",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    )

    assert response.status_code == 200
    assert "events" in response.json()

# Test: Suggest Optimal Time Slots
def test_suggest_optimal_time_slots(client, db_session):
    start_time = datetime.now()
    end_time = start_time + timedelta(days=7)

    response = client.post(
        "/api/calendar/suggest-time",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    )

    assert response.status_code == 200
    assert "suggested_slots" in response.json()

# Test: Create an event in Google Calendar
def test_create_calendar_event(client, db_session):
    # Mock data for the request
    start_time = datetime.now() + timedelta(hours=1)  # Event starts in 1 hour
    end_time = start_time + timedelta(hours=2)        # Event ends in 2 hours

    # Send the request
    response = client.post(
        "/api/calendar/create-event",
        json={
            "summary": "Test Event",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "description": "This is a test event.",
        },
    )

    # Assert the response
    assert response.status_code == 200
    assert "event_id" in response.json()
    assert response.json()["message"] == "Event created successfully"