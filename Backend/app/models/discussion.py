from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.community import Community
    from app.models.user import User

from app.database.connection import Base

class Discussion(Base):
    __tablename__ = "discussions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=True)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    community: Mapped["Community"] = relationship(backref="discussions")
    author: Mapped["User"] = relationship()
