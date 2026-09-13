import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.database.connection import Base
from app.database.session import get_db
from app.main import app
from app.models.announcement import Announcement
from app.models.community import Community, CommunityMembership
from app.models.profile import Profile
from app.models.resource import Resource
from app.models.roadmap import Roadmap, Module, Task, UserTaskProgress
from app.models.user import User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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


def _create_community(db, name):
    community = Community(name=name, description=f"{name} community", active_members_count=0)
    db.add(community)
    db.commit()
    db.refresh(community)
    return community


def _create_roadmap(db, community, title="Web Development Roadmap"):
    roadmap = Roadmap(community_id=community.id, title=title, description="Roadmap description", total_modules=1)
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    module = Module(roadmap_id=roadmap.id, order=1, title="Frontend Basics", description="Build the foundation")
    db.add(module)
    db.commit()
    db.refresh(module)

    task = Task(module_id=module.id, order=1, title="Build a landing page")
    db.add(task)
    db.commit()
    db.refresh(task)

    return roadmap, module, task


def test_approved_web_development_member_sees_real_dashboard_data(client, db_session):
    user = _create_user(db_session)
    programming = _create_community(db_session, "Programming")
    web = _create_community(db_session, "Web Development")
    roadmap, module, task = _create_roadmap(db_session, web, "Web Development Roadmap")

    db_session.add(CommunityMembership(user_id=user.id, community_id=web.id, status="approved"))
    db_session.add(UserTaskProgress(user_id=user.id, task_id=task.id, is_completed=True))
    db_session.add(Resource(community_id=web.id, title="HTML & CSS Guide", resource_type="PDF", difficulty="Beginner", url="https://example.com/web-guide", description="Guide"))
    db_session.add(Announcement(community_id=web.id, author_id=user.id, title="Launch Week", content="New web challenges are live"))
    db_session.add(Resource(community_id=programming.id, title="Programming Guide", resource_type="PDF", difficulty="Advanced", url="https://example.com/prog-guide", description="Other"))
    db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    response = client.get(
        f"/api/v1/communities/{web.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["user_name"] == "Student User"
    assert payload["community_name"] == "Web Development"
    assert payload["roadmap"]["title"] == "Web Development Roadmap"
    assert payload["roadmap"]["modules"][0]["title"] == "Frontend Basics"
    assert payload["stats"]["completed_tasks_count"] == 1
    assert len(payload["resources"]) == 1
    assert payload["resources"][0]["title"] == "HTML & CSS Guide"
    assert len(payload["announcements"]) == 1
    assert payload["announcements"][0]["title"] == "Launch Week"


def test_pending_web_member_is_denied_dashboard_access(client, db_session):
    user = _create_user(db_session)
    web = _create_community(db_session, "Web Development")
    db_session.add(CommunityMembership(user_id=user.id, community_id=web.id, status="pending"))
    db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    response = client.get(
        f"/api/v1/communities/{web.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "approved member" in response.json()["detail"].lower()


def test_web_dashboard_uses_community_scoped_data_only(client, db_session):
    user = _create_user(db_session)
    programming = _create_community(db_session, "Programming")
    web = _create_community(db_session, "Web Development")
    _create_roadmap(db_session, programming, "Programming Roadmap")
    _create_roadmap(db_session, web, "Web Development Roadmap")
    db_session.add(CommunityMembership(user_id=user.id, community_id=web.id, status="approved"))
    db_session.add(Resource(community_id=programming.id, title="Programming Only", resource_type="PDF", difficulty="Advanced", url="https://example.com/bad", description="Wrong"))
    db_session.add(Resource(community_id=web.id, title="Web Only", resource_type="Video", difficulty="Beginner", url="https://example.com/good", description="Right"))
    db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    response = client.get(
        f"/api/v1/communities/{web.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert all(item["title"] != "Programming Only" for item in payload["resources"])
    assert any(item["title"] == "Web Only" for item in payload["resources"])


def test_unauthenticated_user_cannot_access_web_dashboard(client, db_session):
    web = _create_community(db_session, "Web Development")
    response = client.get(f"/api/v1/communities/{web.id}/dashboard")
    assert response.status_code == 401
