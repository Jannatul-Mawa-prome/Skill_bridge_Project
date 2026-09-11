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

class DashboardResponse(BaseModel):
    user_name: str
    stats: DashboardStatsResponse
    roadmap: Optional[RoadmapSchema] = None

class CommunityListSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    active_members_count: int
    topics: List[str] = [] # Can be generated dynamically later
    challenges_count: int = 0
