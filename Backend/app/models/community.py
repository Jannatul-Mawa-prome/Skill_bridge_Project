from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base

if TYPE_CHECKING:
    from app.models.user import User

if TYPE_CHECKING:
    from app.models.roadmap import Roadmap
    
class Community(Base):
    __tablename__ = "communities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    active_members_count: Mapped[int] = mapped_column(Integer, default=0)

    roadmaps: Mapped[List["Roadmap"]] = relationship(
        back_populates="community",
        cascade="all, delete-orphan"
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

    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="member")
    streak: Mapped[int] = mapped_column(Integer, default=0)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()
    community: Mapped["Community"] = relationship(back_populates="memberships")
    assessment: Mapped["AssessmentData"] = relationship(
        back_populates="membership", uselist=False, cascade="all, delete-orphan"
    )


class AssessmentData(Base):
    __tablename__ = "assessment_data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    membership_id: Mapped[int] = mapped_column(ForeignKey("community_memberships.id", ondelete="CASCADE"), unique=True)
    
    skill_level: Mapped[str] = mapped_column(String(50))
    languages_known: Mapped[str] = mapped_column(String(255)) # comma separated
    problem_solving_comfort: Mapped[str] = mapped_column(String(50))
    main_goal: Mapped[str] = mapped_column(String(100))
    weekly_time_commitment: Mapped[str] = mapped_column(String(50))

    membership: Mapped["CommunityMembership"] = relationship(back_populates="assessment")
