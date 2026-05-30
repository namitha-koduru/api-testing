import pytest
from app import create_app
from app.extensions import db
from app.models import User, UserRole


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    user = User(
        email="test@test.com",
        username="testuser",
        role=UserRole.ATTENDEE,
        is_verified=True,
    )
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    res = client.post("/api/auth/login", json={"email": "test@test.com", "password": "password123"})
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "healthy"


def test_register(client):
    res = client.post("/api/auth/register", json={
        "email": "new@test.com",
        "username": "newuser",
        "password": "password123",
    })
    assert res.status_code == 201


def test_login(client):
    client.post("/api/auth/register", json={
        "email": "login@test.com",
        "username": "loginuser",
        "password": "password123",
    })
    res = client.post("/api/auth/login", json={"email": "login@test.com", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.get_json()


def test_events_list(client):
    res = client.get("/api/events")
    assert res.status_code == 200


def test_protected_route_without_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_protected_route_with_auth(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["email"] == "test@test.com"
