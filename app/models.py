import datetime
from . import utils

from sqlalchemy import Integer, String, TEXT, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_url: Mapped[str] = mapped_column(TEXT, nullable=False)

    short_code: Mapped[str] = mapped_column(String(8), unique=True, index=True, default=utils.generate_short_code)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
