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

# Test: Create a new task with AI-powered priority suggestion
def test_create_task_with_ai_priority(client, db_session):
    due_date = datetime.utcnow() + timedelta(days=2)  # 2 days until deadline
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "due_date": due_date.isoformat(),
            "task_length": 5,  # Estimated task length in hours
        },
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert "priority" in response.json()
    assert response.json()["priority"] in ["high", "medium", "low"]

# Test: Create a new task with user-provided priority
def test_create_task_with_user_priority(client, db_session):
    due_date = datetime.utcnow() + timedelta(days=2)  # 2 days until deadline
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",  # User-provided priority
            "due_date": due_date.isoformat(),
        },
    )
    assert response.status_code == 200
    assert "task_id" in response.json()
    assert "priority" in response.json()
    assert response.json()["priority"] == "high"

# Test: Create a new task without priority or task_length (should fail)
def test_create_task_without_priority_or_task_length(client, db_session):
    due_date = datetime.utcnow() + timedelta(days=2)  # 2 days until deadline
    response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "due_date": due_date.isoformat(),
        },
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "task_length is required when priority is not provided" in response.json()["detail"]

# Test: Retrieve all tasks
def test_get_tasks(client, db_session):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )

    # Retrieve all tasks
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

# Test: Update a task
def test_update_task(client, db_session):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )
    task_id = create_response.json()["task_id"]

    # Update the task
    updated_due_date = datetime.utcnow() + timedelta(days=3)
    update_response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "title": "Updated Task",
            "description": "Updated description",
            "priority": "medium",
            "due_date": updated_due_date.isoformat(),
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task"
    assert update_response.json()["priority"] == "medium"

# Test: Delete a task
def test_delete_task(client, db_session):
    # Create a task first
    due_date = datetime.utcnow() + timedelta(days=2)
    create_response = client.post(
        "/api/tasks/",
        json={
            "title": "Learn AI",
            "description": "Study machine learning basics",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )
    task_id = create_response.json()["task_id"]

    # Delete the task
    delete_response = client.delete(f"/api/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Task deleted"

# Test: Retrieve tasks with description "Class"
def test_get_class_tasks(client, db_session):
    # Create a task with description "Class"
    due_date = datetime.utcnow() + timedelta(days=2)
    client.post(
        "/api/tasks/",
        json={
            "title": "Math Class",
            "description": "Class",
            "priority": "high",
            "due_date": due_date.isoformat(),
        },
    )

    # Retrieve tasks with description "Class"
    response = client.get("/api/tasks/classes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert all(task["description"] == "Class" for task in response.json())