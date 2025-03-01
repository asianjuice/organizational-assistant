# backend/tests/test_pomodoro_websocket.py

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app  # Import your FastAPI app

# Fixture to provide a TestClient instance
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client

# Test: WebSocket for Pomodoro timer
def test_pomodoro_websocket(client):
    with client.websocket_connect("/api/pomodoro/timer") as websocket:
        try:
            # Receive messages from the WebSocket for a short duration
            for _ in range(5):  # Test the first 5 seconds of the timer
                data = websocket.receive_text()
                assert data.startswith("Time remaining:")  # Check the format of the message
        except Exception as e:
            # Handle WebSocket disconnection or other errors
            pytest.fail(f"WebSocket error: {e}")
        finally:
            # Close the WebSocket connection
            websocket.close()