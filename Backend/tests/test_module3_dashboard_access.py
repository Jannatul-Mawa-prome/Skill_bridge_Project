import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, hash_password
from app.database.connection import Base
from app.database.session import get_db
from app.main import app
from app.models.community import Community, CommunityMembership
from app.models.profile import Profile
from app.models.user import User


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _create_user(db, email="student@skillbridge.test", name="Student User", roll="2024001"):
    user = User(edu_email=email, password_hash=hash_password("secret123"), is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = Profile(user_id=user.id, full_name=name, roll=roll, semester="1", mobile="0123456789")
    db.add(profile)
    db.commit()
    return user


def _create_community(db, name="Programming Community"):
    community = Community(name=name, description="Test community", active_members_count=0)
    db.add(community)
    db.commit()
    db.refresh(community)
    return community


def test_approved_member_can_access_dashboard(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session)
    token = create_access_token({"sub": str(user.id)})

    membership = CommunityMembership(user_id=user.id, community_id=community.id, status="approved")
    db_session.add(membership)
    db_session.commit()

    response = client.get(
        f"/api/v1/communities/{community.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["user_name"] == "Student User"
    assert payload["stats"]["current_streak_days"] == 0


def test_pending_member_cannot_access_dashboard(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session)
    token = create_access_token({"sub": str(user.id)})

    db_session.add(CommunityMembership(user_id=user.id, community_id=community.id, status="pending"))
    db_session.commit()

    response = client.get(
        f"/api/v1/communities/{community.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403, response.text
    assert "approved member" in response.json()["detail"].lower()


@pytest.mark.parametrize("status", ["rejected", "suspended"])
def test_non_approved_status_users_cannot_access_dashboard(client, db_session, status):
    user = _create_user(db_session)
    community = _create_community(db_session)
    token = create_access_token({"sub": str(user.id)})

    db_session.add(CommunityMembership(user_id=user.id, community_id=community.id, status=status))
    db_session.commit()

    response = client.get(
        f"/api/v1/communities/{community.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403, response.text
    assert "approved member" in response.json()["detail"].lower()


def test_unauthenticated_user_requires_login_for_dashboard(client, db_session):
    community = _create_community(db_session)

    response = client.get(f"/api/v1/communities/{community.id}/dashboard")

    assert response.status_code == 401, response.text


def test_programming_member_cannot_access_web_development_dashboard_without_approved_membership(client, db_session):
    user = _create_user(db_session)
    programming = _create_community(db_session, name="Programming Community")
    web = _create_community(db_session, name="Web Development Community")
    token = create_access_token({"sub": str(user.id)})

    db_session.add(CommunityMembership(user_id=user.id, community_id=programming.id, status="approved"))
    db_session.commit()

    response = client.get(
        f"/api/v1/communities/{web.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403, response.text
    assert "approved member" in response.json()["detail"].lower()


def test_membership_status_check_reflects_backend_state(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session)
    token = create_access_token({"sub": str(user.id)})

    db_session.add(CommunityMembership(user_id=user.id, community_id=community.id, status="pending"))
    db_session.commit()

    response = client.get(
        f"/api/v1/communities/{community.id}/membership",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "pending"
    assert body["is_member"] is False
