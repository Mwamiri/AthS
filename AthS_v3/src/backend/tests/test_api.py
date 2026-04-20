import pytest

from app import create_app, db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SECRET_KEY"] = "test-secret-key-for-testing-only-min-32-chars"
    app.config["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-testing-only-min-32-chars"
    app.config["RATELIMIT_ENABLED"] = False
    app.config["TALISMAN_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "service" in data


def test_get_athletes(client):
    """Test get athletes endpoint."""
    response = client.get("/api/data/athletes")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)


def test_get_events(client):
    """Test get events endpoint."""
    response = client.get("/api/data/events")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)


def test_get_competitions(client):
    """Test get competitions endpoint."""
    response = client.get("/api/data/competitions")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)


def test_get_summary(client):
    """Test get summary endpoint."""
    response = client.get("/api/data/summary")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "athletes" in data["data"]
    assert "events" in data["data"]
    assert "performances" in data["data"]
    assert "competitions" in data["data"]


def test_not_found(client):
    """Test 404 error handler."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "message" in data
    assert "request_id" in data


def test_request_id_header(client):
    """Test that request ID is returned in headers."""
    response = client.get("/api/health")
    assert "X-Request-ID" in response.headers
