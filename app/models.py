import datetime
from . import utils

from typing import List, Optional
from sqlalchemy import Integer, String, TEXT, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass



class User(Base):
    __tablename__ = 'users_table'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)


    urls: Mapped[List['URL']] = relationship(back_populates="owner")

    
class URL(Base):
    __tablename__ = "urls_table"

    url_id: Mapped[int] = mapped_column(primary_key=True)
    target_url: Mapped[str] = mapped_column(TEXT, nullable=False)

    short_code: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    clicks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())

    owned_by: Mapped[Optional[int]] = mapped_column(ForeignKey('users_table.id'))

    owner: Mapped[Optional['User']] = relationship(back_populates="urls")

