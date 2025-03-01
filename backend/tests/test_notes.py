# backend/tests/test_notes.py

import pytest
from fastapi.testclient import TestClient
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

# Test: Create a note
def test_create_note(client, db_session):
    response = client.post(
        "/api/notes/",
        json={
            "title": "Test Note",
            "content": "This is a test note",
            "subject": "Math",
            "tags": ["algebra", "calculus"],
            "user_id": 1,  # Ensure this line is present
        },
    )
    assert response.status_code == 200
    assert "note_id" in response.json()

# Test: Retrieve notes by subject
def test_get_notes_by_subject(client, db_session):
    response = client.get("/api/notes/subject/Math")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test: Retrieve notes by tag
def test_get_notes_by_tag(client, db_session):
    response = client.get("/api/notes/tag/algebra")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test: Update a note
def test_update_note(client, db_session):
    # Create a note first
    create_response = client.post(
        "/api/notes/",
        json={
            "title": "Test Note",
            "content": "This is a test note",
            "subject": "Math",
            "tags": ["algebra", "calculus"],
            "user_id": 1,  # Ensure this line is present
        },
    )
    assert create_response.status_code == 200
    note_id = create_response.json()["note_id"]

    # Update the note
    update_response = client.put(
        f"/api/notes/{note_id}",
        json={
            "title": "Updated Note",
            "content": "This is an updated note",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Note"

# Test: Delete a note
def test_delete_note(client, db_session):
    # Create a note first
    create_response = client.post(
        "/api/notes/",
        json={
            "title": "Test Note",
            "content": "This is a test note",
            "subject": "Math",
            "tags": ["algebra", "calculus"],
            "user_id": 1,  # Ensure this line is present
        },
    )
    assert create_response.status_code == 200
    note_id = create_response.json()["note_id"]

    # Delete the note
    delete_response = client.delete(f"/api/notes/{note_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Note deleted"