from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_admin
from app.database.session import get_db
from app.models.community import Community
from app.models.roadmap import Roadmap, Module, Task, UserTaskProgress
from app.models.user import User
from app.schemas.roadmap import (
    RoadmapCreate,
    RoadmapUpdate,
    RoadmapResponse,
    ModuleCreate,
    ModuleUpdate,
    ModuleResponse,
    TaskCreate,
    TaskUpdate,
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
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    community = db.query(Community).filter(Community.id == roadmap_data.community_id).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    existing_roadmap = db.query(Roadmap).filter(Roadmap.community_id == roadmap_data.community_id).first()
    if existing_roadmap:
        raise HTTPException(status_code=400, detail="A roadmap already exists for this community.")

    roadmap = Roadmap(
        community_id=roadmap_data.community_id,
        title=roadmap_data.title,
        description=roadmap_data.description,
        total_modules=0,
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
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmap


# =========================
# UPDATE ROADMAP
# =========================

@router.put("/{roadmap_id}", response_model=RoadmapResponse)
def update_roadmap(
    roadmap_id: int,
    roadmap_data: RoadmapUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    if roadmap_data.title is not None:
        roadmap.title = roadmap_data.title
    if roadmap_data.description is not None:
        roadmap.description = roadmap_data.description

    db.commit()
    db.refresh(roadmap)
    return roadmap


# =========================
# DELETE ROADMAP
# =========================

@router.delete("/{roadmap_id}")
def delete_roadmap(
    roadmap_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    db.delete(roadmap)
    db.commit()
    return {"message": "Roadmap deleted successfully."}


# =========================
# GET ROADMAP DETAILS
# =========================

@router.get("/{roadmap_id}/details", response_model=RoadmapDetailResponse)
def get_roadmap_details(
    roadmap_id: int,
    db: Session = Depends(get_db)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmap


# =========================
# CREATE MODULE
# =========================

@router.post("/{roadmap_id}/modules", response_model=ModuleResponse)
def create_module(
    roadmap_id: int,
    module_data: ModuleCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    module = Module(
        roadmap_id=roadmap_id,
        order=module_data.order,
        title=module_data.title,
        description=module_data.description,
    )

    db.add(module)
    roadmap.total_modules += 1
    db.commit()
    db.refresh(module)
    return module


# =========================
# UPDATE MODULE
# =========================

@router.put("/modules/{module_id}", response_model=ModuleResponse)
def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    if module_data.order is not None:
        module.order = module_data.order
    if module_data.title is not None:
        module.title = module_data.title
    if module_data.description is not None:
        module.description = module_data.description

    db.commit()
    db.refresh(module)
    return module


# =========================
# DELETE MODULE
# =========================

@router.delete("/modules/{module_id}")
def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    roadmap = db.query(Roadmap).filter(Roadmap.id == module.roadmap_id).first()
    if roadmap and roadmap.total_modules > 0:
        roadmap.total_modules -= 1

    db.delete(module)
    db.commit()
    return {"message": "Module deleted successfully."}


# =========================
# CREATE TASK
# =========================

@router.post("/modules/{module_id}/tasks", response_model=TaskResponse)
def create_task(
    module_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    task = Task(
        module_id=module_id,
        order=task_data.order,
        title=task_data.title,
    )

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# =========================
# UPDATE TASK
# =========================

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_data.order is not None:
        task.order = task_data.order
    if task_data.title is not None:
        task.title = task_data.title

    db.commit()
    db.refresh(task)
    return task


# =========================
# DELETE TASK
# =========================

@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully."}


# =========================
# UPDATE TASK PROGRESS
# =========================

@router.put("/tasks/{task_id}/progress", response_model=TaskProgressResponse)
def update_task_progress(
    task_id: int,
    progress_data: TaskProgressUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    progress = (
        db.query(UserTaskProgress)
        .filter(
            UserTaskProgress.user_id == user_id,
            UserTaskProgress.task_id == task_id
        )
        .first()
    )

    if not progress:
        progress = UserTaskProgress(user_id=user_id, task_id=task_id)
        db.add(progress)

    progress.is_completed = progress_data.is_completed
    progress.completed_at = datetime.utcnow() if progress_data.is_completed else None

    db.commit()
    db.refresh(progress)
    return progress
