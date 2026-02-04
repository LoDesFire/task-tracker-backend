from typing import Any, Optional, Type, TypeVar

import sqlalchemy.exc
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing_extensions import Generic

from helpers.exceptions.repository_exceptions import (
    RepositoryIntegrityException,
    RepositoryNotFoundException,
)
from models.base import IDBase
from models.mixins.id_mixin import IDType

_T = TypeVar("_T", bound=IDBase)


class EntityDbRepository(Generic[_T]):
    model: Type[_T]

    def __init__(self, db_session: async_sessionmaker[AsyncSession]) -> None:
        self.db_session = db_session

    async def get_by_id(self, e_id: IDType) -> _T:
        async with self.db_session() as session:
            result = await session.scalars(
                select(self.model).where(self.model.id.__eq__(e_id))
            )
            entity = result.first()
            if entity is None:
                raise RepositoryNotFoundException(
                    "Entity {} not found".format(self.model.__name__)
                )
            return entity  # type: ignore

    async def create(self, entity: _T) -> _T:
        async with self.db_session() as session:
            try:
                session.add(entity)
                await session.commit()
            except sqlalchemy.exc.IntegrityError as exc:
                raise RepositoryIntegrityException(
                    "Can't commit entity {} creating".format(self.model.__name__)
                ) from exc

            await session.refresh(entity)
            return entity

    async def update(self, e_id: IDType, **kwargs: Any) -> _T:
        async with self.db_session() as session:
            try:
                updated_entity = await session.scalars(
                    update(self.model)
                    .where(self.model.id.__eq__(e_id))
                    .values(**kwargs)
                    .returning(self.model)
                )
                await session.commit()
                return updated_entity.first()  # type: ignore
            except sqlalchemy.exc.IntegrityError as exc:
                raise RepositoryIntegrityException(
                    "Can't commit entity {} updating".format(self.model.__name__)
                ) from exc

    async def delete(self, e_id: IDType) -> Optional[IDType]:
        async with self.db_session() as session:
            try:
                deleted_entity_id = await session.scalars(
                    delete(self.model)
                    .where(self.model.id.__eq__(e_id))
                    .returning(self.model.id)
                )
                await session.commit()
                return deleted_entity_id.first()
            except sqlalchemy.exc.IntegrityError as exc:
                raise RepositoryIntegrityException(
                    "Can't commit entity {} removing".format(self.model.__name__)
                ) from exc
