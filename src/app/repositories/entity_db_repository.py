from collections import namedtuple
from math import ceil
from typing import Any, Optional, Type, TypeVar

import sqlalchemy.exc
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing_extensions import Generic

from src.helpers.exceptions.repository_exceptions import (
    RepositoryException,
    RepositoryIntegrityException,
    RepositoryNotFoundException,
)
from src.models.base import IDBase
from src.models.mixins.id_mixin import IDType

_T = TypeVar("_T", bound=IDBase)


class EntityDbRepository(Generic[_T]):
    model: Type[_T]

    SearchResult = namedtuple(
        "SearchResult",
        [
            "total_items_count",
            "items",
            "page_number",
            "page_count",
        ],
    )

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

    async def search(
        self,
        filters: dict[str, Any],
        sort_by: list[str],
        page_number: int,
        page_size: int,
    ) -> SearchResult:
        filter_clauses = []
        for field, filter_value in filters.items():
            filter_clauses.append(getattr(self.model, field).__eq__(filter_value))

        filtered_query = select(self.model).where(*filter_clauses)
        count_query = select(func.count(self.model.id)).where(*filter_clauses)

        for sort_field in sort_by:
            if sort_field.startswith("-"):
                filtered_query = filtered_query.order_by(
                    getattr(self.model, sort_field[1:]).desc()
                )
            else:
                filtered_query = filtered_query.order_by(
                    getattr(self.model, sort_field).asc()
                )

        async with self.db_session() as session:
            count_scalar = await session.scalars(count_query)
            count = count_scalar.first()
            if not isinstance(count, int):
                raise RepositoryException("Unknown repository error")

            total_pages = max(ceil(count / page_size), 1)
            current_page = min(page_number, total_pages)
            offset = (current_page - 1) * page_size

            filtered_query = filtered_query.offset(offset).limit(page_size)
            filtered_scalars = await session.scalars(filtered_query)

            return self.SearchResult(
                total_items_count=count,
                page_count=total_pages,
                page_number=current_page,
                items=list(filtered_scalars.all()),
            )
