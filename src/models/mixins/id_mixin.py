from uuid import UUID

from sqlalchemy.orm import Mapped

IDType = int | str | UUID


class IDMixin:
    id: Mapped[IDType]
