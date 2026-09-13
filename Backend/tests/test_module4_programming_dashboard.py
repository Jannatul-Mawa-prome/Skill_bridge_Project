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


def _create_roadmap(db, community, title="Programming Roadmap"):
    roadmap = Roadmap(community_id=community.id, title=title, description="Roadmap description", total_modules=1)
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    module = Module(roadmap_id=roadmap.id, order=1, title="Intro Module", description="Module description")
    db.add(module)
    db.commit()
    db.refresh(module)

    task = Task(module_id=module.id, order=1, title="First task")
    db.add(task)
    db.commit()
    db.refresh(task)

    return roadmap, module, task


def test_approved_programming_member_sees_real_dashboard_data(client, db_session):
    user = _create_user(db_session)
    programming = _create_community(db_session, "Programming")
    web = _create_community(db_session, "Web Development")
    roadmap, module, task = _create_roadmap(db_session, programming)

    db_session.add(CommunityMembership(user_id=user.id, community_id=programming.id, status="approved"))
    db_session.add(UserTaskProgress(user_id=user.id, task_id=task.id, is_completed=True))
    db_session.add(Resource(community_id=programming.id, title="Programming Guide", resource_type="PDF", difficulty="Beginner", url="https://example.com/p-guide", description="Guide"))
    db_session.add(Announcement(community_id=programming.id, author_id=user.id, title="Welcome", content="Welcome to the programming community"))
    db_session.add(Resource(community_id=web.id, title="Web Guide", resource_type="Article", difficulty="Beginner", url="https://example.com/w-guide", description="Other"))
    db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    response = client.get(
        f"/api/v1/communities/{programming.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["user_name"] == "Student User"
    assert payload["community_name"] == "Programming"
    assert payload["roadmap"]["title"] == "Programming Roadmap"
    assert payload["roadmap"]["modules"][0]["title"] == "Intro Module"
    assert payload["roadmap"]["modules"][0]["tasks"][0]["title"] == "First task"
    assert payload["stats"]["completed_tasks_count"] == 1
    assert len(payload["resources"]) == 1
    assert payload["resources"][0]["title"] == "Programming Guide"
    assert len(payload["announcements"]) == 1
    assert payload["announcements"][0]["title"] == "Welcome"


def test_pending_users_are_denied_dashboard_access(client, db_session):
    user = _create_user(db_session)
    programming = _create_community(db_session, "Programming")
    db_session.add(CommunityMembership(user_id=user.id, community_id=programming.id, status="pending"))
    db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    response = client.get(
        f"/api/v1/communities/{programming.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "approved member" in response.json()["detail"].lower()


def test_unapproved_other_community_is_blocked(client, db_session):
    user = _create_user(db_session)
    programming = _create_community(db_session, "Programming")
    web = _create_community(db_session, "Web Development")
    db_session.add(CommunityMembership(user_id=user.id, community_id=programming.id, status="approved"))
    db_session.commit()

    token = create_access_token({"sub": str(user.id)})
    response = client.get(
        f"/api/v1/communities/{web.id}/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_unauthenticated_user_cannot_access_dashboard(client, db_session):
    programming = _create_community(db_session, "Programming")
    response = client.get(f"/api/v1/communities/{programming.id}/dashboard")
    assert response.status_code == 401
