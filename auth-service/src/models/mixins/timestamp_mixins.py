import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.datetime.now(tz=datetime.timezone.utc).replace(tzinfo=None),
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.datetime.now(tz=datetime.timezone.utc).replace(tzinfo=None),
    )


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    """TimestampMixin"""
