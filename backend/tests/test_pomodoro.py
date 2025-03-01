import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine
from backend.app.utils.database import PomodoroSession, Task, TaskPriority  # Import TaskPriority

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

# Test: Start a Pomodoro session
def test_start_pomodoro_session(db_session):
    # Create a task to link to the Pomodoro session
    task = Task(title="Test Task", description="Test Description", priority=TaskPriority.MEDIUM, due_date=datetime.now())
    db_session.add(task)
    db_session.commit()

    # Start a Pomodoro session
    response = client.post(
        "/pomodoro/start",
        json={
            "start_time": datetime.now().isoformat(),
            "task_id": task.id,
        },
    )
    assert response.status_code == 200
    assert "session_id" in response.json()

# Test: End a Pomodoro session
def test_end_pomodoro_session(db_session):
    # Create a Pomodoro session
    session = PomodoroSession(start_time=datetime.now(), status="running", task_id=None)
    db_session.add(session)
    db_session.commit()

    # End the Pomodoro session
    response = client.post(
        f"/pomodoro/end/{session.id}",
        json={
            "end_time": (datetime.now() + timedelta(minutes=25)).isoformat(),
        },
    )
    assert response.status_code == 200
    assert "duration_minutes" in response.json()

# Test: Get all Pomodoro sessions
def test_get_all_pomodoro_sessions(db_session):
    # Create a Pomodoro session
    session = PomodoroSession(start_time=datetime.now(), status="running", task_id=None)
    db_session.add(session)
    db_session.commit()

    # Get all Pomodoro sessions
    response = client.get("/pomodoro/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# Test: Export Pomodoro logs
def test_export_pomodoro_logs(db_session):
    # Create a Pomodoro session
    session = PomodoroSession(start_time=datetime.now(), status="running", task_id=None)
    db_session.add(session)
    db_session.commit()

    # Export Pomodoro logs
    response = client.get("/pomodoro/export-logs")
    assert response.status_code == 200
    assert "message" in response.json()

# Test: Get weekly productivity trends
def test_get_weekly_trends(db_session):
    # Create a Pomodoro session
    session = PomodoroSession(
        start_time=datetime.now() - timedelta(days=1),
        end_time=datetime.now() - timedelta(days=1) + timedelta(minutes=25),
        status="completed",
        task_id=None,
    )
    db_session.add(session)
    db_session.commit()

    # Get weekly productivity trends
    response = client.get("/pomodoro/weekly-trends")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert len(response.json()) > 0