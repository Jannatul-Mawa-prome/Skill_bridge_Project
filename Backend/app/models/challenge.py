from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.community import Community
    from app.models.user import User

from app.database.connection import Base

class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False, default="easy")
    xp_reward: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    community: Mapped["Community"] = relationship(backref="challenges")

class UserChallenge(Base):
    __tablename__ = "user_challenges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed") # 'active', 'completed'
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(backref="challenge_progress")
    challenge: Mapped["Challenge"] = relationship(backref="user_progress")
