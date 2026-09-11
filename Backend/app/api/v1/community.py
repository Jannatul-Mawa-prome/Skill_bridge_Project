from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import get_db
from app.schemas.community import JoinCommunityRequest, DashboardResponse, CommunityListSchema
from app.schemas.community_question import (
    CommunityQuestionCreate,
    CommunityQuestionResponse,
    CommunityQuestionUpdate,
)
from app.services.community_service import CommunityService
from app.services.community_question_service import CommunityQuestionService
from app.services.community_content_service import CommunityContentService
from app.schemas.community_content import (
    AnnouncementResponse,
    ChallengeResponse,
    DiscussionResponse,
    EventResponse,
    ResourceResponse,
)
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/api/v1/communities",
    tags=["Communities"]
)

@router.get("", response_model=list[CommunityListSchema])
def get_communities(db: Session = Depends(get_db)):
    service = CommunityService(db)
    return service.get_all_communities()

@router.get(
    "/{community_id}/questions",
    response_model=list[CommunityQuestionResponse],
)
def get_community_questions(
    community_id: int,
    db: Session = Depends(get_db),
):
    service = CommunityQuestionService(db)
    return service.get_active_questions(community_id)

@router.post(
    "/{community_id}/questions",
    response_model=CommunityQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_community_question(
    community_id: int,
    question_data: CommunityQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Question management is authenticated for now; role-based administration
    # can be added when community ownership/roles are introduced.
    service = CommunityQuestionService(db)
    return service.create_question(community_id, question_data)

@router.patch(
    "/{community_id}/questions/{question_id}",
    response_model=CommunityQuestionResponse,
)
def update_community_question(
    community_id: int,
    question_id: int,
    question_data: CommunityQuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommunityQuestionService(db)
    return service.update_question(
        community_id,
        question_id,
        question_data,
    )

def content_service(db: Session) -> CommunityContentService:
    return CommunityContentService(db)

@router.get("/{community_id}/challenges", response_model=list[ChallengeResponse])
def get_challenges(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return content_service(db).get_challenges(current_user, community_id)

@router.post("/{community_id}/challenges/{challenge_id}/complete")
def complete_challenge(
    community_id: int,
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return content_service(db).complete_challenge(
        current_user,
        community_id,
        challenge_id,
    )

@router.get("/{community_id}/resources", response_model=list[ResourceResponse])
def get_resources(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return content_service(db).get_resources(current_user, community_id)

@router.get("/{community_id}/discussions", response_model=list[DiscussionResponse])
def get_discussions(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return content_service(db).get_discussions(current_user, community_id)

@router.get("/{community_id}/announcements", response_model=list[AnnouncementResponse])
def get_announcements(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return content_service(db).get_announcements(current_user, community_id)

@router.get("/{community_id}/events", response_model=list[EventResponse])
def get_events(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return content_service(db).get_events(current_user, community_id)

@router.post("/{community_id}/events/{event_id}/register")
def register_for_event(
    community_id: int,
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return content_service(db).register_for_event(
        current_user,
        community_id,
        event_id,
    )

@router.post("/{community_id}/join")
def join_community(
    community_id: int,
    request: JoinCommunityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CommunityService(db)
    return service.join_community(current_user.id, community_id, request)




@router.get("/my-communities", response_model=list[CommunityListSchema])
def get_my_communities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CommunityService(db)

    return service.get_my_communities(current_user.id)




@router.get("/{community_id}/dashboard", response_model=DashboardResponse)
def get_community_dashboard(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CommunityService(db)
    return service.get_dashboard_data(current_user, community_id)

@router.get("/{community_id}/membership")
def check_membership(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CommunityService(db)

    return service.check_membership(
        current_user.id,
        community_id
    )
