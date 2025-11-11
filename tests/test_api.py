from fastapi.testclient import TestClient
import pytest
import sys
from pathlib import Path

# Ensure the workspace root is on sys.path so we can import `src.app`
workspace_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(workspace_root))

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    # Provide a small predictable activities dataset for every test
    app_module.activities = {
        "Test Club": {
            "description": "A test activity",
            "schedule": "Now",
            "max_participants": 5,
            "participants": ["alice@example.com"]
        },
        "Empty Club": {
            "description": "Empty activity",
            "schedule": "Soon",
            "max_participants": 10,
            "participants": []
        }
    }
    yield


@pytest.fixture()
def client():
    return TestClient(app_module.app)


def test_get_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Test Club" in data
    assert data["Test Club"]["description"] == "A test activity"


def test_signup_and_see_participant(client):
    email = "bob@example.com"
    res = client.post(f"/activities/Test%20Club/signup?email={email}")
    assert res.status_code == 200
    assert "Signed up" in res.json().get("message", "")

    # Participant should now appear in activities
    res2 = client.get("/activities")
    assert res2.status_code == 200
    participants = res2.json()["Test Club"]["participants"]
    assert email in participants


def test_signup_duplicate_returns_400(client):
    email = "alice@example.com"
    # alice already exists in Test Club from the fixture
    res = client.post(f"/activities/Test%20Club/signup?email={email}")
    assert res.status_code == 400


def test_remove_participant(client):
    email = "alice@example.com"
    res = client.delete(f"/activities/Test%20Club/participants?email={email}")
    assert res.status_code == 200
    assert "Removed" in res.json().get("message", "")

    res2 = client.get("/activities")
    assert email not in res2.json()["Test Club"]["participants"]


def test_remove_nonexistent_returns_404(client):
    email = "notfound@example.com"
    res = client.delete(f"/activities/Test%20Club/participants?email={email}")
    assert res.status_code == 404
