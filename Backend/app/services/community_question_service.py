from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.community import Community
from app.repositories.community_question_repository import (
    CommunityQuestionRepository,
)
from app.repositories.community_repository import CommunityRepository
from app.schemas.community_question import (
    CommunityQuestionCreate,
    CommunityQuestionResponse,
    CommunityQuestionUpdate,
)


class CommunityQuestionService:
    def __init__(self, db: Session):
        self.db = db
        self.community_repo = CommunityRepository(db)
        self.question_repo = CommunityQuestionRepository(db)

    def get_active_questions(
        self,
        community_id: int,
    ) -> list[CommunityQuestionResponse]:
        community = self.community_repo.get_community_by_id(community_id)
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")

        return self.question_repo.get_active_questions(community_id)

    def create_question(
        self,
        community_id: int,
        question_data: CommunityQuestionCreate,
    ) -> CommunityQuestionResponse:
        community = self.community_repo.get_community_by_id(community_id)
        if not community:
            raise HTTPException(status_code=404, detail="Community not found")

        if self.question_repo.get_question_by_key(
            community_id,
            question_data.question_key,
        ):
            raise HTTPException(
                status_code=409,
                detail="Question key already exists for this community",
            )

        if question_data.question_type == "text" and question_data.options:
            raise HTTPException(
                status_code=422,
                detail="Text questions cannot define options",
            )

        if question_data.question_type != "text" and not question_data.options:
            raise HTTPException(
                status_code=422,
                detail="Choice questions must define options",
            )

        return self.question_repo.create_question(
            community_id,
            question_data.model_dump(),
        )

    def update_question(
        self,
        community_id: int,
        question_id: int,
        question_data: CommunityQuestionUpdate,
    ) -> CommunityQuestionResponse:
        question = self.question_repo.get_question_by_id(
            community_id,
            question_id,
        )
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        changes = question_data.model_dump(exclude_unset=True)
        question_type = changes.get("question_type", question.question_type)
        options = changes.get("options", question.options)

        if question_type == "text" and options:
            raise HTTPException(
                status_code=422,
                detail="Text questions cannot define options",
            )

        if question_type != "text" and not options:
            raise HTTPException(
                status_code=422,
                detail="Choice questions must define options",
            )

        return self.question_repo.update_question(question, changes)
