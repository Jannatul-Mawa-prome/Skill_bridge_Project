from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.announcement import Announcement
from app.models.challenge import Challenge
from app.models.community import Community, CommunityMembership
from app.models.event import Event
from app.models.profile import Profile
from app.models.resource import Resource
from app.models.roadmap import Module, Roadmap, Task
from app.models.user import User
from app.repositories.admin_repository import AdminRepository
from app.schemas.admin import (
    AdminJoinRequestAnswer,
    AdminJoinRequestResponse,
    AdminMembershipResponse,
    AdminUserCreate,
    AdminUserUpdate,
    AnnouncementCreate,
    AnnouncementUpdate,
    ChallengeCreate,
    ChallengeUpdate,
    CommunityCreate,
    CommunityUpdate,
    EventCreate,
    EventUpdate,
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
            "pending_join_requests": self.repo.count(CommunityMembership, CommunityMembership.status == "pending"),
            "roadmaps": self.repo.count(Roadmap),
            "modules": self.repo.count(Module),
            "tasks": self.repo.count(Task),
            "resources": self.repo.count(Resource),
            "announcements": self.repo.count(Announcement),
            "challenges": self.repo.count(Challenge),
            "events": self.repo.count(Event),
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

    def join_requests(self, community_id: int | None = None) -> list[AdminJoinRequestResponse]:
        requests = self.repo.list_join_requests(community_id=community_id, status="pending")
        result = []
        for req in requests:
            answers = []
            for ans in req.answers:
                answers.append(
                    AdminJoinRequestAnswer(
                        question_id=ans.question_id,
                        question_key=ans.question.question_key if ans.question else "",
                        prompt=ans.question.prompt if ans.question else "",
                        answer=ans.answer,
                    )
                )
            result.append(
                AdminJoinRequestResponse(
                    membership_id=req.id,
                    user_id=req.user_id,
                    community_id=req.community_id,
                    community_name=req.community.name if req.community else "",
                    student_name=req.user.profile.full_name if req.user and req.user.profile else (req.user.edu_email if req.user else ""),
                    student_email=req.user.edu_email if req.user else "",
                    student_roll=req.user.profile.roll if req.user and req.user.profile else None,
                    department=req.user.profile.department if req.user and req.user.profile else None,
                    semester=req.user.profile.semester if req.user and req.user.profile else None,
                    mobile=req.user.profile.mobile if req.user and req.user.profile else None,
                    status=req.status,
                    joined_at=req.joined_at,
                    answers=answers,
                )
            )
        return result

    def approve_join_request(self, membership_id: int, current_admin: User) -> AdminMembershipResponse:
        membership = self.repo.get_join_request(membership_id)
        if not membership:
            raise HTTPException(status_code=404, detail="Join request not found")

        if membership.status == "approved":
            return AdminMembershipResponse.model_validate(membership)

        membership.status = "approved"
        membership.is_active = True
        membership.reviewed_at = datetime.utcnow()
        membership.reviewer_id = current_admin.id

        community = self.repo.get_community(membership.community_id)
        if community:
            community.active_members_count += 1
            self.repo.save(community)

        saved = self._save(membership)
        return AdminMembershipResponse.model_validate(saved)

    def reject_join_request(self, membership_id: int, current_admin: User) -> AdminMembershipResponse:
        membership = self.repo.get_join_request(membership_id)
        if not membership:
            raise HTTPException(status_code=404, detail="Join request not found")

        was_approved = (membership.status == "approved")
        membership.status = "rejected"
        membership.is_active = False
        membership.reviewed_at = datetime.utcnow()
        membership.reviewer_id = current_admin.id

        if was_approved:
            community = self.repo.get_community(membership.community_id)
            if community and community.active_members_count > 0:
                community.active_members_count -= 1
                self.repo.save(community)

        saved = self._save(membership)
        return AdminMembershipResponse.model_validate(saved)

    def challenges(self, community_id: int | None = None) -> list[Challenge]:
        if community_id is not None:
            self.community(community_id)
        return self.repo.list_challenges(community_id)

    def challenge(self, challenge_id: int) -> Challenge:
        item = self.repo.get_challenge(challenge_id)
        if not item:
            raise HTTPException(status_code=404, detail="Challenge not found")
        return item

    def create_challenge(self, data: ChallengeCreate) -> Challenge:
        self.community(data.community_id)
        return self._save(
            Challenge(
                community_id=data.community_id,
                title=data.title,
                description=data.description,
                difficulty=data.difficulty,
                xp_reward=data.xp_reward,
                deadline=data.deadline,
                is_active=data.is_active,
            )
        )

    def update_challenge(self, challenge_id: int, data: ChallengeUpdate) -> Challenge:
        item = self.challenge(challenge_id)
        values = data.model_dump(exclude_unset=True)
        if "community_id" in values:
            self.community(values["community_id"])
        for key, value in values.items():
            setattr(item, key, value)
        return self._save(item)

    def delete_challenge(self, challenge_id: int) -> None:
        self._delete(self.challenge(challenge_id))

    def events(self, community_id: int | None = None) -> list[Event]:
        if community_id is not None:
            self.community(community_id)
        return self.repo.list_events(community_id)

    def event(self, event_id: int) -> Event:
        item = self.repo.get_event(event_id)
        if not item:
            raise HTTPException(status_code=404, detail="Event not found")
        return item

    def create_event(self, data: EventCreate) -> Event:
        self.community(data.community_id)
        return self._save(
            Event(
                community_id=data.community_id,
                title=data.title,
                description=data.description,
                event_date=data.event_date,
                status=data.status,
            )
        )

    def update_event(self, event_id: int, data: EventUpdate) -> Event:
        item = self.event(event_id)
        values = data.model_dump(exclude_unset=True)
        if "community_id" in values:
            self.community(values["community_id"])
        for key, value in values.items():
            setattr(item, key, value)
        return self._save(item)

    def delete_event(self, event_id: int) -> None:
        self._delete(self.event(event_id))
