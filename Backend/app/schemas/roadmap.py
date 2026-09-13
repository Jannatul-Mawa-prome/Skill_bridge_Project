from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class RoadmapCreate(BaseModel):
    community_id: int
    title: str
    description: Optional[str] = None


class RoadmapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class RoadmapResponse(BaseModel):
    id: int
    community_id: int
    title: str
    description: Optional[str] = None
    total_modules: int

    model_config = ConfigDict(from_attributes=True)


class ModuleCreate(BaseModel):
    order: int
    title: str
    description: Optional[str] = None


class ModuleUpdate(BaseModel):
    order: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class ModuleResponse(BaseModel):
    id: int
    roadmap_id: int
    order: int
    title: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    order: int
    title: str


class TaskUpdate(BaseModel):
    order: Optional[int] = None
    title: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    module_id: int
    order: int
    title: str

    model_config = ConfigDict(from_attributes=True)

class TaskNestedResponse(BaseModel):
    id: int
    order: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class ModuleNestedResponse(BaseModel):
    id: int
    order: int
    title: str
    description: Optional[str] = None
    tasks: list[TaskNestedResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RoadmapDetailResponse(BaseModel):
    id: int
    community_id: int
    title: str
    description: Optional[str] = None
    total_modules: int
    modules: list[ModuleNestedResponse] = []

    model_config = ConfigDict(from_attributes=True)

class TaskProgressUpdate(BaseModel):
    is_completed: bool


class TaskProgressResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    is_completed: bool
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)