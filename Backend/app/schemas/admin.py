from datetime import datetime

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
    streak: int
    is_active: bool
    joined_at: datetime

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
    roadmaps: int
    modules: int
    tasks: int
    resources: int
    announcements: int
