import pytest
from fastapi.testclient import TestClient
from datetime import datetime
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

# Test: Create a new goal
def test_create_goal(client, db_session):
    response = client.post(
        "/api/habits-goals/goals/",
        json={
            "title": "Learn Python",
            "description": "Complete a Python course",
            "category": "academic",
            "user_id": 1,
        },
    )
    assert response.status_code == 200
    assert "goal_id" in response.json()

# Test: Retrieve all goals for a user
def test_get_goals(client, db_session):
    # Create a goal first
    client.post(
        "/api/habits-goals/goals/",
        json={
            "title": "Learn Python",
            "description": "Complete a Python course",
            "category": "academic",
            "user_id": 1,
        },
    )

    # Retrieve goals for the user
    response = client.get("/api/habits-goals/goals/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# Test: Create a new habit
def test_create_habit(client, db_session):
    response = client.post(
        "/api/habits-goals/habits/",
        json={
            "title": "Exercise daily",
            "description": "Do 30 minutes of exercise every day",
            "user_id": 1,
        },
    )
    assert response.status_code == 200
    assert "habit_id" in response.json()

# Test: Mark a habit as completed
def test_complete_habit(client, db_session):
    # Create a habit first
    create_response = client.post(
        "/api/habits-goals/habits/",
        json={
            "title": "Exercise daily",
            "description": "Do 30 minutes of exercise every day",
            "user_id": 1,
        },
    )
    assert create_response.status_code == 200
    habit_id = create_response.json()["habit_id"]

    # Mark the habit as completed
    complete_response = client.post(
        "/api/habits-goals/habits/complete/",
        json={
            "habit_id": habit_id,
            "completed_at": datetime.utcnow().isoformat() + "Z",
        },
    )
    assert complete_response.status_code == 200
    assert "streak" in complete_response.json()

# Test: Retrieve all habits for a user
def test_get_habits(client, db_session):
    # Create a habit first
    client.post(
        "/api/habits-goals/habits/",
        json={
            "title": "Exercise daily",
            "description": "Do 30 minutes of exercise every day",
            "user_id": 1,
        },
    )

    # Retrieve habits for the user
    response = client.get("/api/habits-goals/habits/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0