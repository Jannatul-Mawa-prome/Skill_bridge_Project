from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.community import Community, CommunityMembership
from app.models.user import User

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
            raise HTTPException(
                status_code=400,
                detail="User already joined this community"
            )

        membership = self.community_repo.create_membership(
            user_id,
            community_id,
            request
        )

        return {
            "message": "Successfully joined community",
            "membership_id": membership.id,
            "community_id": community_id
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
                CommunityMembership.user_id == user_id
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

        if not membership:
            raise HTTPException(
                status_code=403,
                detail="Not a member of this community"
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

            # Sort modules
            modules_sorted = sorted(
                roadmap.modules,
                key=lambda m: m.order
            )

            module_schemas = []

            for module in modules_sorted:

                # Sort tasks
                tasks_sorted = sorted(
                    module.tasks,
                    key=lambda t: t.order
                )

                task_schemas = []

                module_completed_tasks = 0

                # -------------------------------------------------
                # Build tasks
                # -------------------------------------------------

                for task in tasks_sorted:

                    total_tasks_count += 1

                    is_completed = progress_map.get(
                        task.id,
                        False
                    )

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

                # -------------------------------------------------
                # Module progress
                # -------------------------------------------------

                mod_progress = 0

                if len(tasks_sorted) > 0:

                    mod_progress = int(
                        (
                            module_completed_tasks
                            / len(tasks_sorted)
                        ) * 100
                    )

                # -------------------------------------------------
                # Module status
                # -------------------------------------------------

                module_status = "locked"

                if mod_progress == 100:

                    module_status = "completed"

                elif (
                    mod_progress > 0
                    or module.order == 1
                ):

                    module_status = "in_progress"

                # -------------------------------------------------
                # Module schema
                # -------------------------------------------------

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

            # -----------------------------------------------------
            # Roadmap schema
            # -----------------------------------------------------

            roadmap_schema = RoadmapSchema(
                id=roadmap.id,
                title=roadmap.title,
                description=roadmap.description,
                total_modules=len(module_schemas),
                total_tasks=total_tasks_count,
                completed_tasks=completed_tasks_count,
                modules=module_schemas
            )

        # ---------------------------------------------------------
        # Overall progress
        # ---------------------------------------------------------

        progress_percentage = 0

        if total_tasks_count > 0:

            progress_percentage = int(
                (
                    completed_tasks_count
                    / total_tasks_count
                ) * 100
            )

        # ---------------------------------------------------------
        # Dashboard statistics
        # ---------------------------------------------------------

        stats = DashboardStatsResponse(
            roadmap_progress_percentage=progress_percentage,
            current_streak_days=membership.streak,
            completed_tasks_count=completed_tasks_count,
            community_rank=12
        )

        # ---------------------------------------------------------
        # Final dashboard response
        # ---------------------------------------------------------

        return DashboardResponse(
            user_name=(
                user.profile.full_name
                if user.profile
                and user.profile.full_name
                else "User"
            ),
            stats=stats,
            roadmap=roadmap_schema
        )
    

    def check_membership(self, user_id: int, community_id: int):

        membership = self.community_repo.get_membership(
            user_id,
            community_id
        )

        return {
            "is_member": membership is not None
        }