from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.community import Community, CommunityMembership
from app.models.community_question import CommunityQuestion
from app.models.user import User

from app.repositories.community_repository import CommunityRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.community_question_repository import CommunityQuestionRepository
from app.repositories.community_content_repository import CommunityContentRepository

from app.schemas.community import (
    JoinCommunityRequest,
    JoinCommunityAnswer,
    DashboardResponse,
    DashboardAnswerResponse,
    DashboardCommunityResponse,
    DashboardMembershipResponse,
    DashboardStatsResponse,
    RoadmapSchema,
    ModuleSchema,
    TaskSchema,
    CommunityListSchema,
    DashboardResourceResponse,
    DashboardMemberResponse,
)


class CommunityService:

    def __init__(self, db: Session):
        self.db = db
        self.community_repo = CommunityRepository(db)
        self.roadmap_repo = RoadmapRepository(db)
        self.question_repo = CommunityQuestionRepository(db)
        self.content_repo = CommunityContentRepository(db)

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

        questions = self.question_repo.get_active_questions(community_id)
        answer_pairs = self._validate_join_answers(questions, request)
        membership = self.community_repo.create_membership(
            user_id,
            community_id,
            request,
            answer_pairs,
        )

        return {
            "message": "Successfully joined community",
            "membership_id": membership.id,
            "community_id": community_id
        }

    def _validate_join_answers(
        self,
        questions: list[CommunityQuestion],
        request: JoinCommunityRequest,
    ) -> list[tuple[CommunityQuestion, object]]:
        if not request.answers:
            legacy_values = {
                "skill_level": request.skill_level,
                "languages_known": request.languages_known,
                "technologies_known": request.languages_known,
                "problem_solving_comfort": request.problem_solving_comfort,
                "main_goal": request.main_goal,
                "weekly_time_commitment": request.weekly_time_commitment,
            }
            answers = [
                JoinCommunityAnswer(question_key=key, value=value)
                for key, value in legacy_values.items()
                if value is not None and any(
                    question.question_key == key for question in questions
                )
            ]
        else:
            answers = request.answers

        answer_map = {answer.question_key: answer.value for answer in answers}
        question_map = {question.question_key: question for question in questions}
        unknown_keys = set(answer_map) - set(question_map)
        if unknown_keys:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown community question(s): {', '.join(sorted(unknown_keys))}",
            )

        missing = [
            question.question_key
            for question in questions
            if question.is_required and question.question_key not in answer_map
        ]
        if missing:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required answer(s): {', '.join(missing)}",
            )

        validated: list[tuple[CommunityQuestion, object]] = []
        for key, value in answer_map.items():
            question = question_map[key]
            if question.question_type == "text":
                if not isinstance(value, str) or not value.strip():
                    raise HTTPException(
                        status_code=422,
                        detail=f"Answer for '{key}' must be non-empty text",
                    )
            elif question.question_type == "single_choice":
                if not isinstance(value, str):
                    raise HTTPException(
                        status_code=422,
                        detail=f"Answer for '{key}' must be one option",
                    )
                self._validate_options(question, [value])
            elif question.question_type == "multi_choice":
                if (
                    not isinstance(value, list)
                    or not value
                    or not all(isinstance(item, str) for item in value)
                ):
                    raise HTTPException(
                        status_code=422,
                        detail=f"Answer for '{key}' must contain one or more options",
                    )
                self._validate_options(question, value)

            validated.append((question, value))

        return validated

    @staticmethod
    def _validate_options(
        question: CommunityQuestion,
        values: list[str],
    ) -> None:
        allowed = {
            option["value"]
            for option in (question.options or [])
            if isinstance(option, dict) and "value" in option
        }
        invalid = set(values) - allowed
        if invalid:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid option(s) for '{question.question_key}': {', '.join(sorted(invalid))}",
            )

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

        community = self.community_repo.get_community_by_id(community_id)
        if not community:
            raise HTTPException(
                status_code=404,
                detail="Community not found"
            )

        membership = self.community_repo.get_membership(
            user.id,
            community_id
        )

        if not membership:
            raise HTTPException(
                status_code=403,
                detail="Not a member of this community"
            )

        answer_rows = self.community_repo.get_membership_answers(membership.id)
        resources = self.content_repo.get_resources(community_id)
        challenges = self.content_repo.get_challenges(community_id)
        challenge_statuses = self.content_repo.get_user_challenge_status(
            user.id, [challenge.id for challenge in challenges]
        )
        for challenge in challenges:
            challenge.user_status = challenge_statuses.get(challenge.id)
        discussions = self.content_repo.get_discussions(community_id)
        announcements = self.content_repo.get_announcements(community_id)
        events = self.content_repo.get_events(community_id)
        registered_events = self.content_repo.get_registered_event_ids(
            user.id, [event.id for event in events]
        )
        for event in events:
            event.is_registered = event.id in registered_events
        members = self.content_repo.get_members(community_id)

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
            community=DashboardCommunityResponse(
                id=community.id,
                name=community.name,
                description=community.description,
                active_members_count=community.active_members_count,
            ),
            membership=DashboardMembershipResponse(
                id=membership.id,
                role=membership.role,
                streak=membership.streak,
                joined_at=membership.joined_at,
            ),
            answers=[
                DashboardAnswerResponse(question_key=key, value=value)
                for key, value in answer_rows
            ],
            stats=stats,
            roadmap=roadmap_schema,
            resources=[
                DashboardResourceResponse(
                    id=resource.id,
                    title=resource.title,
                    resource_type=resource.resource_type,
                    difficulty=resource.difficulty,
                    url=resource.url,
                    description=resource.description,
                )
                for resource in resources
            ],
            challenges=challenges,
            discussions=discussions,
            announcements=announcements,
            events=events,
            members=[
                DashboardMemberResponse(
                    user_id=membership_row.user_id,
                    name=profile.full_name,
                    role=membership_row.role,
                )
                for membership_row, profile in members
            ],
        )
    

    def check_membership(self, user_id: int, community_id: int):

        membership = self.community_repo.get_membership(
            user_id,
            community_id
        )

        return {
            "is_member": membership is not None
        }