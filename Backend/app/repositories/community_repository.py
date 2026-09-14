from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from app.models.community import Community, CommunityMembership, AssessmentData
from app.models.community_answer import CommunityAnswer
from app.models.community_question import CommunityQuestion
from app.schemas.community import JoinCommunityRequest

class CommunityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_community_by_name(self, name: str) -> Community | None:
        return self.db.execute(select(Community).where(Community.name == name)).scalar_one_or_none()

    def get_community_by_id(self, community_id: int) -> Community | None:
        return self.db.execute(select(Community).where(Community.id == community_id)).scalar_one_or_none()

    def get_all_communities(self) -> list[Community]:
        return self.db.execute(select(Community)).scalars().all()

    def create_community(self, name: str, description: str = None) -> Community:
        community = Community(name=name, description=description)
        self.db.add(community)
        self.db.commit()
        self.db.refresh(community)
        return community

    def get_membership(self, user_id: int, community_id: int) -> CommunityMembership | None:
        return self.db.execute(
            select(CommunityMembership)
            .where(CommunityMembership.user_id == user_id)
            .where(CommunityMembership.community_id == community_id)
        ).scalar_one_or_none()

    def get_membership_answers(self, membership_id: int) -> list[tuple[str, object]]:
        rows = self.db.execute(
            select(CommunityAnswer.answer, CommunityQuestion.question_key)
            .join(
                CommunityQuestion,
                CommunityQuestion.id == CommunityAnswer.question_id,
            )
            .where(CommunityAnswer.membership_id == membership_id)
            .order_by(CommunityQuestion.order, CommunityQuestion.id)
        ).all()
        return [(question_key, answer) for answer, question_key in rows]

    def get_user_memberships(self, user_id: int, status: str | None = None) -> list[CommunityMembership]:
        query = select(CommunityMembership).where(CommunityMembership.user_id == user_id)
        if status:
            query = query.where(CommunityMembership.status == status)
        return self.db.execute(query).scalars().all()

    def create_membership(
        self,
        user_id: int,
        community_id: int,
        assessment_data: JoinCommunityRequest,
        answers: list[tuple[CommunityQuestion, object]] | None = None,
        status: str = "pending",
    ) -> CommunityMembership:
        # Create or update existing membership
        membership = self.get_membership(user_id, community_id)
        if not membership:
            membership = CommunityMembership(
                user_id=user_id,
                community_id=community_id,
                status=status,
                is_active=(status == "approved"),
            )
            self.db.add(membership)
            self.db.flush()
        else:
            membership.status = status
            membership.is_active = (status == "approved")
            membership.joined_at = datetime.utcnow()
            membership.reviewed_at = None
            membership.reviewer_id = None
            self.db.add(membership)
            self.db.flush()

        # Update community active members only if approved
        if status == "approved":
            community = self.get_community_by_id(community_id)
            if community:
                community.active_members_count += 1
                self.db.add(community)

        # Extract assessment fields from answers if provided
        ans_dict = {q.question_key: ans for q, ans in (answers or [])}
        skill_level = ans_dict.get("skill_level") or assessment_data.skill_level
        lang_val = (
            ans_dict.get("languages_known")
            or ans_dict.get("technologies_known")
            or assessment_data.languages_known
        )
        languages_known = (
            ",".join(lang_val)
            if isinstance(lang_val, list)
            else (str(lang_val) if lang_val else None)
        )
        problem_solving_comfort = (
            ans_dict.get("problem_solving_comfort")
            or assessment_data.problem_solving_comfort
        )
        main_goal = ans_dict.get("main_goal") or assessment_data.main_goal
        weekly_time_commitment = (
            ans_dict.get("weekly_time_commitment")
            or assessment_data.weekly_time_commitment
        )

        # Create or update assessment data
        assessment = self.db.execute(
            select(AssessmentData).where(AssessmentData.membership_id == membership.id)
        ).scalar_one_or_none()

        if not assessment:
            assessment = AssessmentData(
                membership_id=membership.id,
                skill_level=skill_level,
                languages_known=languages_known,
                problem_solving_comfort=problem_solving_comfort,
                main_goal=main_goal,
                weekly_time_commitment=weekly_time_commitment,
            )
            self.db.add(assessment)
        else:
            assessment.skill_level = skill_level
            assessment.languages_known = languages_known
            assessment.problem_solving_comfort = problem_solving_comfort
            assessment.main_goal = main_goal
            assessment.weekly_time_commitment = weekly_time_commitment
            self.db.add(assessment)

        # Delete previous answers if re-applying
        self.db.execute(
            delete(CommunityAnswer).where(CommunityAnswer.membership_id == membership.id)
        )
        self.db.flush()

        for question, answer in answers or []:
            self.db.add(
                CommunityAnswer(
                    membership_id=membership.id,
                    question_id=question.id,
                    answer=answer,
                )
            )
        
        self.db.commit()
        self.db.refresh(membership)
        return membership
