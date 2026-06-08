from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)


def setup_function():
    # Reset activities to a known state before each test
    activities.clear()
    activities.update({
        "Test Activity": {
            "description": "A test activity",
            "schedule": "Now",
            "max_participants": 2,
            "participants": ["existing@school.edu"]
        }
    })


def test_successful_signup():
    resp = client.post("/activities/Test%20Activity/signup", params={"email": "new@school.edu"})
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up new@school.edu for Test Activity" in data["message"]
    assert any(p == "new@school.edu" for p in activities["Test Activity"]["participants"]) 


def test_duplicate_signup_returns_409():
    # First signup should succeed
    r1 = client.post("/activities/Test%20Activity/signup", params={"email": "dup@school.edu"})
    assert r1.status_code == 200

    # Second signup with same email should return 409
    r2 = client.post("/activities/Test%20Activity/signup", params={"email": "dup@school.edu"})
    assert r2.status_code == 409
    assert r2.json().get("detail") == "Student already signed up"


def test_activity_full_returns_409():
    # Fill activity to capacity
    activities["Test Activity"]["participants"] = ["p1@school.edu", "p2@school.edu"]

    r = client.post("/activities/Test%20Activity/signup", params={"email": "late@school.edu"})
    assert r.status_code == 409
    assert r.json().get("detail") == "Activity is full"
