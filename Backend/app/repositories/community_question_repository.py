from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.community_question import CommunityQuestion


class CommunityQuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_questions(self, community_id: int) -> list[CommunityQuestion]:
        return self.db.execute(
            select(CommunityQuestion)
            .where(CommunityQuestion.community_id == community_id)
            .where(CommunityQuestion.is_active.is_(True))
            .order_by(CommunityQuestion.order, CommunityQuestion.id)
        ).scalars().all()

    def get_question_by_key(
        self,
        community_id: int,
        question_key: str,
    ) -> CommunityQuestion | None:
        return self.db.execute(
            select(CommunityQuestion)
            .where(CommunityQuestion.community_id == community_id)
            .where(CommunityQuestion.question_key == question_key)
        ).scalar_one_or_none()

    def get_question_by_id(
        self,
        community_id: int,
        question_id: int,
    ) -> CommunityQuestion | None:
        return self.db.execute(
            select(CommunityQuestion)
            .where(CommunityQuestion.community_id == community_id)
            .where(CommunityQuestion.id == question_id)
        ).scalar_one_or_none()

    def create_question(
        self,
        community_id: int,
        question_data: dict,
    ) -> CommunityQuestion:
        question = CommunityQuestion(
            community_id=community_id,
            **question_data,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update_question(
        self,
        question: CommunityQuestion,
        question_data: dict,
    ) -> CommunityQuestion:
        for field, value in question_data.items():
            setattr(question, field, value)

        self.db.commit()
        self.db.refresh(question)
        return question
