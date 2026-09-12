from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminProfileData(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    roll: str = Field(..., min_length=1, max_length=30)
    semester: str = Field(..., max_length=20)
    mobile: str = Field(..., min_length=1, max_length=20)
    department: str | None = Field(default=None, max_length=100)
    university: str | None = Field(default=None, max_length=150)
    bio: str | None = Field(default=None, max_length=500)
    profile_picture: str | None = Field(default=None, max_length=255)


class AdminUserCreate(AdminProfileData):
    edu_email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    is_verified: bool = False
    is_active: bool = True
    is_admin: bool = False


class AdminProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    roll: str | None = Field(default=None, min_length=1, max_length=30)
    semester: str | None = Field(default=None, max_length=20)
    mobile: str | None = Field(default=None, min_length=1, max_length=20)
    department: str | None = Field(default=None, max_length=100)
    university: str | None = Field(default=None, max_length=150)
    bio: str | None = Field(default=None, max_length=500)
    profile_picture: str | None = Field(default=None, max_length=255)


class AdminUserUpdate(BaseModel):
    edu_email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_verified: bool | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    profile: AdminProfileUpdate | None = None


class UserStatusUpdate(BaseModel):
    is_active: bool | None = None
    is_verified: bool | None = None
    is_admin: bool | None = None


class AdminProfileResponse(AdminProfileData):
    model_config = ConfigDict(from_attributes=True)


class AdminUserResponse(BaseModel):
    id: int
    edu_email: EmailStr
    is_verified: bool
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    profile: AdminProfileResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class CommunityCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    is_active: bool = True


class CommunityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class CommunityStatusUpdate(BaseModel):
    is_active: bool


class AdminCommunityResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    active_members_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MembershipCreate(BaseModel):
    user_id: int
    community_id: int
    role: str = Field(default="member", max_length=50)
    is_active: bool = True


class MembershipUpdate(BaseModel):
    role: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None


class MembershipStatusUpdate(BaseModel):
    is_active: bool


class AdminMembershipResponse(BaseModel):
    id: int
    user_id: int
    community_id: int
    role: str
    status: str = "approved"
    streak: int
    is_active: bool
    joined_at: datetime
    reviewed_at: datetime | None = None
    reviewer_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class RoadmapCreate(BaseModel):
    community_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class RoadmapUpdate(BaseModel):
    community_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None


class AdminRoadmapResponse(BaseModel):
    id: int
    community_id: int
    title: str
    description: str | None = None
    total_modules: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModuleCreate(BaseModel):
    order: int = Field(..., ge=0)
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class ModuleUpdate(BaseModel):
    order: int | None = Field(default=None, ge=0)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None


class AdminModuleResponse(BaseModel):
    id: int
    roadmap_id: int
    order: int
    title: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    order: int = Field(..., ge=0)
    title: str = Field(..., min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    order: int | None = Field(default=None, ge=0)
    title: str | None = Field(default=None, min_length=1, max_length=200)


class AdminTaskResponse(BaseModel):
    id: int
    module_id: int
    order: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class ResourceCreate(BaseModel):
    community_id: int
    title: str = Field(..., min_length=1, max_length=200)
    resource_type: str = Field(..., min_length=1, max_length=50)
    difficulty: str | None = Field(default=None, max_length=50)
    url: str = Field(..., min_length=1)
    description: str | None = None


class ResourceUpdate(BaseModel):
    community_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    resource_type: str | None = Field(default=None, min_length=1, max_length=50)
    difficulty: str | None = Field(default=None, max_length=50)
    url: str | None = Field(default=None, min_length=1)
    description: str | None = None


class AdminResourceResponse(BaseModel):
    id: int
    community_id: int
    title: str
    resource_type: str
    difficulty: str | None = None
    url: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementCreate(BaseModel):
    community_id: int
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class AnnouncementUpdate(BaseModel):
    community_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)


class AdminAnnouncementResponse(BaseModel):
    id: int
    community_id: int
    author_id: int
    title: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminOverviewResponse(BaseModel):
    users: int
    active_users: int
    verified_users: int
    administrators: int
    communities: int
    active_communities: int
    memberships: int
    pending_join_requests: int = 0
    roadmaps: int
    modules: int
    tasks: int
    resources: int
    announcements: int
    challenges: int = 0
    events: int = 0


class AdminJoinRequestAnswer(BaseModel):
    question_id: int
    question_key: str
    prompt: str
    answer: Any


class AdminJoinRequestResponse(BaseModel):
    membership_id: int
    user_id: int
    community_id: int
    community_name: str
    student_name: str
    student_email: str
    student_roll: str | None = None
    department: str | None = None
    semester: str | None = None
    mobile: str | None = None
    status: str
    joined_at: datetime
    answers: list[AdminJoinRequestAnswer] = []


class ChallengeCreate(BaseModel):
    community_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    difficulty: str = Field(default="easy", max_length=50)
    xp_reward: int = Field(default=0, ge=0)
    deadline: datetime | None = None
    is_active: bool = True


class ChallengeUpdate(BaseModel):
    community_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    difficulty: str | None = Field(default=None, max_length=50)
    xp_reward: int | None = Field(default=None, ge=0)
    deadline: datetime | None = None
    is_active: bool | None = None


class AdminChallengeResponse(BaseModel):
    id: int
    community_id: int
    title: str
    description: str | None = None
    difficulty: str
    xp_reward: int
    is_active: bool
    deadline: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventCreate(BaseModel):
    community_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    event_date: datetime
    status: str = Field(default="upcoming", max_length=50)


class EventUpdate(BaseModel):
    community_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    event_date: datetime | None = None
    status: str | None = Field(default=None, max_length=50)


class AdminEventResponse(BaseModel):
    id: int
    community_id: int
    title: str
    description: str | None = None
    event_date: datetime
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
