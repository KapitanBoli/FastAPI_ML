from datetime import datetime, timezone
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def get_current_dt() -> datetime:
    dt = datetime.now(tz=timezone.utc)
    return dt.replace(tzinfo=None)


class User(Base):
    name: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=get_current_dt, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_dt,
        onupdate=get_current_dt,
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )
