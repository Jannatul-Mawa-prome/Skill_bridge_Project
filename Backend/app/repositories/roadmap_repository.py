from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.models.roadmap import Roadmap, Module, Task, UserTaskProgress

class RoadmapRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_roadmap_by_community(self, community_id: int) -> Roadmap | None:
        # Assuming one roadmap per community for now, or returning the main one.
        # joinedload helps in avoiding N+1 queries when fetching modules and tasks
        return self.db.execute(
            select(Roadmap)
            .where(Roadmap.community_id == community_id)
            .options(joinedload(Roadmap.modules).joinedload(Module.tasks))
        ).unique().scalars().first()
    
    def create_roadmap(self, community_id: int, title: str, description: str = None) -> Roadmap:
        roadmap = Roadmap(community_id=community_id, title=title, description=description)
        self.db.add(roadmap)
        self.db.commit()
        self.db.refresh(roadmap)
        return roadmap
    
    def get_user_progress(self, user_id: int, roadmap_id: int) -> list[UserTaskProgress]:
        # Get progress for tasks that belong to the given roadmap
        return self.db.execute(
            select(UserTaskProgress)
            .join(Task, UserTaskProgress.task_id == Task.id)
            .join(Module, Task.module_id == Module.id)
            .where(UserTaskProgress.user_id == user_id)
            .where(Module.roadmap_id == roadmap_id)
        ).scalars().all()

    
    def mark_task_completed(self, user_id: int, task_id: int) -> UserTaskProgress:
        progress = self.db.execute(
            select(UserTaskProgress)
            .where(UserTaskProgress.user_id == user_id)
            .where(UserTaskProgress.task_id == task_id)
        ).scalar_one_or_none()
        
        from datetime import datetime
        if progress:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
        else:
            progress = UserTaskProgress(
                user_id=user_id, 
                task_id=task_id, 
                is_completed=True, 
                completed_at=datetime.utcnow()
            )
            self.db.add(progress)
            
        self.db.commit()
        self.db.refresh(progress)
        return progress
