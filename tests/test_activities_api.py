import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Robotics Club"
PARTICIPANT_EMAIL = "student@example.com"


@pytest.fixture
def client(monkeypatch):
    # Arrange
    test_activities = {
        ACTIVITY_NAME: {
            "description": "Build and program robots",
            "schedule": "Mondays after school",
            "max_participants": 3,
            "participants": [PARTICIPANT_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    # Act
    with TestClient(app_module.app, follow_redirects=False) as test_client:
        yield test_client


def test_root_redirects_to_frontend(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activities = {
        ACTIVITY_NAME: {
            "description": "Build and program robots",
            "schedule": "Mondays after school",
            "max_participants": 3,
            "participants": [PARTICIPANT_EMAIL],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    new_email = "new-student@example.com"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {new_email} for {ACTIVITY_NAME}"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [PARTICIPANT_EMAIL, new_email]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = PARTICIPANT_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == [PARTICIPANT_EMAIL]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{unknown_activity}/signup",
        params={"email": "new-student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    email = PARTICIPANT_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {ACTIVITY_NAME}"
    }
    participants = client.get("/activities").json()[ACTIVITY_NAME]["participants"]
    assert participants == []


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    email = "not-signed-up@example.com"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.delete(
        f"/activities/{unknown_activity}/signup",
        params={"email": PARTICIPANT_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}