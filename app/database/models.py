import datetime
from typing import ClassVar, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.database.mixins.timestamp_mixins import TimestampMixin


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Users(Base, TimestampMixin):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, info={"sortable": False}
    )

    email: Mapped[str] = mapped_column(String(128), nullable=False)
    username: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(
        Text, nullable=False, info={"sortable": False}
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    _sortable_fields: ClassVar[Optional[set]] = None

    @classmethod
    def sortable_fields(cls):
        if cls._sortable_fields is None:
            cls._sortable_fields = {
                column_name
                for column_name, attrs in Users.__mapper__.c.items()
                if attrs.info.get("sortable", True)
            }
        return cls._sortable_fields
