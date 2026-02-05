from typing import Any

import sqlalchemy
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.repositories.entity_db_repository import EntityDbRepository
from src.helpers.exceptions.repository_exceptions import (
    RepositoryIntegrityException,
    RepositoryNotFoundException,
)
from src.models import Users
from src.models.mixins.id_mixin import IDType


class UserRepository(EntityDbRepository[Users]):
    model = Users

    def __init__(self, db_session: async_sessionmaker[AsyncSession]) -> None:
        super().__init__(db_session)
        self.db_session = db_session

    async def get_users(self, user_ids: list[IDType]) -> list[Users]:
        async with self.db_session() as session:
            stmt = select(Users).where(Users.id.in_(user_ids))
            scalar_res = await session.scalars(stmt)
            return list(scalar_res.all())

    async def get_user_by_email(self, email: str) -> Users:
        """
        Obtaining a user by email
        :param email: user's email address
        :return:
        User database object
        :raises RepositoryNotFoundException
        """
        async with self.db_session() as session:
            stmnt = select(Users).where(Users.email == email)
            scalar_res = await session.scalars(stmnt)
            user = scalar_res.first()

            if user is None:
                raise RepositoryNotFoundException("User not found")

        return user

    async def update_user_by_email(
        self,
        user_email: str,
        user_update_data: dict[str, Any],
    ):
        """
        Updates a user fields by email
        :param user_email: email of the user
        :param user_update_data: data to update
        :raises RepositoryIntegrityException
        """
        try:
            async with self.db_session() as session:
                stmnt = (
                    update(Users)
                    .where(Users.email == user_email)
                    .values(**user_update_data)
                )
                await session.execute(stmnt)
                await session.commit()
        except sqlalchemy.exc.IntegrityError as exc:
            raise RepositoryIntegrityException() from exc
