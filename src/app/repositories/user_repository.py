from typing import Any

import sqlalchemy
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.schemas import RegisterUserAppSchema
from src.helpers.exceptions.repository_exceptions import (
    RepositoryIntegrityException,
    RepositoryNotFoundException,
)
from src.models import Users


class UserRepository:
    def __init__(self, db_session: async_sessionmaker[AsyncSession]) -> None:
        self.db_session = db_session

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

    async def get_user_by_id(self, user_id: str) -> Users:
        """
        Obtaining a user by id
        :param user_id: user's id
        :return:
        User database object
        :raises RepositoryNotFoundException
        """
        async with self.db_session() as session:
            stmnt = select(Users).where(Users.id == user_id)
            scalar_res = await session.scalars(stmnt)
            user = scalar_res.first()

            if user is None:
                raise RepositoryNotFoundException("User not found")

        return user

    async def create_user(self, user_schema: RegisterUserAppSchema) -> Users:
        """
        Creating a new user
        :param user_schema: user's request data
        :return:
        Created user object
        :raises RepositoryIntegrityException
        """
        try:
            async with self.db_session() as session:
                stmnt = insert(Users).values(user_schema.model_dump()).returning(Users)
                scalar_res = await session.scalars(stmnt)
                user = scalar_res.first()
                await session.commit()

        except sqlalchemy.exc.IntegrityError as exc:
            raise RepositoryIntegrityException() from exc

        return user  # type: ignore

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

    async def update_user(
        self,
        user_id: str,
        user_update_data: dict[str, Any],
    ) -> Users:
        try:
            async with self.db_session() as session:
                stmnt = (
                    update(Users)
                    .where(Users.id == user_id)
                    .values(**user_update_data)
                    .returning(Users)
                )
                users = await session.scalars(stmnt)
                await session.commit()
        except sqlalchemy.exc.IntegrityError as exc:
            raise RepositoryIntegrityException() from exc

        return users.first()  # type: ignore

    async def delete_user(self, user_id: str):
        try:
            async with self.db_session() as session:
                stmnt = delete(Users).where(Users.id == user_id).returning(Users.id)
                deleted_user_id = await session.scalars(stmnt)
                await session.commit()
        except sqlalchemy.exc.IntegrityError as exc:
            raise RepositoryIntegrityException() from exc

        return deleted_user_id.first()
