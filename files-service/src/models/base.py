import uuid
from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, declared_attr

from models.mixins.id_mixin import IDMixin


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {"schema": "files"}

    __T = TypeVar("__T", bound=BaseModel)

    def to_pydantic(self, pydantic_cls: Type[__T]):
        return pydantic_cls(**self.__dict__)


UsersIDType = uuid.UUID

class IDBase(Base, IDMixin):
    __abstract__ = True
