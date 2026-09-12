from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.community import CommunityMembership
    from app.models.community_question import CommunityQuestion


class CommunityAnswer(Base):
    __tablename__ = "community_answers"
    __table_args__ = (
        UniqueConstraint(
            "membership_id",
            "question_id",
            name="uq_community_answers_membership_question",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    membership_id: Mapped[int] = mapped_column(
        ForeignKey("community_memberships.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("community_questions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    answer: Mapped[Any] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    membership: Mapped["CommunityMembership"] = relationship(back_populates="answers")
    question: Mapped["CommunityQuestion"] = relationship()
