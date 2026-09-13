from typing import List, Optional
from pydantic import BaseModel, Field

class JoinCommunityRequest(BaseModel):
    skill_level: str = Field(..., description="E.g., beginner, intermediate, advanced")
    languages_known: List[str] = Field(..., description="List of programming languages")
    problem_solving_comfort: str = Field(..., description="E.g., new, basic, comfortable, advanced")
    main_goal: str = Field(..., description="E.g., learn, problem-solving, competitive, projects")
    weekly_time_commitment: str = Field(..., description="E.g., 0-2 hours, 2-5 hours, etc.")

class DashboardStatsResponse(BaseModel):
    roadmap_progress_percentage: int
    current_streak_days: int
    completed_tasks_count: int
    community_rank: int

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

class ResourceSchema(BaseModel):
    id: int
    community_id: int
    module_id: Optional[int] = None
    title: str
    resource_type: str
    difficulty: Optional[str] = None
    url: str
    description: Optional[str] = None
    is_active: bool = True


class ResourceCreateRequest(BaseModel):
    community_id: int
    module_id: Optional[int] = None
    title: str
    resource_type: str
    difficulty: Optional[str] = None
    url: str
    description: Optional[str] = None


class ResourceUpdateRequest(BaseModel):
    community_id: Optional[int] = None
    module_id: Optional[int] = None
    title: Optional[str] = None
    resource_type: Optional[str] = None
    difficulty: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AnnouncementSchema(BaseModel):
    id: int
    title: str
    content: str
    created_at: Optional[str] = None
    author_name: Optional[str] = None

class DashboardResponse(BaseModel):
    user_name: str
    community_id: int
    community_name: str
    stats: DashboardStatsResponse
    roadmap: Optional[RoadmapSchema] = None
    resources: List[ResourceSchema] = []
    announcements: List[AnnouncementSchema] = []

class CommunityListSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    active_members_count: int
    topics: List[str] = [] # Can be generated dynamically later
    challenges_count: int = 0


class AdminMembershipSummarySchema(BaseModel):
    id: int
    user_id: int
    community_id: int
    community_name: str
    student_name: str
    student_email: str
    student_roll: Optional[str] = None
    status: str
    request_date: str


class AdminMembershipDetailSchema(BaseModel):
    id: int
    user_id: int
    community_id: int
    community_name: str
    student_name: str
    student_email: str
    student_roll: Optional[str] = None
    status: str
    request_date: str
    answers: dict


class AdminMembershipActionSchema(BaseModel):
    membership_id: int
    community_id: int
    status: str
    message: str
