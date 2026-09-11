from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.roadmap import Roadmap, Module, Task,UserTaskProgress
from app.schemas.roadmap import (
    RoadmapCreate,
    RoadmapResponse,
    ModuleCreate,
    ModuleResponse,
    TaskCreate,
    TaskResponse,
    RoadmapDetailResponse,
    TaskProgressUpdate,
    TaskProgressResponse,
)


router = APIRouter(
    prefix="/api/v1/roadmaps",
    tags=["Roadmaps"]
)


# =========================
# CREATE ROADMAP
# =========================

@router.post("/", response_model=RoadmapResponse)
def create_roadmap(
    roadmap_data: RoadmapCreate,
    db: Session = Depends(get_db)
):
    roadmap = Roadmap(
        community_id=roadmap_data.community_id,
        title=roadmap_data.title,
        description=roadmap_data.description
    )

    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)

    return roadmap


# =========================
# GET ALL ROADMAPS
# =========================

@router.get("/", response_model=list[RoadmapResponse])
def get_roadmaps(
    db: Session = Depends(get_db)
):
    roadmaps = db.query(Roadmap).all()

    return roadmaps


# =========================
# GET SINGLE ROADMAP
# =========================

@router.get("/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db)
):
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id)
        .first()
    )

    if not roadmap:
        raise HTTPException(
            status_code=404,
            detail="Roadmap not found"
        )

    return roadmap


# =========================
# GET ROADMAP DETAILS
# =========================

@router.get(
    "/{roadmap_id}/details",
    response_model=RoadmapDetailResponse
)
def get_roadmap_details(
    roadmap_id: int,
    db: Session = Depends(get_db)
):
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id)
        .first()
    )

    if not roadmap:
        raise HTTPException(
            status_code=404,
            detail="Roadmap not found"
        )

    return roadmap


# =========================
# CREATE MODULE
# =========================

@router.post(
    "/{roadmap_id}/modules",
    response_model=ModuleResponse
)
def create_module(
    roadmap_id: int,
    module_data: ModuleCreate,
    db: Session = Depends(get_db)
):
    roadmap = (
        db.query(Roadmap)
        .filter(Roadmap.id == roadmap_id)
        .first()
    )

    if not roadmap:
        raise HTTPException(
            status_code=404,
            detail="Roadmap not found"
        )

    module = Module(
        roadmap_id=roadmap_id,
        order=module_data.order,
        title=module_data.title,
        description=module_data.description
    )

    db.add(module)

    roadmap.total_modules += 1

    db.commit()
    db.refresh(module)

    return module


# =========================
# CREATE TASK
# =========================

@router.post(
    "/modules/{module_id}/tasks",
    response_model=TaskResponse
)
def create_task(
    module_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    module = (
        db.query(Module)
        .filter(Module.id == module_id)
        .first()
    )

    if not module:
        raise HTTPException(
            status_code=404,
            detail="Module not found"
        )

    task = Task(
        module_id=module_id,
        order=task_data.order,
        title=task_data.title
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

# =========================
# UPDATE TASK PROGRESS
# =========================

@router.put(
    "/tasks/{task_id}/progress",
    response_model=TaskProgressResponse
)
def update_task_progress(
    task_id: int,
    progress_data: TaskProgressUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    progress = (
        db.query(UserTaskProgress)
        .filter(
            UserTaskProgress.user_id == user_id,
            UserTaskProgress.task_id == task_id
        )
        .first()
    )

    if not progress:
        progress = UserTaskProgress(
            user_id=user_id,
            task_id=task_id
        )

        db.add(progress)

    progress.is_completed = progress_data.is_completed

    if progress_data.is_completed:
        progress.completed_at = datetime.utcnow()
    else:
        progress.completed_at = None

    db.commit()
    db.refresh(progress)

    return progress