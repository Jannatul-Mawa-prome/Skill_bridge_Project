import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.database.connection import Base
from app.database.session import get_db
from app.main import app
from app.models.community import Community
from app.models.profile import Profile
from app.models.roadmap import Roadmap, Module, Task
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


def _create_admin(db, email="admin@skillbridge.test", name="Admin User"):
    user = User(edu_email=email, password_hash=hash_password("secret123"), is_active=True, role="admin")
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = Profile(user_id=user.id, full_name=name, roll="admin01", semester="1", mobile="0000000000")
    db.add(profile)
    db.commit()
    return user


def _create_user(db, email="student@skillbridge.test", name="Student User"):
    user = User(edu_email=email, password_hash=hash_password("secret123"), is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = Profile(user_id=user.id, full_name=name, roll="2024001", semester="1", mobile="0123456789")
    db.add(profile)
    db.commit()
    return user


def _create_community(db, name):
    community = Community(name=name, description=f"{name} community", active_members_count=0)
    db.add(community)
    db.commit()
    db.refresh(community)
    return community


def test_admin_can_create_and_edit_roadmap(client, db_session):
    admin = _create_admin(db_session)
    community = _create_community(db_session, "Programming")
    token = create_access_token({"sub": str(admin.id)})

    response = client.post(
        "/api/v1/roadmaps/",
        json={"community_id": community.id, "title": "New Programming Roadmap", "description": "Updated description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    roadmap_id = response.json()["id"]

    response = client.put(
        f"/api/v1/roadmaps/{roadmap_id}",
        json={"title": "Updated Programming Roadmap", "description": "New description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["title"] == "Updated Programming Roadmap"
    assert payload["description"] == "New description"


def test_admin_can_manage_modules_and_tasks(client, db_session):
    admin = _create_admin(db_session)
    community = _create_community(db_session, "Web Development")
    token = create_access_token({"sub": str(admin.id)})

    roadmap_response = client.post(
        "/api/v1/roadmaps/",
        json={"community_id": community.id, "title": "Web Roadmap", "description": "Initial"},
        headers={"Authorization": f"Bearer {token}"},
    )
    roadmap_id = roadmap_response.json()["id"]

    module_response = client.post(
        f"/api/v1/roadmaps/{roadmap_id}/modules",
        json={"order": 1, "title": "HTML Basics", "description": "Intro"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert module_response.status_code == 200, module_response.text
    module_id = module_response.json()["id"]

    task_response = client.post(
        f"/api/v1/roadmaps/modules/{module_id}/tasks",
        json={"order": 1, "title": "Build a form"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert task_response.status_code == 200, task_response.text
    task_id = task_response.json()["id"]

    edit_module = client.put(
        f"/api/v1/roadmaps/modules/{module_id}",
        json={"order": 2, "title": "HTML & CSS Basics", "description": "Updated"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert edit_module.status_code == 200, edit_module.text
    assert edit_module.json()["title"] == "HTML & CSS Basics"

    edit_task = client.put(
        f"/api/v1/roadmaps/tasks/{task_id}",
        json={"order": 2, "title": "Build a responsive form"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert edit_task.status_code == 200, edit_task.text
    assert edit_task.json()["title"] == "Build a responsive form"

    delete_task = client.delete(
        f"/api/v1/roadmaps/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_task.status_code == 200, delete_task.text

    delete_module = client.delete(
        f"/api/v1/roadmaps/modules/{module_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_module.status_code == 200, delete_module.text


def test_admin_can_delete_roadmap_and_dashboard_updates(client, db_session):
    admin = _create_admin(db_session)
    student = _create_user(db_session)
    community = _create_community(db_session, "Programming")
    token = create_access_token({"sub": str(admin.id)})
    student_token = create_access_token({"sub": str(student.id)})

    roadmap_response = client.post(
        "/api/v1/roadmaps/",
        json={"community_id": community.id, "title": "Programming Roadmap", "description": "Initial roadmap"},
        headers={"Authorization": f"Bearer {token}"},
    )
    roadmap_id = roadmap_response.json()["id"]

    module_response = client.post(
        f"/api/v1/roadmaps/{roadmap_id}/modules",
        json={"order": 1, "title": "Intro Module", "description": "Intro"},
        headers={"Authorization": f"Bearer {token}"},
    )
    module_id = module_response.json()["id"]

    task_response = client.post(
        f"/api/v1/roadmaps/modules/{module_id}/tasks",
        json={"order": 1, "title": "Learn syntax"},
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = task_response.json()["id"]

    db_session.add(__import__('app.models.community', fromlist=['CommunityMembership']).CommunityMembership(user_id=student.id, community_id=community.id, status="approved"))
    db_session.commit()

    dashboard_before = client.get(
        f"/api/v1/communities/{community.id}/dashboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert dashboard_before.status_code == 200
    assert dashboard_before.json()["roadmap"]["title"] == "Programming Roadmap"

    delete_response = client.delete(
        f"/api/v1/roadmaps/{roadmap_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200, delete_response.text

    dashboard_after = client.get(
        f"/api/v1/communities/{community.id}/dashboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert dashboard_after.status_code == 200, dashboard_after.text
    assert dashboard_after.json()["roadmap"] is None


def test_non_admin_cannot_manage_roadmap(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session, "Programming")
    token = create_access_token({"sub": str(user.id)})

    response = client.post(
        "/api/v1/roadmaps/",
        json={"community_id": community.id, "title": "Wrong"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
