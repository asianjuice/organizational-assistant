# backend/tests/test_study.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine, PomodoroSession, User

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

# Fixture to create a test user
@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(name="Test User", email="test@example.com", password="password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

# Test: Get study session recommendations
def test_get_study_recommendations(client, db_session, test_user):
    # Create a Pomodoro session for the test user
    start_time = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)

    session = PomodoroSession(
        start_time=start_time,
        end_time=end_time,
        user_id=test_user.id,  # Add this line
    )
    db_session.add(session)
    db_session.commit()

    # Get study session recommendations
    response = client.get(f"/api/study/recommendations/{test_user.id}")
    assert response.status_code == 200
    assert "recommendations" in response.json()
    assert len(response.json()["recommendations"]) > 0