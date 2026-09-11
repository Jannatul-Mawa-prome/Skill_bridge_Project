from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


QuestionType = Literal["text", "single_choice", "multi_choice"]


class CommunityQuestionOption(BaseModel):
    value: str
    label: str
    description: str | None = None


class CommunityQuestionResponse(BaseModel):
    id: int
    community_id: int
    question_key: str
    prompt: str
    question_type: QuestionType
    options: list[CommunityQuestionOption] | None = None
    order: int
    is_required: bool

    model_config = ConfigDict(from_attributes=True)


class CommunityQuestionCreate(BaseModel):
    question_key: str = Field(..., min_length=1, max_length=100)
    prompt: str = Field(..., min_length=1)
    question_type: QuestionType
    options: list[CommunityQuestionOption] | None = None
    order: int = Field(..., ge=1)
    is_required: bool = True


class CommunityQuestionUpdate(BaseModel):
    prompt: str | None = Field(default=None, min_length=1)
    question_type: QuestionType | None = None
    options: list[CommunityQuestionOption] | None = None
    order: int | None = Field(default=None, ge=1)
    is_required: bool | None = None
    is_active: bool | None = None
