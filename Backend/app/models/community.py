from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.user import User

if TYPE_CHECKING:
    from app.models.roadmap import Roadmap
    from app.models.community_question import CommunityQuestion
    from app.models.community_answer import CommunityAnswer
    
class Community(Base):
    __tablename__ = "communities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    active_members_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    roadmaps: Mapped[List["Roadmap"]] = relationship(
        back_populates="community",
        cascade="all, delete-orphan"
    )

    questions: Mapped[List["CommunityQuestion"]] = relationship(
        back_populates="community",
        cascade="all, delete-orphan",
        order_by="CommunityQuestion.order",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    memberships: Mapped[List["CommunityMembership"]] = relationship(
        back_populates="community",
        cascade="all, delete-orphan"
    )

class CommunityMembership(Base):
    __tablename__ = "community_memberships"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id", ondelete="CASCADE"), index=True)
    
    role: Mapped[str] = mapped_column(String(50), default="member")
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewer_id])
    community: Mapped["Community"] = relationship(back_populates="memberships")
    answers: Mapped[List["CommunityAnswer"]] = relationship(
        back_populates="membership",
        cascade="all, delete-orphan",
    )
    assessment: Mapped["AssessmentData"] = relationship(
        back_populates="membership", uselist=False, cascade="all, delete-orphan"
    )


class AssessmentData(Base):
    __tablename__ = "assessment_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    membership_id: Mapped[int] = mapped_column(ForeignKey("community_memberships.id", ondelete="CASCADE"), unique=True)
    
    skill_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    languages_known: Mapped[str | None] = mapped_column(String(255), nullable=True)
    problem_solving_comfort: Mapped[str | None] = mapped_column(String(50), nullable=True)
    main_goal: Mapped[str | None] = mapped_column(String(100), nullable=True)
    weekly_time_commitment: Mapped[str | None] = mapped_column(String(50), nullable=True)

    membership: Mapped["CommunityMembership"] = relationship(back_populates="assessment")
