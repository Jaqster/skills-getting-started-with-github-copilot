import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200(client):
    # Arrange: pre-seeded data is available via the app
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200


def test_get_activities_returns_dict(client):
    # Arrange: pre-seeded data is available via the app
    # Act
    response = client.get("/activities")
    data = response.json()
    # Assert
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_known_activity(client):
    # Arrange: pre-seeded data is available via the app
    # Act
    response = client.get("/activities")
    # Assert
    assert "Chess Club" in response.json()


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_returns_message(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert "message" in response.json()


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404


def test_signup_already_registered_returns_400(client):
    # Arrange: michael@mergington.edu is pre-seeded in Chess Club
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


def test_signup_full_activity_returns_400(client):
    # Arrange: fill Chess Club to its max_participants (12)
    activity_name = "Chess Club"
    for i in range(activities[activity_name]["max_participants"] - len(activities[activity_name]["participants"])):
        activities[activity_name]["participants"].append(f"filler{i}@mergington.edu")
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")
    # Assert
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange: michael@mergington.edu is pre-seeded in Chess Club
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_message(client):
    # Arrange: michael@mergington.edu is pre-seeded in Chess Club
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert "message" in response.json()


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "michael@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404


def test_unregister_not_registered_returns_404(client):
    # Arrange: this email is not in any activity
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    # Assert
    assert response.status_code == 404
