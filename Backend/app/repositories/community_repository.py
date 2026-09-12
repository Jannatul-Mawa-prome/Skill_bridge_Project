from sqlalchemy.orm import Session
from sqlalchemy import select

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
            self.db.add(membership)
            self.db.flush()

        # Update community active members only if approved
        if status == "approved":
            community = self.get_community_by_id(community_id)
            if community:
                community.active_members_count += 1
                self.db.add(community)

        # Create or update assessment data
        assessment = self.db.execute(
            select(AssessmentData).where(AssessmentData.membership_id == membership.id)
        ).scalar_one_or_none()

        if not assessment:
            assessment = AssessmentData(
                membership_id=membership.id,
                skill_level=assessment_data.skill_level,
                languages_known=",".join(assessment_data.languages_known) if assessment_data.languages_known else None,
                problem_solving_comfort=assessment_data.problem_solving_comfort,
                main_goal=assessment_data.main_goal,
                weekly_time_commitment=assessment_data.weekly_time_commitment
            )
            self.db.add(assessment)
        else:
            assessment.skill_level = assessment_data.skill_level
            if assessment_data.languages_known:
                assessment.languages_known = ",".join(assessment_data.languages_known)
            assessment.problem_solving_comfort = assessment_data.problem_solving_comfort
            assessment.main_goal = assessment_data.main_goal
            assessment.weekly_time_commitment = assessment_data.weekly_time_commitment
            self.db.add(assessment)

        # Delete previous answers if re-applying
        existing_answers = self.db.execute(
            select(CommunityAnswer).where(CommunityAnswer.membership_id == membership.id)
        ).scalars().all()
        for ans in existing_answers:
            self.db.delete(ans)

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
