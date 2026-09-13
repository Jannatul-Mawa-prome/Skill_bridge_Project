import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token, hash_password
from app.database.connection import Base
from app.main import app
from app.database.session import get_db
from app.models.community import Community, CommunityMembership, AssessmentData
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


def test_join_request_creates_pending_request_and_not_approved(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session)
    token = create_access_token({"sub": str(user.id)})

    response = client.post(
        f"/api/v1/communities/{community.id}/join",
        json={
            "skill_level": "beginner",
            "languages_known": ["python"],
            "problem_solving_comfort": "basic",
            "main_goal": "learn",
            "weekly_time_commitment": "2-5 hours"
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == "Successfully joined community" or "pending" in payload["message"].lower()

    membership = db_session.query(CommunityMembership).filter_by(user_id=user.id, community_id=community.id).first()
    assert membership is not None
    assert membership.status == "pending"
    assert membership.status != "approved"

    assessment = db_session.query(AssessmentData).filter_by(membership_id=membership.id).first()
    assert assessment is not None
    assert "python" in assessment.languages_known


def test_duplicate_pending_request_rejected(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session)
    token = create_access_token({"sub": str(user.id)})

    first = client.post(
        f"/api/v1/communities/{community.id}/join",
        json={
            "skill_level": "beginner",
            "languages_known": ["python"],
            "problem_solving_comfort": "basic",
            "main_goal": "learn",
            "weekly_time_commitment": "2-5 hours"
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/communities/{community.id}/join",
        json={
            "skill_level": "intermediate",
            "languages_known": ["java"],
            "problem_solving_comfort": "comfortable",
            "main_goal": "competitive",
            "weekly_time_commitment": "5-10 hours"
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert second.status_code == 400, second.text
    assert "pending request" in second.json()["detail"].lower()

    memberships = db_session.query(CommunityMembership).filter_by(user_id=user.id, community_id=community.id).all()
    assert len(memberships) == 1


def test_existing_approved_member_cannot_submit_new_request(client, db_session):
    user = _create_user(db_session)
    community = _create_community(db_session)
    token = create_access_token({"sub": str(user.id)})

    membership = CommunityMembership(user_id=user.id, community_id=community.id, status="approved")
    db_session.add(membership)
    db_session.commit()

    response = client.post(
        f"/api/v1/communities/{community.id}/join",
        json={
            "skill_level": "advanced",
            "languages_known": ["javascript"],
            "problem_solving_comfort": "advanced",
            "main_goal": "projects",
            "weekly_time_commitment": "10+ hours"
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400, response.text
    assert "already a member" in response.json()["detail"].lower()

    memberships = db_session.query(CommunityMembership).filter_by(user_id=user.id, community_id=community.id).all()
    assert len(memberships) == 1
    assert memberships[0].status == "approved"
