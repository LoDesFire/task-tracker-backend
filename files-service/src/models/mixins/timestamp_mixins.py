import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )
