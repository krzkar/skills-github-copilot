import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after every test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange - client is ready, activities pre-loaded

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activity_has_required_fields(self, client):
        # Arrange - client is ready, activities pre-loaded

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        for activity in data.values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email in participants

    def test_signup_unknown_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self, client):
        # Arrange - michael is already enrolled in Chess Club
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400


class TestUnregister:
    def test_unregister_success(self, client):
        # Arrange - michael is already enrolled in Chess Club
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        # Arrange - michael is already enrolled in Chess Club
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert email not in participants

    def test_unregister_unknown_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_not_enrolled_returns_404(self, client):
        # Arrange - nobody is not enrolled in Chess Club
        email = "nobody@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
