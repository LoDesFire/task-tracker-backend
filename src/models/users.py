import datetime
import uuid
from typing import ClassVar, Optional

from sqlalchemy import UUID, Boolean, DateTime, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import IDBase
from src.models.mixins.timestamp_mixins import TimestampMixin

UsersIDType = uuid.UUID


class Users(IDBase, TimestampMixin):
    id: Mapped[UsersIDType] = mapped_column(
        UUID,
        primary_key=True,
        info={"sortable": False},
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    email: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        info={"sortable": False},
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        index=True,
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
