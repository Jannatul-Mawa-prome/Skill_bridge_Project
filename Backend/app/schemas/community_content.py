from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChallengeResponse(BaseModel):
    id: int
    community_id: int
    title: str
    description: str | None = None
    difficulty: str
    xp_reward: int
    is_active: bool
    deadline: datetime | None = None
    user_status: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ResourceResponse(BaseModel):
    id: int
    community_id: int
    title: str
    resource_type: str
    difficulty: str | None = None
    url: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DiscussionResponse(BaseModel):
    id: int
    community_id: int
    author_id: int
    title: str
    content: str | None = None
    reply_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementResponse(BaseModel):
    id: int
    community_id: int
    author_id: int
    title: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventResponse(BaseModel):
    id: int
    community_id: int
    title: str
    description: str | None = None
    event_date: datetime
    status: str
    is_registered: bool = False

    model_config = ConfigDict(from_attributes=True)
