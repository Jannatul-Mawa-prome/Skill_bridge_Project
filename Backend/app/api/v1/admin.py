from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.admin import (
    AdminAnnouncementResponse,
    AdminChallengeResponse,
    AdminCommunityResponse,
    AdminEventResponse,
    AdminJoinRequestResponse,
    AdminMembershipResponse,
    AdminModuleResponse,
    AdminOverviewResponse,
    AdminResourceResponse,
    AdminRoadmapResponse,
    AdminTaskResponse,
    AdminUserCreate,
    AdminUserResponse,
    AdminUserUpdate,
    AnnouncementCreate,
    AnnouncementUpdate,
    ChallengeCreate,
    ChallengeUpdate,
    CommunityCreate,
    CommunityStatusUpdate,
    CommunityUpdate,
    EventCreate,
    EventUpdate,
    MembershipCreate,
    MembershipStatusUpdate,
    MembershipUpdate,
    ModuleCreate,
    ModuleUpdate,
    ResourceCreate,
    ResourceUpdate,
    RoadmapCreate,
    RoadmapUpdate,
    TaskCreate,
    TaskUpdate,
    UserStatusUpdate,
)
from app.services.admin_service import AdminService


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Administration"],
    dependencies=[Depends(get_current_admin)],
)


def service(db: Session) -> AdminService:
    return AdminService(db)


@router.get("/overview", response_model=AdminOverviewResponse)
@router.get("/stats", response_model=AdminOverviewResponse)
def overview(db: Session = Depends(get_db)):
    return service(db).overview()


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    search: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
):
    return service(db).users(search)


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: AdminUserCreate, db: Session = Depends(get_db)):
    return service(db).create_user(data)


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return service(db).user(user_id)


@router.put("/users/{user_id}", response_model=AdminUserResponse)
@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return service(db).update_user(user_id, data, current_admin)


@router.put("/users/{user_id}/status", response_model=AdminUserResponse)
@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return service(db).update_user_status(user_id, data, current_admin)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    service(db).delete_user(user_id, current_admin)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/communities", response_model=list[AdminCommunityResponse])
def list_communities(db: Session = Depends(get_db)):
    return service(db).communities()


@router.post("/communities", response_model=AdminCommunityResponse, status_code=status.HTTP_201_CREATED)
def create_community(data: CommunityCreate, db: Session = Depends(get_db)):
    return service(db).create_community(data)


@router.get("/communities/{community_id}", response_model=AdminCommunityResponse)
def get_community(community_id: int, db: Session = Depends(get_db)):
    return service(db).community(community_id)


@router.put("/communities/{community_id}", response_model=AdminCommunityResponse)
@router.patch("/communities/{community_id}", response_model=AdminCommunityResponse)
def update_community(community_id: int, data: CommunityUpdate, db: Session = Depends(get_db)):
    return service(db).update_community(community_id, data)


@router.put("/communities/{community_id}/status", response_model=AdminCommunityResponse)
@router.patch("/communities/{community_id}/status", response_model=AdminCommunityResponse)
def update_community_status(
    community_id: int,
    data: CommunityStatusUpdate,
    db: Session = Depends(get_db),
):
    return service(db).update_community(community_id, CommunityUpdate(is_active=data.is_active))


@router.delete("/communities/{community_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_community(community_id: int, db: Session = Depends(get_db)):
    service(db).delete_community(community_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/memberships", response_model=list[AdminMembershipResponse])
def list_memberships(
    community_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service(db).memberships(community_id)


@router.get("/communities/{community_id}/memberships", response_model=list[AdminMembershipResponse])
def list_community_memberships(community_id: int, db: Session = Depends(get_db)):
    return service(db).memberships(community_id)


@router.post("/memberships", response_model=AdminMembershipResponse, status_code=status.HTTP_201_CREATED)
def create_membership(data: MembershipCreate, db: Session = Depends(get_db)):
    return service(db).create_membership(data)


@router.get("/memberships/{membership_id}", response_model=AdminMembershipResponse)
def get_membership(membership_id: int, db: Session = Depends(get_db)):
    return service(db).membership(membership_id)


@router.put("/memberships/{membership_id}", response_model=AdminMembershipResponse)
@router.patch("/memberships/{membership_id}", response_model=AdminMembershipResponse)
def update_membership(membership_id: int, data: MembershipUpdate, db: Session = Depends(get_db)):
    return service(db).update_membership(membership_id, data)


@router.put("/memberships/{membership_id}/status", response_model=AdminMembershipResponse)
@router.patch("/memberships/{membership_id}/status", response_model=AdminMembershipResponse)
def update_membership_status(
    membership_id: int,
    data: MembershipStatusUpdate,
    db: Session = Depends(get_db),
):
    return service(db).update_membership(membership_id, MembershipUpdate(is_active=data.is_active))


@router.delete("/memberships/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(membership_id: int, db: Session = Depends(get_db)):
    service(db).delete_membership(membership_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/roadmaps", response_model=list[AdminRoadmapResponse])
def list_roadmaps(db: Session = Depends(get_db)):
    return service(db).roadmaps()


@router.post("/roadmaps", response_model=AdminRoadmapResponse, status_code=status.HTTP_201_CREATED)
def create_roadmap(data: RoadmapCreate, db: Session = Depends(get_db)):
    return service(db).create_roadmap(data)


@router.get("/roadmaps/{roadmap_id}", response_model=AdminRoadmapResponse)
def get_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    return service(db).roadmap(roadmap_id)


@router.put("/roadmaps/{roadmap_id}", response_model=AdminRoadmapResponse)
@router.patch("/roadmaps/{roadmap_id}", response_model=AdminRoadmapResponse)
def update_roadmap(roadmap_id: int, data: RoadmapUpdate, db: Session = Depends(get_db)):
    return service(db).update_roadmap(roadmap_id, data)


@router.delete("/roadmaps/{roadmap_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    service(db).delete_roadmap(roadmap_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/roadmaps/{roadmap_id}/modules", response_model=list[AdminModuleResponse])
def list_modules(roadmap_id: int, db: Session = Depends(get_db)):
    return service(db).modules(roadmap_id)


@router.post("/roadmaps/{roadmap_id}/modules", response_model=AdminModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(roadmap_id: int, data: ModuleCreate, db: Session = Depends(get_db)):
    return service(db).create_module(roadmap_id, data)


@router.get("/modules/{module_id}", response_model=AdminModuleResponse)
def get_module(module_id: int, db: Session = Depends(get_db)):
    return service(db).module(module_id)


@router.put("/modules/{module_id}", response_model=AdminModuleResponse)
@router.patch("/modules/{module_id}", response_model=AdminModuleResponse)
def update_module(module_id: int, data: ModuleUpdate, db: Session = Depends(get_db)):
    return service(db).update_module(module_id, data)


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(module_id: int, db: Session = Depends(get_db)):
    service(db).delete_module(module_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/modules/{module_id}/tasks", response_model=list[AdminTaskResponse])
def list_tasks(module_id: int, db: Session = Depends(get_db)):
    return service(db).tasks(module_id)


@router.post("/modules/{module_id}/tasks", response_model=AdminTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(module_id: int, data: TaskCreate, db: Session = Depends(get_db)):
    return service(db).create_task(module_id, data)


@router.get("/tasks/{task_id}", response_model=AdminTaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return service(db).task(task_id)


@router.put("/tasks/{task_id}", response_model=AdminTaskResponse)
@router.patch("/tasks/{task_id}", response_model=AdminTaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    return service(db).update_task(task_id, data)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    service(db).delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/resources", response_model=list[AdminResourceResponse])
def list_resources(
    community_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service(db).resources(community_id)


@router.post("/resources", response_model=AdminResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(data: ResourceCreate, db: Session = Depends(get_db)):
    return service(db).create_resource(data)


@router.get("/resources/{resource_id}", response_model=AdminResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    return service(db).resource(resource_id)


@router.put("/resources/{resource_id}", response_model=AdminResourceResponse)
@router.patch("/resources/{resource_id}", response_model=AdminResourceResponse)
def update_resource(resource_id: int, data: ResourceUpdate, db: Session = Depends(get_db)):
    return service(db).update_resource(resource_id, data)


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    service(db).delete_resource(resource_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/announcements", response_model=list[AdminAnnouncementResponse])
def list_announcements(
    community_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service(db).announcements(community_id)


@router.post("/announcements", response_model=AdminAnnouncementResponse, status_code=status.HTTP_201_CREATED)
def create_announcement(
    data: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return service(db).create_announcement(data, current_admin.id)


@router.get("/announcements/{announcement_id}", response_model=AdminAnnouncementResponse)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    return service(db).announcement(announcement_id)


@router.put("/announcements/{announcement_id}", response_model=AdminAnnouncementResponse)
@router.patch("/announcements/{announcement_id}", response_model=AdminAnnouncementResponse)
def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdate,
    db: Session = Depends(get_db),
):
    return service(db).update_announcement(announcement_id, data)


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    service(db).delete_announcement(announcement_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =========================
# JOIN REQUESTS
# =========================

@router.get("/join-requests", response_model=list[AdminJoinRequestResponse])
def list_join_requests(
    community_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service(db).join_requests(community_id)


@router.post("/join-requests/{membership_id}/approve", response_model=AdminMembershipResponse)
def approve_join_request(
    membership_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return service(db).approve_join_request(membership_id, current_admin)


@router.post("/join-requests/{membership_id}/reject", response_model=AdminMembershipResponse)
def reject_join_request(
    membership_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return service(db).reject_join_request(membership_id, current_admin)


# =========================
# CHALLENGES
# =========================

@router.get("/challenges", response_model=list[AdminChallengeResponse])
def list_challenges(
    community_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service(db).challenges(community_id)


@router.post("/challenges", response_model=AdminChallengeResponse, status_code=status.HTTP_201_CREATED)
def create_challenge(
    data: ChallengeCreate,
    db: Session = Depends(get_db),
):
    return service(db).create_challenge(data)


@router.get("/challenges/{challenge_id}", response_model=AdminChallengeResponse)
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    return service(db).challenge(challenge_id)


@router.put("/challenges/{challenge_id}", response_model=AdminChallengeResponse)
@router.patch("/challenges/{challenge_id}", response_model=AdminChallengeResponse)
def update_challenge(
    challenge_id: int,
    data: ChallengeUpdate,
    db: Session = Depends(get_db),
):
    return service(db).update_challenge(challenge_id, data)


@router.delete("/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_challenge(challenge_id: int, db: Session = Depends(get_db)):
    service(db).delete_challenge(challenge_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =========================
# EVENTS
# =========================

@router.get("/events", response_model=list[AdminEventResponse])
def list_events(
    community_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return service(db).events(community_id)


@router.post("/events", response_model=AdminEventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    data: EventCreate,
    db: Session = Depends(get_db),
):
    return service(db).create_event(data)


@router.get("/events/{event_id}", response_model=AdminEventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    return service(db).event(event_id)


@router.put("/events/{event_id}", response_model=AdminEventResponse)
@router.patch("/events/{event_id}", response_model=AdminEventResponse)
def update_event(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
):
    return service(db).update_event(event_id, data)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    service(db).delete_event(event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
