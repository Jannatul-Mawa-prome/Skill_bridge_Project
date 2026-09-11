from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{settings.database_user}:"
    f"{settings.database_password}@"
    f"{settings.database_host}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)


engine = create_engine(
    DATABASE_URL,
    echo=True
)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)