from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import get_db
from app.schemas.community import JoinCommunityRequest, DashboardResponse, CommunityListSchema
from app.services.community_service import CommunityService
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
