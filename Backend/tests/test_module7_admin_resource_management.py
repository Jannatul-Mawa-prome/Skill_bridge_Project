import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.database.connection import Base
from app.database.session import get_db
from app.main import app
from app.models.community import Community, CommunityMembership
from app.models.profile import Profile
from app.models.resource import Resource
from app.models.roadmap import Roadmap, Module
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


def _create_roadmap_and_module(db, community, title="Roadmap"):
    roadmap = Roadmap(community_id=community.id, title=title, description="Roadmap description", total_modules=0)
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    module = Module(roadmap_id=roadmap.id, order=1, title="Intro Module", description="Module description")
    db.add(module)
    db.commit()
    db.refresh(module)

    roadmap.total_modules = 1
    db.commit()
    return roadmap, module


def test_admin_can_create_and_edit_resource(client, db_session):
    admin = _create_admin(db_session)
    community = _create_community(db_session, "Programming")
    _, module = _create_roadmap_and_module(db_session, community)
    token = create_access_token({"sub": str(admin.id)})

    response = client.post(
        "/api/v1/resources/",
        json={
            "community_id": community.id,
            "module_id": module.id,
            "title": "Beginner Guide",
            "resource_type": "Article",
            "difficulty": "Beginner",
            "url": "https://example.com/guide",
            "description": "Helpful notes"
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    resource_id = response.json()["id"]

    edit_response = client.put(
        f"/api/v1/resources/{resource_id}",
        json={
            "title": "Updated Beginner Guide",
            "resource_type": "Tutorial",
            "difficulty": "Intermediate",
            "url": "https://example.com/updated-guide",
            "description": "Updated notes"
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert edit_response.status_code == 200, edit_response.text
    payload = edit_response.json()
    assert payload["title"] == "Updated Beginner Guide"
    assert payload["resource_type"] == "Tutorial"
    assert payload["difficulty"] == "Intermediate"


def test_delete_disables_resource_and_student_dashboard_reflects_it(client, db_session):
    admin = _create_admin(db_session)
    student = _create_user(db_session)
    community = _create_community(db_session, "Programming")
    _, module = _create_roadmap_and_module(db_session, community)
    token = create_access_token({"sub": str(admin.id)})
    student_token = create_access_token({"sub": str(student.id)})

    db_session.add(CommunityMembership(user_id=student.id, community_id=community.id, status="approved"))
    db_session.commit()

    resource = Resource(
        community_id=community.id,
        module_id=module.id,
        title="Programming Resource",
        resource_type="Video",
        difficulty="Beginner",
        url="https://example.com/video",
        description="Will be removed",
        is_active=True,
    )
    db_session.add(resource)
    db_session.commit()
    db_session.refresh(resource)

    dashboard_before = client.get(
        f"/api/v1/communities/{community.id}/dashboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert dashboard_before.status_code == 200
    assert any(item["title"] == "Programming Resource" for item in dashboard_before.json()["resources"])

    delete_response = client.delete(
        f"/api/v1/resources/{resource.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200, delete_response.text

    dashboard_after = client.get(
        f"/api/v1/communities/{community.id}/dashboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert dashboard_after.status_code == 200
    assert all(item["title"] != "Programming Resource" for item in dashboard_after.json()["resources"])


def test_student_dashboard_only_shows_community_specific_active_resources(client, db_session):
    admin = _create_admin(db_session)
    student = _create_user(db_session)
    programming = _create_community(db_session, "Programming")
    web = _create_community(db_session, "Web Development")
    token = create_access_token({"sub": str(admin.id)})
    student_token = create_access_token({"sub": str(student.id)})

    db_session.add(CommunityMembership(user_id=student.id, community_id=programming.id, status="approved"))
    db_session.commit()

    db_session.add(Resource(community_id=programming.id, title="Programming Only", resource_type="Article", difficulty="Beginner", url="https://example.com/prog", description="Programming", is_active=True))
    db_session.add(Resource(community_id=web.id, title="Web Only", resource_type="Documentation", difficulty="Intermediate", url="https://example.com/web", description="Web", is_active=True))
    db_session.commit()

    response = client.get(
        f"/api/v1/communities/{programming.id}/dashboard",
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert all(item["title"] != "Web Only" for item in payload["resources"])
    assert any(item["title"] == "Programming Only" for item in payload["resources"])


def test_non_admin_cannot_manage_resources(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session, "Programming")
    token = create_access_token({"sub": str(user.id)})

    response = client.post(
        "/api/v1/resources/",
        json={
            "community_id": community.id,
            "title": "Bad Resource",
            "resource_type": "Article",
            "url": "https://example.com/bad"
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
