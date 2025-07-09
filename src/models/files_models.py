from sqlalchemy import Integer, String, Text, ForeignKey, UUID, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.models.base import Base, IDBase, UsersIDType
from src.models.mixins.id_mixin import IDMixin
from src.models.mixins.timestamp_mixins import CreatedAtMixin


class Files(Base, IDMixin, CreatedAtMixin):
    __table_args__ = (
        UniqueConstraint("bucket", "s3_object_key"),
        {"schema": "files"},
    )

    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
    )
    bucket: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    s3_object_key: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    original_filename: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    project_file = relationship("ProjectFiles", back_populates="file")
    user_file = relationship("UserFiles", back_populates="file")


class ProjectFiles(IDBase):
    __tablename__ = "project_files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    project_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    file_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Files.id),
        nullable=False,
        unique=True,
    )

    file = relationship("Files", back_populates="project_file")


class UserFiles(IDBase):
    __tablename__ = "user_files"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    user_id: Mapped[UsersIDType] = mapped_column(
        UUID,
        nullable=False,
        index=True,
    )
    file_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Files.id),
        nullable=False,
        unique=True,
    )

    file = relationship("Files", back_populates="user_file")
