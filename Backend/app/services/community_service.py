from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.community import Community, CommunityMembership, AssessmentData
from app.models.profile import Profile
from app.models.user import User
from app.models.resource import Resource
from app.models.announcement import Announcement

from app.repositories.community_repository import CommunityRepository
from app.repositories.roadmap_repository import RoadmapRepository

from app.schemas.community import (
    JoinCommunityRequest,
    DashboardResponse,
    DashboardStatsResponse,
    RoadmapSchema,
    ModuleSchema,
    TaskSchema,
    CommunityListSchema,
    AdminMembershipSummarySchema,
    AdminMembershipDetailSchema,
    AdminMembershipActionSchema,
    ResourceSchema,
    AnnouncementSchema,
)


class CommunityService:

    def __init__(self, db: Session):
        self.db = db
        self.community_repo = CommunityRepository(db)
        self.roadmap_repo = RoadmapRepository(db)

    # =========================================================
    # GET ALL COMMUNITIES
    # =========================================================

    def get_all_communities(self) -> list[CommunityListSchema]:

        communities = self.community_repo.get_all_communities()

        result = []

        for c in communities:

            # Mock topics/challenges for now
            if "Programming" in c.name:
                mock_topics = [
                    "C++",
                    "Python",
                    "Problem Solving"
                ]
            else:
                mock_topics = [
                    "HTML",
                    "CSS",
                    "React"
                ]

            result.append(
                CommunityListSchema(
                    id=c.id,
                    name=c.name,
                    description=c.description,
                    active_members_count=c.active_members_count,
                    topics=mock_topics,
                    challenges_count=15
                )
            )

        return result

    # =========================================================
    # JOIN COMMUNITY
    # =========================================================

    def join_community(
        self,
        user_id: int,
        community_id: int,
        request: JoinCommunityRequest
    ):

        community = self.community_repo.get_community_by_id(
            community_id
        )

        if not community:
            raise HTTPException(
                status_code=404,
                detail="Community not found"
            )

        existing_membership = self.community_repo.get_membership(
            user_id,
            community_id
        )

        if existing_membership:
            if existing_membership.status == "pending":
                raise HTTPException(
                    status_code=400,
                    detail="You already have a pending request."
                )
            if existing_membership.status == "approved":
                raise HTTPException(
                    status_code=400,
                    detail="You are already a member of this community."
                )
            if existing_membership.status == "rejected":
                raise HTTPException(
                    status_code=400,
                    detail="Your previous request was rejected."
                )

        membership = self.community_repo.create_membership(
            user_id,
            community_id,
            request
        )

        return {
            "message": "Request submitted successfully. Your membership is pending approval.",
            "membership_id": membership.id,
            "community_id": community_id,
            "status": membership.status
        }

    # =========================================================
    # GET MY COMMUNITIES
    # =========================================================

    def get_my_communities(
        self,
        user_id: int
    ):

        memberships = (
            self.db.query(CommunityMembership)
            .filter(
                CommunityMembership.user_id == user_id,
                CommunityMembership.status == "approved"
            )
            .all()
        )

        return [
            membership.community
            for membership in memberships
        ]

    # =========================================================
    # GET COMMUNITY DASHBOARD
    # =========================================================

    def get_dashboard_data(
        self,
        user: User,
        community_id: int
    ) -> DashboardResponse:

        # -----------------------------------------------------
        # Check membership
        # -----------------------------------------------------

        membership = self.community_repo.get_membership(
            user.id,
            community_id
        )

        if not membership or membership.status != "approved":
            raise HTTPException(
                status_code=403,
                detail="Dashboard access requires an approved member for this community."
            )

        community = self.community_repo.get_community_by_id(community_id)
        if not community:
            raise HTTPException(
                status_code=404,
                detail="Community not found"
            )

        # -----------------------------------------------------
        # Get roadmap
        # -----------------------------------------------------

        roadmap = self.roadmap_repo.get_roadmap_by_community(
            community_id
        )

        # -----------------------------------------------------
        # Get user's task progress
        # -----------------------------------------------------

        if roadmap:

            progress_list = self.roadmap_repo.get_user_progress(
                user.id,
                roadmap.id
            )

            progress_map = {
                p.task_id: p.is_completed
                for p in progress_list
            }

        else:

            progress_map = {}

        # -----------------------------------------------------
        # Initialize roadmap data
        # -----------------------------------------------------

        roadmap_schema = None

        completed_tasks_count = 0
        total_tasks_count = 0

        # -----------------------------------------------------
        # Build roadmap response
        # -----------------------------------------------------

        if roadmap:

            modules_sorted = sorted(
                roadmap.modules,
                key=lambda m: m.order
            )

            module_schemas = []

            for module in modules_sorted:

                tasks_sorted = sorted(
                    module.tasks,
                    key=lambda t: t.order
                )

                task_schemas = []
                module_completed_tasks = 0

                for task in tasks_sorted:
                    total_tasks_count += 1

                    is_completed = progress_map.get(task.id, False)

                    if is_completed:
                        module_completed_tasks += 1
                        completed_tasks_count += 1

                    task_schemas.append(
                        TaskSchema(
                            id=task.id,
                            title=task.title,
                            is_completed=is_completed
                        )
                    )

                mod_progress = 0
                if len(tasks_sorted) > 0:
                    mod_progress = int((module_completed_tasks / len(tasks_sorted)) * 100)

                module_status = "locked"
                if mod_progress == 100:
                    module_status = "completed"
                elif mod_progress > 0 or module.order == 1:
                    module_status = "in_progress"

                module_schemas.append(
                    ModuleSchema(
                        id=module.id,
                        title=module.title,
                        description=module.description,
                        status=module_status,
                        progress_percentage=mod_progress,
                        tasks=task_schemas
                    )
                )

            roadmap_schema = RoadmapSchema(
                id=roadmap.id,
                title=roadmap.title,
                description=roadmap.description,
                total_modules=len(module_schemas),
                total_tasks=total_tasks_count,
                completed_tasks=completed_tasks_count,
                modules=module_schemas
            )

        progress_percentage = 0
        if total_tasks_count > 0:
            progress_percentage = int((completed_tasks_count / total_tasks_count) * 100)

        resources = (
            self.db.query(Resource)
            .filter(Resource.community_id == community_id, Resource.is_active.is_(True))
            .order_by(Resource.created_at.desc())
            .all()
        )
        announcements = (
            self.db.query(Announcement)
            .filter(Announcement.community_id == community_id)
            .order_by(Announcement.created_at.desc())
            .all()
        )

        resource_schemas = [
            ResourceSchema(
                id=r.id,
                community_id=r.community_id,
                module_id=r.module_id,
                title=r.title,
                resource_type=r.resource_type,
                difficulty=r.difficulty,
                url=r.url,
                description=r.description,
                is_active=r.is_active
            )
            for r in resources
        ]

        announcement_schemas = [
            AnnouncementSchema(
                id=a.id,
                title=a.title,
                content=a.content,
                created_at=a.created_at.isoformat() if a.created_at else None,
                author_name=(a.author.profile.full_name if a.author and a.author.profile else "Community Team")
            )
            for a in announcements
        ]

        stats = DashboardStatsResponse(
            roadmap_progress_percentage=progress_percentage,
            current_streak_days=membership.streak,
            completed_tasks_count=completed_tasks_count,
            community_rank=12
        )

        return DashboardResponse(
            user_name=(
                user.profile.full_name
                if user.profile
                and user.profile.full_name
                else "User"
            ),
            community_id=community.id,
            community_name=community.name,
            stats=stats,
            roadmap=roadmap_schema,
            resources=resource_schemas,
            announcements=announcement_schemas
        )
    

    def check_membership(self, user_id: int, community_id: int):

        membership = self.community_repo.get_membership(
            user_id,
            community_id
        )

        status = membership.status if membership else "none"

        return {
            "is_member": membership is not None and membership.status == "approved",
            "status": status,
            "can_access_dashboard": membership is not None and membership.status == "approved"
        }

    def get_pending_memberships_for_admin(self) -> list[AdminMembershipSummarySchema]:
        memberships = self.community_repo.get_pending_memberships()
        result = []

        for membership in memberships:
            user = membership.user
            profile = user.profile if user and hasattr(user, "profile") else None
            community = membership.community
            result.append(
                AdminMembershipSummarySchema(
                    id=membership.id,
                    user_id=user.id if user else 0,
                    community_id=community.id if community else 0,
                    community_name=community.name if community else "Unknown",
                    student_name=profile.full_name if profile else "Unknown Student",
                    student_email=user.edu_email if user else "",
                    student_roll=profile.roll if profile else None,
                    status=membership.status,
                    request_date=membership.joined_at.isoformat() if membership.joined_at else ""
                )
            )

        return result

    def get_membership_request_detail(self, membership_id: int) -> AdminMembershipDetailSchema:
        membership = self.community_repo.get_membership_by_id(membership_id)
        if membership is None:
            raise HTTPException(status_code=404, detail="Membership request not found.")

        user = membership.user
        profile = user.profile if user and hasattr(user, "profile") else None
        community = membership.community
        assessment = membership.assessment

        answers = {}
        if assessment:
            answers = {
                "skill_level": assessment.skill_level,
                "languages_known": assessment.languages_known.split(",") if assessment.languages_known else [],
                "problem_solving_comfort": assessment.problem_solving_comfort,
                "main_goal": assessment.main_goal,
                "weekly_time_commitment": assessment.weekly_time_commitment,
            }

        return AdminMembershipDetailSchema(
            id=membership.id,
            user_id=user.id if user else 0,
            community_id=community.id if community else 0,
            community_name=community.name if community else "Unknown",
            student_name=profile.full_name if profile else "Unknown Student",
            student_email=user.edu_email if user else "",
            student_roll=profile.roll if profile else None,
            status=membership.status,
            request_date=membership.joined_at.isoformat() if membership.joined_at else "",
            answers=answers,
        )

    def review_membership_request(self, membership_id: int, action: str, current_user: User) -> AdminMembershipActionSchema:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required.")

        membership = self.community_repo.get_membership_by_id(membership_id)
        if membership is None:
            raise HTTPException(status_code=404, detail="Membership request not found.")

        if membership.status != "pending":
            raise HTTPException(status_code=400, detail="This request is no longer pending.")

        action = action.lower()
        if action not in {"approve", "reject"}:
            raise HTTPException(status_code=400, detail="Invalid action.")

        new_status = "approved" if action == "approve" else "rejected"
        updated = self.community_repo.update_membership_status(membership_id, new_status)

        if action == "approve":
            if updated.community is not None:
                updated.community.active_members_count = max(0, updated.community.active_members_count)
            return AdminMembershipActionSchema(
                membership_id=updated.id,
                community_id=updated.community_id,
                status="approved",
                message="Membership request approved."
            )

        return AdminMembershipActionSchema(
            membership_id=updated.id,
            community_id=updated.community_id,
            status="rejected",
            message="Membership request rejected."
        )