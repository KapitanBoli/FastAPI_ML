from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Video(Base):
    status: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[JSON] = mapped_column(JSON, nullable=True)
