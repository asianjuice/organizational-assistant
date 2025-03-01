import pytest
from fastapi.testclient import TestClient
from backend.app.main import app  # Import your FastAPI app
from backend.app.utils.database import SessionLocal, Base, engine
import os

# Fixture to provide a TestClient instance
@pytest.fixture(scope="module")
def client():
    # Create a TestClient instance for the FastAPI app
    with TestClient(app) as client:
        yield client

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

# Test: Upload a file to Google Drive
def test_upload_file(client, db_session):
    # Create a dummy file
    file_path = "test_file.txt"
    with open(file_path, "w") as f:
        f.write("This is a test file.")

    # Upload the file
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/files/upload",
            files={"file": ("test_file.txt", f, "text/plain")},
        )

    # Assert the response
    assert response.status_code == 200
    assert "file_id" in response.json()

    # Clean up the dummy file
    os.remove(file_path)

# Test: List files in Google Drive
def test_list_files(client, db_session):
    response = client.get("/api/files/list")
    assert response.status_code == 200
    assert "files" in response.json()