import pytest
from fastapi.testclient import TestClient


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check that each activity has the required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_for_activity(client: TestClient):
    """Test signing up for an activity"""
    # First get the activities to find one to sign up for
    response = client.get("/activities")
    activities = response.json()

    # Pick the first activity
    activity_name = list(activities.keys())[0]
    initial_participants = activities[activity_name]["participants"].copy()

    # Sign up a new student
    test_email = "test.student@mergington.edu"
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]

    # Verify the student was added
    response = client.get("/activities")
    activities = response.json()
    assert test_email in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(initial_participants) + 1


def test_signup_duplicate(client: TestClient):
    """Test signing up for the same activity twice"""
    # First get the activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Sign up a student
    test_email = "duplicate.test@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )

    # Try to sign up again
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client: TestClient):
    """Test signing up for a nonexistent activity"""
    response = client.post(
        "/activities/NonexistentActivity/signup",
        params={"email": "test@mergington.edu"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_unregister_from_activity(client: TestClient):
    """Test unregistering from an activity"""
    # First get the activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Sign up a student first
    test_email = "unregister.test@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": test_email}
    )

    # Get initial count
    response = client.get("/activities")
    activities = response.json()
    initial_count = len(activities[activity_name]["participants"])

    # Unregister the student
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": test_email}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert test_email in data["message"]

    # Verify the student was removed
    response = client.get("/activities")
    activities = response.json()
    assert test_email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1


def test_unregister_not_signed_up(client: TestClient):
    """Test unregistering a student who is not signed up"""
    # First get the activities
    response = client.get("/activities")
    activities = response.json()
    activity_name = list(activities.keys())[0]

    # Try to unregister a student who is not signed up
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": "notsignedup@mergington.edu"}
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity(client: TestClient):
    """Test unregistering from a nonexistent activity"""
    response = client.delete(
        "/activities/NonexistentActivity/unregister",
        params={"email": "test@mergington.edu"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_root_redirect(client: TestClient):
    """Test that root path redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200  # FastAPI handles the redirect internally in tests
    # The redirect response should point to the static file
    # In test client, redirects are followed by default