from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.community import Community, CommunityMembership, AssessmentData
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

    def create_membership(self, user_id: int, community_id: int, assessment_data: JoinCommunityRequest) -> CommunityMembership:
        # Create membership
        membership = CommunityMembership(user_id=user_id, community_id=community_id)
        self.db.add(membership)
        self.db.flush() # To get membership.id

        # Update community active members
        community = self.get_community_by_id(community_id)
        if community:
            community.active_members_count += 1
            self.db.add(community)

        # Create assessment data
        assessment = AssessmentData(
            membership_id=membership.id,
            skill_level=assessment_data.skill_level,
            languages_known=",".join(assessment_data.languages_known),
            problem_solving_comfort=assessment_data.problem_solving_comfort,
            main_goal=assessment_data.main_goal,
            weekly_time_commitment=assessment_data.weekly_time_commitment
        )
        self.db.add(assessment)
        
        self.db.commit()
        self.db.refresh(membership)
        return membership
