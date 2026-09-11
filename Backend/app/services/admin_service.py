from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.announcement import Announcement
from app.models.community import Community, CommunityMembership
from app.models.profile import Profile
from app.models.resource import Resource
from app.models.roadmap import Module, Roadmap, Task
from app.models.user import User
from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import (
    AdminUserCreate,
    AdminUserUpdate,
    AnnouncementCreate,
    AnnouncementUpdate,
    CommunityCreate,
    CommunityUpdate,
    MembershipCreate,
    MembershipUpdate,
    ModuleCreate,
    ModuleUpdate,
    ResourceCreate,
    ResourceUpdate,
    RoadmapCreate,
    RoadmapUpdate,
    TaskCreate,
    TaskUpdate,
    UserStatusUpdate,
)


class AdminService:
    def __init__(self, db: Session):
        self.repo = AdminRepository(db)

    def _save(self, entity):
        try:
            return self.repo.save(entity)
        except IntegrityError as exc:
            self.repo.db.rollback()
            raise HTTPException(status_code=409, detail="The requested change conflicts with existing data") from exc

    def _delete(self, entity):
        try:
            self.repo.delete(entity)
        except IntegrityError as exc:
            self.repo.db.rollback()
            raise HTTPException(status_code=409, detail="This record cannot be deleted while it is in use") from exc

    def overview(self) -> dict[str, int]:
        return {
            "users": self.repo.count(User),
            "active_users": self.repo.count(User, User.is_active.is_(True)),
            "verified_users": self.repo.count(User, User.is_verified.is_(True)),
            "administrators": self.repo.count(User, User.is_admin.is_(True)),
            "communities": self.repo.count(Community),
            "active_communities": self.repo.count(Community, Community.is_active.is_(True)),
            "memberships": self.repo.count(CommunityMembership),
            "roadmaps": self.repo.count(Roadmap),
            "modules": self.repo.count(Module),
            "tasks": self.repo.count(Task),
            "resources": self.repo.count(Resource),
            "announcements": self.repo.count(Announcement),
        }

    def users(self, search: str | None = None):
        return self.repo.list_users(search)

    def user(self, user_id: int) -> User:
        entity = self.repo.get_user(user_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="User not found")
        return entity

    def create_user(self, data: AdminUserCreate) -> User:
        if self.repo.get_user_by_email(str(data.edu_email)):
            raise HTTPException(status_code=409, detail="Email already registered")
        entity = User(
            edu_email=str(data.edu_email),
            password_hash=hash_password(data.password),
            is_verified=data.is_verified,
            is_active=data.is_active,
            is_admin=data.is_admin,
            profile=Profile(**data.model_dump(exclude={"edu_email", "password", "is_verified", "is_active", "is_admin"})),
        )
        return self._save(entity)

    def update_user(self, user_id: int, data: AdminUserUpdate, current_admin: User) -> User:
        entity = self.user(user_id)
        values = data.model_dump(exclude_unset=True, exclude={"profile", "password"})
        if entity.id == current_admin.id:
            if values.get("is_admin") is False or values.get("is_active") is False:
                raise HTTPException(status_code=400, detail="You cannot deactivate or demote your own account")
        if "edu_email" in values:
            other = self.repo.get_user_by_email(str(values["edu_email"]))
            if other is not None and other.id != entity.id:
                raise HTTPException(status_code=409, detail="Email already registered")
            values["edu_email"] = str(values["edu_email"])
        for key, value in values.items():
            setattr(entity, key, value)
        if data.password is not None:
            entity.password_hash = hash_password(data.password)
        if data.profile is not None:
            if entity.profile is None:
                entity.profile = Profile(**data.profile.model_dump())
            else:
                for key, value in data.profile.model_dump(exclude_unset=True).items():
                    setattr(entity.profile, key, value)
        return self._save(entity)

    def update_user_status(self, user_id: int, data: UserStatusUpdate, current_admin: User) -> User:
        return self.update_user(user_id, AdminUserUpdate(**data.model_dump(exclude_unset=True)), current_admin)

    def delete_user(self, user_id: int, current_admin: User) -> None:
        entity = self.user(user_id)
        if entity.id == current_admin.id:
            raise HTTPException(status_code=400, detail="You cannot delete your own account")
        self._delete(entity)

    def communities(self):
        return self.repo.list_communities()

    def community(self, community_id: int) -> Community:
        entity = self.repo.get_community(community_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Community not found")
        return entity

    def create_community(self, data: CommunityCreate) -> Community:
        if self.repo.get_community_by_name(data.name):
            raise HTTPException(status_code=409, detail="Community name already exists")
        return self._save(Community(**data.model_dump()))

    def update_community(self, community_id: int, data: CommunityUpdate) -> Community:
        entity = self.community(community_id)
        values = data.model_dump(exclude_unset=True)
        if "name" in values:
            other = self.repo.get_community_by_name(values["name"])
            if other is not None and other.id != entity.id:
                raise HTTPException(status_code=409, detail="Community name already exists")
        for key, value in values.items():
            setattr(entity, key, value)
        return self._save(entity)

    def delete_community(self, community_id: int) -> None:
        self._delete(self.community(community_id))

    def memberships(self, community_id: int | None = None):
        if community_id is not None:
            self.community(community_id)
        return self.repo.list_memberships(community_id)

    def membership(self, membership_id: int) -> CommunityMembership:
        entity = self.repo.get_membership(membership_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Membership not found")
        return entity

    def create_membership(self, data: MembershipCreate) -> CommunityMembership:
        self.user(data.user_id)
        self.community(data.community_id)
        if self.repo.membership_exists(data.user_id, data.community_id):
            raise HTTPException(status_code=409, detail="Membership already exists")
        entity = self._save(CommunityMembership(**data.model_dump()))
        community = self.community(data.community_id)
        community.active_members_count = self.repo.count(
            CommunityMembership,
            CommunityMembership.community_id == data.community_id,
            CommunityMembership.is_active.is_(True),
        )
        self._save(community)
        return entity

    def update_membership(self, membership_id: int, data: MembershipUpdate) -> CommunityMembership:
        entity = self.membership(membership_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
        entity = self._save(entity)
        community = self.community(entity.community_id)
        community.active_members_count = self.repo.count(
            CommunityMembership,
            CommunityMembership.community_id == entity.community_id,
            CommunityMembership.is_active.is_(True),
        )
        self._save(community)
        return entity

    def delete_membership(self, membership_id: int) -> None:
        entity = self.membership(membership_id)
        community_id = entity.community_id
        self._delete(entity)
        community = self.community(community_id)
        community.active_members_count = self.repo.count(
            CommunityMembership,
            CommunityMembership.community_id == community_id,
            CommunityMembership.is_active.is_(True),
        )
        self._save(community)

    def roadmaps(self):
        return self.repo.list_roadmaps()

    def roadmap(self, roadmap_id: int) -> Roadmap:
        entity = self.repo.get_roadmap(roadmap_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        return entity

    def create_roadmap(self, data: RoadmapCreate) -> Roadmap:
        self.community(data.community_id)
        return self._save(Roadmap(**data.model_dump()))

    def update_roadmap(self, roadmap_id: int, data: RoadmapUpdate) -> Roadmap:
        entity = self.roadmap(roadmap_id)
        values = data.model_dump(exclude_unset=True)
        if "community_id" in values:
            self.community(values["community_id"])
        for key, value in values.items():
            setattr(entity, key, value)
        return self._save(entity)

    def delete_roadmap(self, roadmap_id: int) -> None:
        self._delete(self.roadmap(roadmap_id))

    def modules(self, roadmap_id: int):
        self.roadmap(roadmap_id)
        return self.repo.list_modules(roadmap_id)

    def module(self, module_id: int) -> Module:
        entity = self.repo.get_module(module_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Module not found")
        return entity

    def create_module(self, roadmap_id: int, data: ModuleCreate) -> Module:
        roadmap = self.roadmap(roadmap_id)
        entity = self._save(Module(roadmap_id=roadmap_id, **data.model_dump()))
        roadmap.total_modules = self.repo.count(Module, Module.roadmap_id == roadmap_id)
        self._save(roadmap)
        return entity

    def update_module(self, module_id: int, data: ModuleUpdate) -> Module:
        entity = self.module(module_id)
        old_roadmap_id = entity.roadmap_id
        values = data.model_dump(exclude_unset=True)
        for key, value in values.items():
            setattr(entity, key, value)
        entity = self._save(entity)
        if "roadmap_id" in values:
            # roadmap_id is intentionally not accepted by ModuleUpdate; keep this
            # branch defensive if the schema is extended later.
            for roadmap_id in {old_roadmap_id, entity.roadmap_id}:
                roadmap = self.roadmap(roadmap_id)
                roadmap.total_modules = self.repo.count(Module, Module.roadmap_id == roadmap_id)
                self._save(roadmap)
        return entity

    def delete_module(self, module_id: int) -> None:
        entity = self.module(module_id)
        roadmap_id = entity.roadmap_id
        self._delete(entity)
        roadmap = self.roadmap(roadmap_id)
        roadmap.total_modules = self.repo.count(Module, Module.roadmap_id == roadmap_id)
        self._save(roadmap)

    def tasks(self, module_id: int):
        self.module(module_id)
        return self.repo.list_tasks(module_id)

    def task(self, task_id: int) -> Task:
        entity = self.repo.get_task(task_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return entity

    def create_task(self, module_id: int, data: TaskCreate) -> Task:
        self.module(module_id)
        return self._save(Task(module_id=module_id, **data.model_dump()))

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        entity = self.task(task_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
        return self._save(entity)

    def delete_task(self, task_id: int) -> None:
        self._delete(self.task(task_id))

    def resources(self, community_id: int | None = None):
        if community_id is not None:
            self.community(community_id)
        return self.repo.list_resources(community_id)

    def resource(self, resource_id: int) -> Resource:
        entity = self.repo.get_resource(resource_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        return entity

    def create_resource(self, data: ResourceCreate) -> Resource:
        self.community(data.community_id)
        return self._save(Resource(**data.model_dump()))

    def update_resource(self, resource_id: int, data: ResourceUpdate) -> Resource:
        entity = self.resource(resource_id)
        values = data.model_dump(exclude_unset=True)
        if "community_id" in values:
            self.community(values["community_id"])
        for key, value in values.items():
            setattr(entity, key, value)
        return self._save(entity)

    def delete_resource(self, resource_id: int) -> None:
        self._delete(self.resource(resource_id))

    def announcements(self, community_id: int | None = None):
        if community_id is not None:
            self.community(community_id)
        return self.repo.list_announcements(community_id)

    def announcement(self, announcement_id: int) -> Announcement:
        entity = self.repo.get_announcement(announcement_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Announcement not found")
        return entity

    def create_announcement(self, data: AnnouncementCreate, author_id: int) -> Announcement:
        self.community(data.community_id)
        return self._save(Announcement(author_id=author_id, **data.model_dump()))

    def update_announcement(self, announcement_id: int, data: AnnouncementUpdate) -> Announcement:
        entity = self.announcement(announcement_id)
        values = data.model_dump(exclude_unset=True)
        if "community_id" in values:
            self.community(values["community_id"])
        for key, value in values.items():
            setattr(entity, key, value)
        return self._save(entity)

    def delete_announcement(self, announcement_id: int) -> None:
        self._delete(self.announcement(announcement_id))
