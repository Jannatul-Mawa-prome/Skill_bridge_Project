from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field
from app.schemas.community_content import (
    AnnouncementResponse,
    ChallengeResponse,
    DiscussionResponse,
    EventResponse,
)


class JoinCommunityAnswer(BaseModel):
    question_key: str = Field(..., min_length=1, max_length=100)
    value: Any


class JoinCommunityRequest(BaseModel):
    answers: List["JoinCommunityAnswer"] = Field(
        default_factory=list,
        description="Answers keyed by the community's active questions",
    )
    # Deprecated fixed fields are retained so existing clients continue to work.
    skill_level: Optional[str] = None
    languages_known: Optional[List[str]] = None
    problem_solving_comfort: Optional[str] = None
    main_goal: Optional[str] = None
    weekly_time_commitment: Optional[str] = None

class DashboardStatsResponse(BaseModel):
    roadmap_progress_percentage: int
    current_streak_days: int
    completed_tasks_count: int

class DashboardCommunityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    active_members_count: int

class DashboardMembershipResponse(BaseModel):
    id: int
    role: str
    status: str
    streak: int
    joined_at: datetime

class MembershipStatusResponse(BaseModel):
    is_member: bool
    status: str
    membership_id: Optional[int] = None

class DashboardAnswerResponse(BaseModel):
    question_key: str
    value: Any

class DashboardResourceResponse(BaseModel):
    id: int
    title: str
    resource_type: str
    difficulty: Optional[str] = None
    url: str
    description: Optional[str] = None

class DashboardMemberResponse(BaseModel):
    user_id: int
    name: str
    role: str

class TaskSchema(BaseModel):
    id: int
    title: str
    is_completed: bool

class ModuleSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str = Field(..., description="completed, in_progress, locked")
    progress_percentage: int
    tasks: List[TaskSchema]

class RoadmapSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    total_modules: int
    total_tasks: int
    completed_tasks: int
    modules: List[ModuleSchema]

class DashboardResponse(BaseModel):
    user_name: str
    community: DashboardCommunityResponse
    membership: DashboardMembershipResponse
    answers: List[DashboardAnswerResponse]
    stats: DashboardStatsResponse
    roadmap: Optional[RoadmapSchema] = None
    resources: List[DashboardResourceResponse] = []
    challenges: List[ChallengeResponse] = []
    discussions: List[DiscussionResponse] = []
    announcements: List[AnnouncementResponse] = []
    events: List[EventResponse] = []
    members: List[DashboardMemberResponse] = []

class CommunityListSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    active_members_count: int
    topics: List[str] = [] # Can be generated dynamically later
    challenges_count: int = 0
