from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.community import Community
    from app.models.user import User

from app.database.connection import Base

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    community_id: Mapped[int] = mapped_column(ForeignKey("communities.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="active") # active, completed
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    community: Mapped["Community"] = relationship(backref="projects")
    members: Mapped[list["ProjectMember"]] = relationship(back_populates="project")

class ProjectMember(Base):
    __tablename__ = "project_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()
