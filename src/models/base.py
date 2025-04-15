from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.models.mixins.uuid_mixin import UUIDMixin


class Base(DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {"schema": "auth"}

    __T = TypeVar("__T", bound=BaseModel)

    def to_pydantic(self, pydantic_cls: Type[__T]):
        return pydantic_cls(**self.__dict__)


class UUIDBase(Base, UUIDMixin):
    __abstract__ = True
