from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
from app.database.connection import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    roll: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False
    )

    semester: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    mobile: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    university: Mapped[str] = mapped_column(
        String(150),
        nullable=True
    )

    bio: Mapped[str] = mapped_column(
        String(500),
        nullable=True
    )

    profile_picture: Mapped[str] = mapped_column(
        String(255),
        nullable=True
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
    user: Mapped["User"] = relationship(
        back_populates="profile"
    )