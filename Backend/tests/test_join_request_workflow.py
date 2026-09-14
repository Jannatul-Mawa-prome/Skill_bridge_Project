import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal
from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.profile import Profile
from app.models.community import Community, CommunityMembership
from app.models.community_question import CommunityQuestion
from app.models.community_answer import CommunityAnswer


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def test_setup():
    db = SessionLocal()

    # Find or ensure admin
    admin = db.query(User).filter_by(edu_email="admin@skillbridge.edu").first()
    if not admin:
        admin = User(
            edu_email="admin@skillbridge.edu",
            password_hash=hash_password("Admin@12345"),
            is_verified=True,
            is_active=True,
            is_admin=True,
        )
        admin.profile = Profile(
            full_name="Platform Admin",
            roll="ADMIN-001",
            semester="N/A",
            mobile="01700000000",
            department="CSE",
            university="DUET",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    admin_token = create_access_token({"sub": str(admin.id)})

    # Test user 1 for Programming
    user1 = db.query(User).filter_by(edu_email="test_prog_user@student.duet.ac.bd").first()
    if not user1:
        user1 = User(
            edu_email="test_prog_user@student.duet.ac.bd",
            password_hash=hash_password("Pass@12345"),
            is_verified=True,
            is_active=True,
            is_admin=False,
        )
        user1.profile = Profile(
            full_name="Programming Applicant",
            roll="PROG-001",
            semester="3rd",
            mobile="01711111111",
            department="CSE",
            university="DUET",
        )
        db.add(user1)
        db.commit()
        db.refresh(user1)

    user1_token = create_access_token({"sub": str(user1.id)})

    # Test user 2 for Web Dev
    user2 = db.query(User).filter_by(edu_email="test_web_user@student.duet.ac.bd").first()
    if not user2:
        user2 = User(
            edu_email="test_web_user@student.duet.ac.bd",
            password_hash=hash_password("Pass@12345"),
            is_verified=True,
            is_active=True,
            is_admin=False,
        )
        user2.profile = Profile(
            full_name="Web Applicant",
            roll="WEB-001",
            semester="4th",
            mobile="01722222222",
            department="CSE",
            university="DUET",
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

    user2_token = create_access_token({"sub": str(user2.id)})

    prog_comm = db.query(Community).filter(Community.name.ilike("%programming%")).first()
    web_comm = db.query(Community).filter(Community.name.ilike("%web%")).first()

    assert prog_comm is not None, "Programming community not found"
    assert web_comm is not None, "Web Dev community not found"

    admin_id = admin.id
    user1_id = user1.id
    user2_id = user2.id
    prog_comm_id = prog_comm.id
    web_comm_id = web_comm.id

    # Clean any previous test memberships for test users
    db.query(CommunityMembership).filter(
        CommunityMembership.user_id.in_([user1_id, user2_id])
    ).delete()
    db.commit()

    db.close()

    return {
        "admin_token": admin_token,
        "admin_id": admin_id,
        "user1_token": user1_token,
        "user1_id": user1_id,
        "user2_token": user2_token,
        "user2_id": user2_id,
        "prog_comm_id": prog_comm_id,
        "web_comm_id": web_comm_id,
    }


def test_programming_community_join_workflow(client, test_setup):
    token = test_setup["user1_token"]
    admin_token = test_setup["admin_token"]
    comm_id = test_setup["prog_comm_id"]
    headers = {"Authorization": f"Bearer {token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Check initial membership -> none
    res = client.get(f"/api/v1/communities/{comm_id}/membership", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "none"
    assert data["is_member"] is False

    # 2. Cannot access dashboard
    dash_res = client.get(f"/api/v1/communities/{comm_id}/dashboard", headers=headers)
    assert dash_res.status_code == 403

    # 3. Submit join request
    answers_payload = {
        "answers": [
            {"question_key": "skill_level", "value": "beginner"},
            {"question_key": "languages_known", "value": ["cpp", "python"]},
            {"question_key": "problem_solving_comfort", "value": "basic"},
            {"question_key": "main_goal", "value": "learn"},
            {"question_key": "weekly_time_commitment", "value": "4-7"},
        ]
    }
    join_res = client.post(f"/api/v1/communities/{comm_id}/join", json=answers_payload, headers=headers)
    assert join_res.status_code == 200
    join_data = join_res.json()
    assert join_data["status"] == "pending"
    membership_id = join_data["membership_id"]

    # 4. Membership status is now pending
    mem_res = client.get(f"/api/v1/communities/{comm_id}/membership", headers=headers)
    assert mem_res.status_code == 200
    mem_data = mem_res.json()
    assert mem_data["status"] == "pending"
    assert mem_data["is_member"] is False

    # 5. Dashboard still forbidden while pending
    dash_pending_res = client.get(f"/api/v1/communities/{comm_id}/dashboard", headers=headers)
    assert dash_pending_res.status_code == 403
    assert "pending" in dash_pending_res.json()["detail"].lower()

    # 6. Duplicate join request is rejected
    dup_res = client.post(f"/api/v1/communities/{comm_id}/join", json=answers_payload, headers=headers)
    assert dup_res.status_code == 400
    assert "pending" in dup_res.json()["detail"].lower()

    # 7. Request appears in Admin Panel
    admin_reqs_res = client.get("/api/v1/admin/join-requests", headers=admin_headers)
    assert admin_reqs_res.status_code == 200
    requests_list = admin_reqs_res.json()
    our_req = next((r for r in requests_list if r["membership_id"] == membership_id), None)
    assert our_req is not None
    assert our_req["student_email"] == "test_prog_user@student.duet.ac.bd"
    assert our_req["community_id"] == comm_id
    assert len(our_req["answers"]) == 5

    # 8. Admin approves request
    approve_res = client.post(f"/api/v1/admin/join-requests/{membership_id}/approve", headers=admin_headers)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"
    assert approve_res.json()["is_active"] is True

    # 9. Request no longer in pending join-requests
    admin_reqs_res2 = client.get("/api/v1/admin/join-requests", headers=admin_headers)
    requests_list2 = admin_reqs_res2.json()
    assert not any(r["membership_id"] == membership_id for r in requests_list2)

    # 10. User membership is now approved & active
    mem_res2 = client.get(f"/api/v1/communities/{comm_id}/membership", headers=headers)
    assert mem_res2.status_code == 200
    assert mem_res2.json()["status"] == "approved"
    assert mem_res2.json()["is_member"] is True

    # 11. User can now access dashboard
    dash_ok_res = client.get(f"/api/v1/communities/{comm_id}/dashboard", headers=headers)
    assert dash_ok_res.status_code == 200
    assert dash_ok_res.json()["community"]["id"] == comm_id

    # 12. Duplicate join request prevented after approved
    dup_appr_res = client.post(f"/api/v1/communities/{comm_id}/join", json=answers_payload, headers=headers)
    assert dup_appr_res.status_code == 400
    assert "already an approved member" in dup_appr_res.json()["detail"].lower()


def test_web_development_community_join_reject_reapply_workflow(client, test_setup):
    token = test_setup["user2_token"]
    admin_token = test_setup["admin_token"]
    comm_id = test_setup["web_comm_id"]
    headers = {"Authorization": f"Bearer {token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Check initial membership -> none
    res = client.get(f"/api/v1/communities/{comm_id}/membership", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "none"

    # 2. Cannot access dashboard
    dash_res = client.get(f"/api/v1/communities/{comm_id}/dashboard", headers=headers)
    assert dash_res.status_code == 403

    # 3. Submit join request
    answers_payload = {
        "answers": [
            {"question_key": "skill_level", "value": "intermediate"},
            {"question_key": "technologies_known", "value": ["html-css", "javascript", "react"]},
            {"question_key": "main_goal", "value": "projects"},
            {"question_key": "weekly_time_commitment", "value": "5-10"},
        ]
    }
    join_res = client.post(f"/api/v1/communities/{comm_id}/join", json=answers_payload, headers=headers)
    assert join_res.status_code == 200
    membership_id = join_res.json()["membership_id"]

    # 4. Appears in Admin Panel
    admin_reqs_res = client.get("/api/v1/admin/join-requests", headers=admin_headers)
    assert admin_reqs_res.status_code == 200
    our_req = next((r for r in admin_reqs_res.json() if r["membership_id"] == membership_id), None)
    assert our_req is not None
    assert our_req["student_email"] == "test_web_user@student.duet.ac.bd"
    assert len(our_req["answers"]) == 4

    # 5. Admin rejects request
    reject_res = client.post(f"/api/v1/admin/join-requests/{membership_id}/reject", headers=admin_headers)
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"
    assert reject_res.json()["is_active"] is False

    # 6. User membership status is rejected and not active
    mem_res = client.get(f"/api/v1/communities/{comm_id}/membership", headers=headers)
    assert mem_res.status_code == 200
    assert mem_res.json()["status"] == "rejected"
    assert mem_res.json()["is_member"] is False

    # 7. User cannot access dashboard
    dash_rej_res = client.get(f"/api/v1/communities/{comm_id}/dashboard", headers=headers)
    assert dash_rej_res.status_code == 403

    # 8. User can re-apply after rejection!
    reapply_payload = {
        "answers": [
            {"question_key": "skill_level", "value": "advanced"},
            {"question_key": "technologies_known", "value": ["html-css", "javascript", "react", "nodejs", "backend"]},
            {"question_key": "main_goal", "value": "job"},
            {"question_key": "weekly_time_commitment", "value": "10+"},
        ]
    }
    reapply_res = client.post(f"/api/v1/communities/{comm_id}/join", json=reapply_payload, headers=headers)
    assert reapply_res.status_code == 200
    assert reapply_res.json()["status"] == "pending"

    # 9. Membership status is pending again
    mem_reapply_res = client.get(f"/api/v1/communities/{comm_id}/membership", headers=headers)
    assert mem_reapply_res.status_code == 200
    assert mem_reapply_res.json()["status"] == "pending"
    assert mem_reapply_res.json()["is_member"] is False

    # 10. Duplicate request rejected while pending
    dup_res = client.post(f"/api/v1/communities/{comm_id}/join", json=reapply_payload, headers=headers)
    assert dup_res.status_code == 400

    # 11. Admin sees pending re-application in Admin Panel
    admin_reqs_res2 = client.get("/api/v1/admin/join-requests", headers=admin_headers)
    our_reapply_req = next((r for r in admin_reqs_res2.json() if r["membership_id"] == membership_id), None)
    assert our_reapply_req is not None
    assert our_reapply_req["status"] == "pending"

    # 12. Admin approves re-application
    approve_res = client.post(f"/api/v1/admin/join-requests/{membership_id}/approve", headers=admin_headers)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"
    assert approve_res.json()["is_active"] is True

    # 13. User can now access dashboard
    dash_ok_res = client.get(f"/api/v1/communities/{comm_id}/dashboard", headers=headers)
    assert dash_ok_res.status_code == 200
    assert dash_ok_res.json()["community"]["id"] == comm_id
