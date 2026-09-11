from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.announcement import Announcement
from app.models.community import Community, CommunityMembership
from app.models.resource import Resource
from app.models.roadmap import Module, Roadmap, Task
from app.models.profile import Profile
from app.models.user import User


class AdminRepository:
    """Persistence operations used only by the administrator API."""

    def __init__(self, db: Session):
        self.db = db

    def list_users(self, search: str | None = None) -> list[User]:
        query = select(User).options(joinedload(User.profile)).order_by(User.id)
        if search:
            term = f"%{search}%"
            query = query.outerjoin(Profile).where(
                User.edu_email.ilike(term)
                | Profile.full_name.ilike(term)
                | Profile.roll.ilike(term)
            )
        return list(self.db.execute(query).unique().scalars().all())

    def get_user(self, user_id: int) -> User | None:
        return self.db.execute(
            select(User).options(joinedload(User.profile)).where(User.id == user_id)
        ).unique().scalar_one_or_none()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.execute(select(User).where(User.edu_email == email)).scalar_one_or_none()

    def list_communities(self) -> list[Community]:
        return list(self.db.execute(select(Community).order_by(Community.id)).scalars().all())

    def get_community(self, community_id: int) -> Community | None:
        return self.db.get(Community, community_id)

    def get_community_by_name(self, name: str) -> Community | None:
        return self.db.execute(select(Community).where(Community.name == name)).scalar_one_or_none()

    def list_memberships(self, community_id: int | None = None) -> list[CommunityMembership]:
        query = select(CommunityMembership).order_by(CommunityMembership.id)
        if community_id is not None:
            query = query.where(CommunityMembership.community_id == community_id)
        return list(self.db.execute(query).scalars().all())

    def get_membership(self, membership_id: int) -> CommunityMembership | None:
        return self.db.get(CommunityMembership, membership_id)

    def membership_exists(self, user_id: int, community_id: int) -> bool:
        return self.db.execute(
            select(CommunityMembership.id).where(
                CommunityMembership.user_id == user_id,
                CommunityMembership.community_id == community_id,
            )
        ).first() is not None

    def list_roadmaps(self) -> list[Roadmap]:
        return list(self.db.execute(select(Roadmap).order_by(Roadmap.id)).scalars().all())

    def get_roadmap(self, roadmap_id: int) -> Roadmap | None:
        return self.db.get(Roadmap, roadmap_id)

    def list_modules(self, roadmap_id: int | None = None) -> list[Module]:
        query = select(Module).order_by(Module.order, Module.id)
        if roadmap_id is not None:
            query = query.where(Module.roadmap_id == roadmap_id)
        return list(self.db.execute(query).scalars().all())

    def get_module(self, module_id: int) -> Module | None:
        return self.db.get(Module, module_id)

    def list_tasks(self, module_id: int | None = None) -> list[Task]:
        query = select(Task).order_by(Task.order, Task.id)
        if module_id is not None:
            query = query.where(Task.module_id == module_id)
        return list(self.db.execute(query).scalars().all())

    def get_task(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def list_resources(self, community_id: int | None = None) -> list[Resource]:
        query = select(Resource).order_by(Resource.id)
        if community_id is not None:
            query = query.where(Resource.community_id == community_id)
        return list(self.db.execute(query).scalars().all())

    def get_resource(self, resource_id: int) -> Resource | None:
        return self.db.get(Resource, resource_id)

    def list_announcements(self, community_id: int | None = None) -> list[Announcement]:
        query = select(Announcement).order_by(Announcement.created_at.desc(), Announcement.id.desc())
        if community_id is not None:
            query = query.where(Announcement.community_id == community_id)
        return list(self.db.execute(query).scalars().all())

    def get_announcement(self, announcement_id: int) -> Announcement | None:
        return self.db.get(Announcement, announcement_id)

    def count(self, model, *conditions) -> int:
        query = select(func.count()).select_from(model)
        if conditions:
            query = query.where(*conditions)
        return int(self.db.execute(query).scalar_one())

    def save(self, entity):
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity) -> None:
        self.db.delete(entity)
        self.db.commit()
