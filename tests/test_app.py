import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app import app, create_access_token, users_db
from datetime import timedelta

# Initialize the TestClient with the FastAPI app
client = TestClient(app)

# Helper to generate token for testing
def get_token(username: str, role: str):
    return create_access_token(data={"sub": username}, role=role, expires_delta=timedelta(minutes=60))

@pytest.fixture
def token():
    # Generate a valid token for the test user
    return get_token("admin", "admin")

@pytest.fixture
def user_token():
    # Generate a token for a regular user
    return get_token("user", "user")

# Test for the root endpoint
def test_get_hello():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"User": "Welcome to MLOPS"}

# Test the login endpoint
def test_login_success():
    response = client.post("/token", data={"username": "admin", "password": "adminpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/token", data={"username": "admin", "password": "wrongpass"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

# Test the generate_report endpoint with mocked image processing
@patch("app.BlipMed")
def test_generate_report(mock_blip, token):
    # Mock the generate_report method
    mock_blip.return_value.generate_report.return_value = "Mocked report"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open("test_image.jpg", "rb") as image:
        response = client.post("/generate_report/", headers=headers, files={"file": ("filename", image, "image/jpeg")}, data={"indication": "test indication"})
    
    assert response.status_code == 200
    assert response.json()["report"] == "Mocked report"

# Test the /vqa endpoint
@patch("app.BlipMed")
def test_question_image(mock_blip, token):
    mock_blip.return_value.generate_report.return_value = "Answer"
    headers = {"Authorization": f"Bearer {token}"}
    
    with open("test_image.jpg", "rb") as image:
        response = client.post("/vqa", headers=headers, files={"file": ("filename", image, "image/jpeg")}, data={"question": "What is in the image?"})
    
    assert response.status_code == 200
    assert response.json()["question"] == "What is in the image?"

# Test for the monitoring endpoint with admin role
@patch("app.generate_drift_report")
def test_monitoring_admin_access(mock_generate_drift_report, token):
    mock_generate_drift_report.return_value = "Mocked drift report"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/monitoring", headers=headers)
    assert response.status_code == 200

# Test for the monitoring endpoint with user role (should fail)
def test_monitoring_user_access(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/monitoring", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"