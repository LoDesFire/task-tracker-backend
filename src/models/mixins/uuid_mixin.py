import uuid

from sqlalchemy import UUID, text
from sqlalchemy.orm import Mapped, mapped_column


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(
        UUID,
        primary_key=True,
        info={"sortable": False},
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
