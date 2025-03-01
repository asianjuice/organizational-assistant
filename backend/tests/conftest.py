import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine
from backend.app.utils.database import Task, PomodoroSession

# Create a TestClient instance
client = TestClient(app)

# Fixture to set up and tear down the database
@pytest.fixture(scope="module")
def setup_database():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables after tests are done
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
def test_fetch_google_calendar_events(db_session):
    # Mock data for the request
    start_time = datetime.now()
    end_time = start_time + timedelta(days=7)

    # Send the request
    response = client.post(
        "/calendar/events",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    )

    # Assert the response
    assert response.status_code == 200
    assert "events" in response.json()

# Test: Suggest Optimal Time Slots
def test_suggest_optimal_time_slots(db_session):
    # Mock data for the request
    start_time = datetime.now()
    end_time = start_time + timedelta(days=7)

    # Send the request
    response = client.post(
        "/calendar/suggest-time",
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    )

    # Assert the response
    assert response.status_code == 200
    assert "suggested_slots" in response.json()