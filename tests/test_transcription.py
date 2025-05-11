import pytest
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_transcribe_no_file():
    response = client.post("/transcribe")
    assert response.status_code == 422  # Validation error

def test_transcribe_invalid_file():
    files = {"file": ("test.txt", b"not an audio file", "text/plain")}
    response = client.post("/transcribe", files=files)
    assert response.status_code == 400
    assert "Invalid audio file" in response.json()["detail"] 